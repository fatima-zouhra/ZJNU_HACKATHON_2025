
#========================================================#
#  This file defines the unified chat endpoint for handling student questions about PE classes and the university handbook.
#  It intelligently routes questions to the appropriate service based on AI analysis of the question intent.
#========================================================#

from flask import Blueprint, request, jsonify
from sqlalchemy import text
import logging
import os
import sys
import json

# Adding parent directory to path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from models import SportClass, ClassSchedule, Location, Teacher, HandbookCategory, HandbookSection, HandbookFAQ
from services.handbook_db_service import handbook_db_service
from services.ai_services import ai_service

# Set up logging to track the app’s activity and important messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


unified_chat_bp = Blueprint('unified_chat', __name__)

@unified_chat_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    MAIN UNIFIED CHAT ENDPOINT - Handles both PE classes and handbook questions intelligently
    """
    try:
        # Ensure we're getting JSON
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "status": "error"
            }), 400

        data = request.get_json()
        
        # Validate request
        if not data or 'question' not in data:
            return jsonify({
                "error": "Question is required",
                "status": "error"
            }), 400
            
        user_question = data.get('question', '').strip()
        
        if not user_question:
            return jsonify({
                "error": "Question cannot be empty",
                "status": "error"
            }), 400
        
        logger.info(f"Unified chat received: {user_question}")

        # TODO: Step 1: Use AI to understand the question intent
        ai_analysis = ai_service.analyze_student_query(user_question)
        logger.info(f"AI Analysis: {ai_analysis}")

        # Initialize handbook data
        handbook_db_service.initialize_handbook_data()

        # TODO: Step 2: Route based on AI analysis
        intent = ai_analysis["intent"]
        confidence = ai_analysis["confidence"]
        detected_sport = ai_analysis["sport"]

        # Low confidence - ask for clarification (this ensures we don't guess wrong)
        if confidence < 0.4:
            return get_clarification_response(user_question)

        # TODO: Step 3: Handle different intents
        if intent == "pe_class" or detected_sport:
            return handle_pe_query(user_question, detected_sport, ai_analysis)
        elif intent == "handbook":
            return handle_handbook_query(user_question, ai_analysis)
        elif intent == "combined":
            return handle_combined_query(user_question, ai_analysis)
        else:
            # Try both services and see what works
            return handle_unknown_intent(user_question, ai_analysis)
        
    except Exception as e:
        logger.error(f"❌ Error in unified chat: {str(e)}")
        return jsonify({
            "error": "Sorry, I encountered an error processing your question. Please try again.",
            "status": "error",
            "details": str(e)
        }), 500

def handle_pe_query(question, detected_sport, ai_analysis):
    """Handle PE class queries"""
    try:
        logger.info(f"🏀 Handling PE query for sport: {detected_sport}")
        
        if not detected_sport:
            # No sport detected - show available sports
            available_sports = get_available_sports_list()
            return jsonify({
                "response": "I'm not sure which PE class you're asking about. Please mention the sport name.",
                "status": "clarify_needed",
                "type": "pe",
                "available_sports": available_sports,
                "examples": [
                    "Where is basketball class?",
                    "游泳课在哪里？",
                    "When is tennis practice?",
                    "羽毛球课的时间"
                ]
            })

        # Get class info from database
        sport_class = SportClass.query.filter(
            SportClass.name.ilike(f'%{detected_sport}%')
        ).first()
        
        if sport_class:
            # Get related information from database
            schedule = ClassSchedule.query.filter_by(
                class_id=sport_class.id, 
                is_active=True
            ).first()
            
            location = Location.query.get(sport_class.location_id)
            teacher = Teacher.query.get(sport_class.teacher_id)
            
            # Build structured response data
            response_data = build_pe_response_data(detected_sport, sport_class, location, teacher, schedule)
            
            # Enhance response with AI
            if ai_service.ai_enabled:
                enhanced_response = ai_service.enhance_pe_response(question, response_data)
                response_data["response"] = enhanced_response
                response_data["ai_enhanced"] = True
            else:
                response_data["ai_enhanced"] = False

            response_data["original_analysis"] = ai_analysis
            logger.info(f"Successfully found class for: {detected_sport}")
            return jsonify(response_data)
        else:
            # Sport detected but no class found
            available_sports = get_available_sports_list()
            return jsonify({
                "response": f"Sorry, no {detected_sport} class was found in our current schedule.",
                "status": "not_found",
                "type": "pe",
                "sport_asked": detected_sport,
                "available_sports": available_sports
            })
            
    except Exception as e:
        logger.error(f"Error handling PE query: {e}")
        return jsonify({
            "response": f"I'm having trouble finding {detected_sport} class information right now. Please try again later.",
            "status": "error",
            "type": "pe"
        })

def handle_handbook_query(question, ai_analysis):
    """Handle handbook queries with PDF service as primary"""
    try:
        logger.info(f"📚 Handling handbook query: {question}")
        
        # First check if this is actually a combined query
        question_lower = question.lower()
        pe_indicators = ['pe', 'sport', 'basketball', 'swimming', 'tennis', 'class']
        handbook_indicators = ['credit', 'graduation', 'requirement', 'deadline']
        
        has_pe = any(word in question_lower for word in pe_indicators)
        has_handbook = any(word in question_lower for word in handbook_indicators)
        
        if has_pe and has_handbook:
            logger.info("🔄 Re-routing to combined query handler")
            return handle_combined_query(question, ai_analysis)
        
        # TODO: Step 1: Try PDF service first
        pdf_response = _try_pdf_service(question)
        if pdf_response and _is_meaningful_pdf_response(pdf_response):
            logger.info("Using PDF handbook service")
            
            # Enhance with AI if available
            if ai_service.ai_enabled:
                try:
                    enhanced_response = ai_service.enhance_handbook_response(question, {"faqs": [], "sections": []})
                    if enhanced_response and len(enhanced_response) > 100:
                        pdf_response = enhanced_response
                except Exception as e:
                    logger.warning(f"AI enhancement failed: {e}")
            
            return jsonify({
                "response": pdf_response,
                "answer": pdf_response,
                "source": "pdf_handbook",
                "status": "success",
                "type": "handbook",
                "ai_enhanced": ai_service.ai_enabled,
                "original_analysis": ai_analysis
            })
        
        # TODO: Step 2: Try simple handbook service as fallback
        simple_answer = _try_simple_handbook(question)
        if simple_answer:
            logger.info("✅ Using simple handbook service")
            return jsonify({
                "response": simple_answer,
                "answer": simple_answer,
                "source": "simple_handbook",
                "status": "success",
                "type": "handbook",
                "original_analysis": ai_analysis
            })
        
        # TODO: Step 3: Final AI fallback
        if ai_service.ai_enabled:
            try:
                ai_response = ai_service.enhance_handbook_response(question, {"faqs": [], "sections": []})
                if ai_response and len(ai_response) > 100:
                    logger.info("✅ Using AI-generated response")
                    return jsonify({
                        "response": ai_response,
                        "answer": ai_response,
                        "source": "ai_generated",
                        "status": "success",
                        "type": "handbook",
                        "ai_enhanced": True,
                        "original_analysis": ai_analysis
                    })
            except Exception as e:
                logger.warning(f"AI fallback failed: {e}")
        
        # TODO: Step 4: Ultimate fallback
        return jsonify({
            "response": _get_fallback_handbook_response(question),
            "source": "fallback",
            "status": "partial",
            "type": "handbook",
            "original_analysis": ai_analysis
        })
        
    except Exception as e:
        logger.error(f"Error handling handbook query: {e}")
        return jsonify({
            "response": "I'm having trouble accessing handbook information. Please contact the International Student Office for assistance.",
            "status": "error",
            "type": "handbook"
        })

def _try_pdf_service(question):
    """Try to get answer from PDF handbook service with better error handling"""
    try:
        from services.handbook_pdf_service import ask_handbook_clean
        
        # Check if PDF service is properly configured
        pdf_status = get_handbook_pdf_status()
        if pdf_status.get('status') != 'available':
            logger.warning(f"PDF service not available: {pdf_status}")
            return None
            
        pdf_response = ask_handbook_clean(question)
        logger.info(f"📖 PDF service response length: {len(pdf_response) if pdf_response else 0}")
        return pdf_response
        
    except ImportError as e:
        logger.error(f"PDF service import error: {e}")
        return None
    except Exception as e:
        logger.error(f"PDF service error: {e}")
        return None

def get_handbook_pdf_status():
    """Get the status of the PDF handbook service"""
    try:
        from services.handbook_pdf_service import get_handbook_status
        return get_handbook_status()
    except ImportError:
        return {"status": "not_configured", "error": "PDF service not found"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def _try_simple_handbook(question):
    """Try simple handbook service"""
    try:
        from services.simple_handbook_service import simple_handbook
        return simple_handbook.search(question)
    except ImportError:
        return None
    except Exception as e:
        logger.warning(f"Simple handbook error: {e}")
        return None

def _is_meaningful_pdf_response(pdf_response):
    """Check if PDF response is meaningful"""
    if not pdf_response or len(pdf_response.strip()) < 50:
        return False
    
    error_indicators = [
        "couldn't find", "not found", "unavailable", "trouble", 
        "error", "try again", "contact office", "difficulties"
    ]
    
    response_lower = pdf_response.lower()
    return not any(indicator in response_lower for indicator in error_indicators)

def _get_fallback_handbook_response(question):
    """Get fallback response"""
    return (
        f"I couldn't find specific information about '{question}' in our handbook systems. "
        "For detailed information, please contact the International Student Office:\n\n"
        "• Email: iso@zjnu.cn\n"
        "• Phone: +86 (579) 82283155\n"
        "• Location: Room 100, North Building, Administration Center"
    )

def handle_combined_query(question, ai_analysis):
    """Handle queries that need both PE and handbook information"""
    try:
        logger.info(f"Handling combined query: {question}")
        
        question_lower = question.lower()
        
        # PE credit requirements for graduation
        if any(word in question_lower for word in ['credit', 'credits']) and any(word in question_lower for word in ['pe', 'sport', 'class']):
            return jsonify({
                "response": "Yes, PE classes count for academic credits towards graduation at ZJNU. Most PE classes are 1-2 credits each. The specific credit requirements depend on your program and are outlined in the graduation requirements. As a computer science student, you'll need 4 credits.",
                "status": "success",
                "type": "combined",
                "suggestions": [
                    "Show me available PE classes",
                    "What are the graduation requirements?",
                    "How many total credits do I need?"
                ],
                "original_analysis": ai_analysis
            })
        
        # Use AI to handle other complex combined queries
        if ai_service.ai_enabled:
            ai_response = ai_service.handle_complex_queries(question)
            if ai_response:
                return jsonify({
                    "response": ai_response,
                    "status": "success",
                    "type": "combined_ai",
                    "ai_generated": True,
                    "original_analysis": ai_analysis
                })
        
        # Registration deadlines for specific sports
        if any(word in question_lower for word in ['deadline', 'register', 'enroll']) and any(word in question_lower for word in ['basketball', 'swimming', 'tennis', 'sport']):
            return jsonify({
                "response": "PE class registration follows the academic calendar deadlines. You can register for specific sports classes during the add/drop period at the beginning of each semester. Check the academic calendar for exact dates.",
                "status": "success",
                "type": "combined",
                "suggestions": [
                    "When is the add/drop period?",
                    "Show me basketball class information",
                    "What is the academic calendar for this semester?"
                ],
                "original_analysis": ai_analysis
            })
        
        # Default combined response
        return jsonify({
            "response": "I can help you with both PE class information and university policies. Could you specify what you'd like to know more about?",
            "status": "success",
            "type": "combined",
            "suggestions": [
                "Tell me about basketball class location",
                "What are the graduation requirements?",
                "When is course registration deadline?",
                "How do I apply for a student visa?"
            ],
            "original_analysis": ai_analysis
        })
        
    except Exception as e:
        logger.error(f"Error handling combined query: {e}")
        return jsonify({
            "response": "I'm having trouble processing your complex question. Please try asking about PE classes or handbook information separately.",
            "status": "error",
            "type": "combined"
        })

def handle_unknown_intent(question, ai_analysis):
    """Handle questions where intent isn't clear"""
    try:
        logger.info(f"❓ Handling unknown intent: {question}")
        
        # Try PE first
        pe_response = try_pe_fallback(question)
        if pe_response and pe_response.get('status') == 'success':
            return jsonify(pe_response)
        
        # Try handbook second
        handbook_response = try_handbook_fallback(question)
        if handbook_response and handbook_response.get('status') == 'success':
            return jsonify(handbook_response)
        
        # Final fallback with AI
        if ai_service.ai_enabled:
            ai_fallback = ai_service.handle_complex_queries(question)
            if ai_fallback:
                return jsonify({
                    "response": ai_fallback,
                    "status": "success",
                    "type": "ai_fallback",
                    "ai_generated": True
                })
        
        # Ultimate fallback
        return get_clarification_response(question)
        
    except Exception as e:
        logger.error(f"Error handling unknown intent: {e}")
        return get_clarification_response(question)

def try_pe_fallback(question):
    """Try to extract sport and handle as PE query"""
    try:
        # Simple sport detection for fallback
        sport_keywords = {
            'basketball': 'basketball', '篮球': 'basketball',
            'swimming': 'swimming', '游泳': 'swimming',
            'tennis': 'tennis', '网球': 'tennis',
            'badminton': 'badminton', '羽毛球': 'badminton',
            'soccer': 'soccer', '足球': 'soccer',
            'volleyball': 'volleyball', '排球': 'volleyball',
            'table tennis': 'table tennis', 'ping pong': 'table tennis', '乒乓球': 'table tennis',
            'tai chi': 'tai chi', '太极': 'tai chi', '太极拳': 'tai chi'
        }
        
        question_lower = question.lower()
        for keyword, sport in sport_keywords.items():
            if keyword in question_lower:
                return handle_pe_query(question, sport, {"intent": "pe_class", "sport": sport, "confidence": 0.6})
        return None
    except Exception as e:
        logger.error(f"Error in PE fallback: {e}")
        return None

def try_handbook_fallback(question):
    """Try to handle as handbook query with PDF priority"""
    try:
        # First try PDF service
        pdf_response = _try_pdf_service(question)
        if pdf_response and _is_meaningful_pdf_response(pdf_response):
            return {
                "response": pdf_response,
                "answer": pdf_response,
                "source": "pdf_handbook",
                "status": "success",
                "type": "handbook"
            }
        
        # Then try database
        results = handbook_db_service.search_handbook(question)
        if results["faqs"] or results["sections"]:
            response_text = generate_handbook_response(question, results)
            return {
                "response": response_text,
                "answer": response_text,
                "source": "database",
                "status": "success",
                "type": "handbook",
                "results_found": len(results["faqs"]) + len(results["sections"])
            }
        
        # Finally try simple handbook
        simple_answer = _try_simple_handbook(question)
        if simple_answer:
            return {
                "response": simple_answer,
                "answer": simple_answer,
                "source": "simple_handbook",
                "status": "success",
                "type": "handbook"
            }
        
        return None
    except Exception as e:
        logger.error(f"Error in handbook fallback: {e}")
        return None

def _try_pdf_fallback(question):
    """Try to get answer from PDF handbook with new filename"""
    try:
    
        from services.handbook_pdf_service import ask_handbook_clean
        pdf_response = ask_handbook_clean(question)
        return pdf_response
    except ImportError:
        logger.warning("PDF handbook service not available (file may be renamed)")
        return None
    except Exception as e:
        logger.warning(f"PDF fallback service failed: {e}")
        return None

def build_pe_response_data(sport, sport_class, location, teacher, schedule):
    """Build comprehensive PE response data"""
    # Build basic response message
    response_message = f"Your {sport} class is at {location.name}"
    if location.building:
        response_message += f" ({location.building})"
    
    if schedule:
        response_message += f". It's on {schedule.day_of_week}"
        if schedule.start_time and schedule.end_time:
            response_message += f" from {schedule.start_time} to {schedule.end_time}"
    
    if teacher:
        response_message += f" with {teacher.name}"
    
    response_message += "."

    # Build comprehensive response
    response_data = {
        "response": response_message,
        "sport": sport,
        "status": "success",
        "type": "pe",
        "question_asked": sport,  # Simplified for this context
        "location_details": {
            "name": location.name,
            "building": location.building,
            "floor": location.floor,
            "room_number": location.room_number,
            "description": location.description
        },
        "teacher": {
            "name": teacher.name if teacher else None,
            "contact": teacher.contact_info if teacher else None,
            "email": teacher.email if teacher else None
        }
    }
    
    # Add schedule if available
    if schedule:
        response_data["schedule"] = {
            "day": schedule.day_of_week,
            "time": f"{schedule.start_time} - {schedule.end_time}" if schedule.start_time and schedule.end_time else None,
            "semester": schedule.semester
        }

    # Add images if available
    response_data["images"] = []
    if hasattr(location, "image_urls") and location.image_urls:
        try:
            if isinstance(location.image_urls, list):
                response_data["images"] = location.image_urls
            else:
                parsed = json.loads(location.image_urls)
                if isinstance(parsed, list):
                    response_data["images"] = parsed
                else:
                    response_data["images"] = [str(parsed)]
        except Exception:
            response_data["images"] = [str(location.image_urls)]

    # Add map links
    map_links = {}
    if location.amap_link and location.amap_link != "https://uri.amap.com/xxx":
        map_links["amap_link"] = location.amap_link
    if location.baidu_map_link and location.baidu_map_link != "https://api.map.baidu.com/xxx":
        map_links["baidu_map_link"] = location.baidu_map_link
    
    if map_links:
        response_data["maps"] = map_links

    return response_data

def generate_handbook_response(question, results):
    """Generate handbook response without AI"""
    # If we found direct FAQ matches
    if results["faqs"]:
        faq = results["faqs"][0]
        return f"{faq.answer}"
    
    # If we found relevant sections
    if results["sections"]:
        section = results["sections"][0]
        return f"{section.content}"
    
    # No direct matches
    category_name = handbook_db_service.classify_question(question)
    category_info = handbook_db_service.get_category_info(category_name)
    
    if category_info and category_info["sections"]:
        return f"I found information about {category_name}:\n\n{category_info['sections'][0].content}"
    
    # Final fallback
    return f"I couldn't find specific information about '{question}' in the ZJNU handbook. You might want to check the official handbook or contact the International Student Office."

def get_clarification_response(question):
    """Get clarification response for unclear questions"""
    available_sports = get_available_sports_list()
    
    return jsonify({
        "response": "I'm not quite sure what you're asking about. Could you clarify if you're asking about PE classes or university policies?",
        "status": "clarify_needed",
        "type": "clarification",
        "question_asked": question,
        "available_sports": available_sports,
        "suggestions": [
            "Where is basketball class?",
            "What are the graduation requirements?",
            "How do I apply for a student visa?",
            "When is swimming class?",
            "Tell me about tuition fees"
        ]
    })

@unified_chat_bp.route('/sports', methods=['GET'])
def get_available_sports():
    """Get list of all available sports from database"""
    try:
        sports_list = get_available_sports_list()
        
        return jsonify({
            "sports": sports_list,
            "count": len(sports_list),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error getting sports list: {str(e)}")
        return jsonify({
            "sports": ["basketball", "swimming", "tennis", "badminton", "soccer", "volleyball", "table tennis", "tai chi"],
            "status": "success",
            "note": "Using fallback sports list"
        })

@unified_chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with PDF service status"""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db_status = "connected"
        
        # Get counts
        sports_count = SportClass.query.count()
        categories_count = HandbookCategory.query.count()
        
        
        db_info = f"connected ({sports_count} sports, {categories_count} handbook categories)"
        
        # Check AI status
        ai_status = "available" if ai_service.ai_enabled else "disabled"
        
        # Check PDF service status
        pdf_status = "unknown"
        try:
            from services.handbook_pdf_service import get_handbook_status
            pdf_info = get_handbook_status()
            pdf_status = pdf_info.get('status', 'unknown')
        except ImportError:
            pdf_status = "not_available"
        except Exception as e:
            pdf_status = f"error: {e}"
    
    except Exception as e:
        db_status = f"error: {str(e)}"
        db_info = "disconnected"
        ai_status = "unknown"
        pdf_status = "unknown"
    
    return jsonify({
        "status": "healthy",
        "service": "HandyChat Assistant",
        "database": db_info,
        "ai_service": ai_status,
        "pdf_service": pdf_status,
        "capabilities": {
            "pe_classes": True,
            "handbook": True,
            "ai_understanding": ai_service.ai_enabled,
            "pdf_handbook": pdf_status == "available",
            "bilingual_support": True
        },
        "stats": {
            "sports_classes": sports_count,
            "handbook_categories": categories_count
        }
    })
@unified_chat_bp.route('/analyze', methods=['POST'])
def analyze_question():
    """Debug endpoint to see question analysis"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        ai_analysis = ai_service.analyze_student_query(question)
        handbook_category = handbook_db_service.classify_question(question)
        
        return jsonify({
            "question": question,
            "ai_analysis": ai_analysis,
            "handbook_category": handbook_category,
            "ai_enabled": ai_service.ai_enabled,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_available_sports_list():
    """Get list of available sports from database"""
    try:
        sports = SportClass.query.with_entities(SportClass.name).distinct().all()
        return [sport[0] for sport in sports] if sports else [
            "basketball", "swimming", "tennis", "badminton", "soccer", "volleyball", "table tennis", "tai chi"
        ]
    except Exception as e:
        logger.error(f"Error fetching sports from database: {e}")
        return ["basketball", "swimming", "tennis", "badminton", "soccer", "volleyball", "table tennis", "tai chi"]