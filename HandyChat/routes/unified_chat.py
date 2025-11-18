#========================================================#
#  Unified chat endpoint for handling student questions
#  about PE classes and the university handbook.
#  Routes questions based on AI intent analysis + fallbacks.
#========================================================#

from flask import Blueprint, request, jsonify, Response
from sqlalchemy import text
import logging
import os
import sys
import json


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from models import (
    SportClass,
    ClassSchedule,
    Location,
    Teacher,
)

from services.ai_services import ai_service
from services.json_handbook_service import json_handbook_service
from services.handbook_search_service import optimized_handbook_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

unified_chat_bp = Blueprint('unified_chat', __name__)


@unified_chat_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    MAIN UNIFIED CHAT ENDPOINT
    Handles both PE class and handbook questions intelligently.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "status": "error"
            }), 400

        data = request.get_json()
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

        # TODO: Step 1: AI intent analysis (with safe fallback) ----
        ai_analysis = ai_service.analyze_student_query(user_question)
        if not isinstance(ai_analysis, dict):
            logger.warning("AI analysis returned non-dict or None. Falling back to 'unknown' intent.")
            ai_analysis = {
                "intent": "unknown",
                "sport": "",
                "time_reference": "",
                "handbook_topic": "",
                "urgency": "low",
                "language": "english",
                "confidence": 0.0,
            }

        logger.info(f"AI Analysis: {ai_analysis}")

        intent = ai_analysis.get("intent", "unknown")
        confidence = ai_analysis.get("confidence", 0.0)
        detected_sport = ai_analysis.get("sport") or ""

        # TODO: Step 2: Low-confidence → clarification ----
        if confidence < 0.4:
            return get_clarification_response(user_question)

        # TODO: Step 3: Route based on intent ----
        if intent == "pe_class" or detected_sport:
            return handle_pe_query(user_question, detected_sport, ai_analysis)
        elif intent == "handbook":
            return handle_handbook_query(user_question, ai_analysis)
        elif intent == "combined":
            return handle_combined_query(user_question, ai_analysis)
        else:
            # Unknown intent → try PE, then handbook, then AI fallback/clarification
            return handle_unknown_intent(user_question, ai_analysis)

    except Exception as e:
        logger.error(f"❌ Error in unified chat: {str(e)}")
        return jsonify({
            "error": "Sorry, I encountered an error processing your question. Please try again.",
            "status": "error",
            "details": str(e)
        }), 500


def handle_pe_query(question, detected_sport, ai_analysis):
    """Handle PE class queries."""
    try:
        logger.info(f"🏀 Handling PE query for sport: {detected_sport}")

        # If no sport detected, ask the user to clarify
        if not detected_sport:
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

        # Look up PE class in DB
        sport_class = SportClass.query.filter(
            SportClass.name.ilike(f'%{detected_sport}%')
        ).first()

        if sport_class:
            schedule = ClassSchedule.query.filter_by(
                class_id=sport_class.id,
                is_active=True
            ).first()

            location = Location.query.get(sport_class.location_id)
            teacher = Teacher.query.get(sport_class.teacher_id)

            # Build structured response
            response_data = build_pe_response_data(detected_sport, sport_class, location, teacher, schedule)

            # enhance with AI
            if ai_service.ai_enabled:
                try:
                    enhanced_response = ai_service.enhance_pe_response(question, response_data)
                    if enhanced_response:
                        response_data["response"] = enhanced_response
                        response_data["ai_enhanced"] = True
                    else:
                        response_data["ai_enhanced"] = False
                except Exception as e:
                    logger.warning(f"AI PE enhancement failed: {e}")
                    response_data["ai_enhanced"] = False
            else:
                response_data["ai_enhanced"] = False

            response_data["original_analysis"] = ai_analysis
            logger.info(f"Successfully found class for: {detected_sport}")
            return jsonify(response_data)

        # Sport detected but no matching class in DB
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
    """
    Handbook query handler using OPTIMIZED search service
    """
    try:
        logger.info(f"OPTIMIZED handbook query: '{question}'")

        # Use OPTIMIZED search service
        search_result = optimized_handbook_service.search_handbook(question)

        if search_result.get("found"):
            results = search_result["results"]
            confidence = search_result.get("confidence", "unknown")
            best_match_score = search_result.get("best_match_score", 0)
            total_matches = search_result.get("total_matches", 0)
            
            logger.info(f"🎯 OPTIMIZED MATCH: confidence={confidence}, score={best_match_score}, matches={total_matches}")

            # FIXED: Accept all confidence levels except "none"
            if confidence != "none":
                best_match = results[0]
                answer = best_match.get("answer_en", "")
                
                return jsonify({
                    "response": answer,
                    "answer": answer,
                    "source": "optimized_handbook", 
                    "status": "success",
                    "type": "handbook",
                    "ai_enhanced": False,
                    "search_metadata": {
                        "confidence": confidence,
                        "relevance_score": best_match_score,
                        "total_matches": total_matches,
                        "matched_question": best_match.get("question_en"),
                        "category": best_match.get("category"),
                        "match_type": best_match.get("match_type", "unknown")
                    },
                    "original_analysis": ai_analysis
                })
            else:
                logger.warning(f"No confidence matches found: {confidence}")

        logger.info(f"No optimized matches found for: '{question}'")
        
        # Get similar questions for suggestions
        all_questions = optimized_handbook_service.get_all_questions()
        similar_questions = _find_similar_questions(question, [q["question_en"] for q in all_questions])
        
        if similar_questions:
            response = f"I couldn't find an exact match for '{question}'. Did you mean:\n\n"
            for i, similar_q in enumerate(similar_questions[:3], 1):
                response += f"{i}. {similar_q}\n"
            response += "\nTry asking one of these questions for specific information."
        else:
            response = f"I couldn't find specific information about '{question}' in the handbook. Please try asking more specific questions or contact the International Student Office."

        return jsonify({
            "response": response,
            "source": "suggestions",
            "status": "suggestions",
            "type": "handbook"
        })

    except Exception as e:
        logger.error(f"❌ Error in optimized handbook query: {e}")
        return jsonify({
            "response": "Handbook service error. Please try again.",
            "status": "error",
            "type": "handbook"
        })
def _find_similar_questions(user_question, all_questions):
    """Find similar questions for suggestions"""
    user_q_lower = user_question.lower()
    similar = []
    
    for question in all_questions:
        q_lower = question.lower()
        
        # Check for significant word overlap
        user_words = set(user_q_lower.split())
        q_words = set(q_lower.split())
        
        common_words = user_words.intersection(q_words)
        if len(common_words) >= 2: 
            similar.append(question)
    
    return similar[:5]
def _get_category_fallback_response(question, predicted_category):
    """Get category-specific fallback response"""
    if predicted_category:
        category_responses = {
            "Visa Application / 签证申请": f"I couldn't find specific visa information about '{question}' in our current database. Please contact the International Student Office for visa assistance:\n\n• Email: iso@zjnu.cn\n• Phone: +86 (579) 82283155\n• Location: Exit-Entry Administration Bureau, 1055 Bayi North Street, Jinhua",
            "Academic Affairs / 学业指南": f"For detailed academic information about '{question}', please consult your college advisor or the Academic Affairs Office. You can also check the official ZJNU academic calendar and course registration system.",
            "Regulations on Tuition and Accommodation / 学费与住宿规定": f"Tuition and accommodation questions are best handled by the Finance Office and Student Housing Office. Please visit them for specific information about '{question}' or check the fee schedule in the handbook.",
            "Guide to Campus Life / 校园生活指南": f"General campus life information is available from the Student Affairs Office. For '{question}', you might want to check the campus service centers or contact the International Student Office.",
            "Scholarships for International Students / 国际学生奖学金指南": f"For scholarship information regarding '{question}', please contact the International Student Office during application periods (March-May for fall, September-November for spring).",
            "Student Status & Degree Regulations / 学籍与学位规定": f"Student status and degree requirements questions should be directed to your college's academic affairs office. For '{question}', they can provide the most accurate and up-to-date information.",
            "Disciplinary & Attendance Rules / 纪律与考勤规定": f"Disciplinary and attendance policies are strictly enforced. For specific questions about '{question}', please consult the Student Affairs Office or your department head.",
            "Useful Laws and Forms / 常用法律与表格": f"Legal documents and forms are available from the International Student Office. For '{question}', please visit their office or check the official ZJNU website for downloadable forms."
        }
        
        return category_responses.get(predicted_category, 
            f"I couldn't find specific information about '{question}' in our handbook systems. Please contact the International Student Office at iso@zjnu.cn for assistance.")
    
    return f"I couldn't find specific information about '{question}' in our handbook systems. For detailed information, please contact the International Student Office:\n\n• Email: iso@zjnu.cn\n• Phone: +86 (579) 82283155\n• Location: Room 100, North Building, Administration Center"


def handle_combined_query(question, ai_analysis):
    """Handle queries needing both PE + handbook info."""
    try:
        logger.info(f"Handling combined query: {question}")
        question_lower = question.lower()

        # Example: PE credits towards graduation
        if any(word in question_lower for word in ['credit', 'credits']) and \
           any(word in question_lower for word in ['pe', 'sport', 'class']):
            return jsonify({
                "response": (
                    "Yes, PE classes count for academic credits towards graduation at ZJNU. "
                    "Most PE classes are 1–2 credits each. The specific credit requirements "
                    "depend on your program and are outlined in the graduation requirements."
                ),
                "status": "success",
                "type": "combined",
                "suggestions": [
                    "Show me available PE classes",
                    "What are the graduation requirements?",
                    "How many total credits do I need?"
                ],
                "original_analysis": ai_analysis
            })

        # AI-based combined answer
        if ai_service.ai_enabled:
            try:
                ai_response = ai_service.handle_complex_queries(question)
                if ai_response:
                    return jsonify({
                        "response": ai_response,
                        "status": "success",
                        "type": "combined_ai",
                        "ai_generated": True,
                        "original_analysis": ai_analysis
                    })
            except Exception as e:
                logger.warning(f"AI combined-query handler failed: {e}")

        # Registration deadlines for sports
        if any(word in question_lower for word in ['deadline', 'register', 'enroll']) and \
           any(word in question_lower for word in ['basketball', 'swimming', 'tennis', 'sport']):
            return jsonify({
                "response": (
                    "PE class registration follows the academic calendar deadlines. You can register "
                    "for specific sports classes during the add/drop period at the beginning of each "
                    "semester. Check the academic calendar for exact dates."
                ),
                "status": "success",
                "type": "combined",
                "suggestions": [
                    "When is the add/drop period?",
                    "Show me basketball class information",
                    "What is the academic calendar for this semester?"
                ],
                "original_analysis": ai_analysis
            })

        # Generic combined fallback
        return jsonify({
            "response": (
                "I can help you with both PE class information and university policies. "
                "Could you specify what you'd like to know more about?"
            ),
            "status": "success",
            "type": "combined",
            "suggestions": [
                "Tell me about basketball class location",
                "What are the graduation requirements?",
                "When is the course registration deadline?",
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
    """Handle questions where the AI couldn't clearly classify intent."""
    try:
        logger.info(f"❓ Handling unknown intent: {question}")

        # ---- Try PE fallback first ----
        pe_response = try_pe_fallback(question)

        # If handle_pe_query returned a Flask Response, just return it
        if isinstance(pe_response, Response):
            return pe_response

        # If a dict was returned, check its status
        if isinstance(pe_response, dict) and pe_response.get('status') == 'success':
            return jsonify(pe_response)

        # ---- Try handbook fallback next ----
        handbook_response = try_handbook_fallback(question)

        if isinstance(handbook_response, Response):
            return handbook_response

        if isinstance(handbook_response, dict) and handbook_response.get('status') == 'success':
            return jsonify(handbook_response)

        # ---- AI final fallback ----
        if ai_service.ai_enabled:
            try:
                ai_fallback = ai_service.handle_complex_queries(question)
                if ai_fallback:
                    return jsonify({
                        "response": ai_fallback,
                        "status": "success",
                        "type": "ai_fallback",
                        "ai_generated": True
                    })
            except Exception as e:
                logger.warning(f"AI fallback failed in unknown intent handler: {e}")

        # ask for clarification ----
        return get_clarification_response(question)

    except Exception as e:
        logger.error(f"Error handling unknown intent: {e}")
        return get_clarification_response(question)


def try_pe_fallback(question):
    """Try to detect sport keywords and treat as PE query."""
    try:
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
                # This returns a Flask Response from handle_pe_query
                return handle_pe_query(
                    question,
                    sport,
                    {"intent": "pe_class", "sport": sport, "confidence": 0.6}
                )
        return None

    except Exception as e:
        logger.error(f"Error in PE fallback: {e}")
        return None


def try_handbook_fallback(question):
    """Try to handle question as handbook-related with OPTIMIZED service first"""
    try:
        # Try optimized service first
        optimized_response = optimized_handbook_service.search_handbook(question)
        if optimized_response and optimized_response.get("found"):
            best_match = optimized_response["results"][0]
            return {
                "response": best_match.get("answer_en", ""),
                "answer": best_match.get("answer_en", ""),
                "source": "optimized_handbook", 
                "status": "success",
                "type": "handbook",
                "total_matches": optimized_response.get("total_matches", 0)
            }

        # Fallback to JSON service only if optimized service finds nothing
        json_response = json_handbook_service.search_handbook(question)
        if json_response and json_response.get("found"):
            best_match = json_response["results"][0]
            return {
                "response": best_match.get("answer_en", ""),
                "answer": best_match.get("answer_en", ""),
                "source": "json_handbook",  
                "status": "success",
                "type": "handbook",
                "results_found": json_response.get("total_matches", 0)
            }

        return None

    except Exception as e:
        logger.error(f"Error in handbook fallback: {e}")
        return None

def build_pe_response_data(sport, sport_class, location, teacher, schedule):
    """Build structured PE class response payload."""
    response_message = f"Your {sport} class is at {location.name}" if location else f"Your {sport} class location is not fully configured yet"

    if location and location.building:
        response_message += f" ({location.building})"

    if schedule:
        response_message += f". It's on {schedule.day_of_week}"
        if schedule.start_time and schedule.end_time:
            response_message += f" from {schedule.start_time} to {schedule.end_time}"

    if teacher:
        response_message += f" with {teacher.name}"

    response_message += "."

    response_data = {
        "response": response_message,
        "sport": sport,
        "status": "success",
        "type": "pe",
        "question_asked": sport,
        "location_details": {
            "name": getattr(location, "name", None),
            "building": getattr(location, "building", None),
            "floor": getattr(location, "floor", None),
            "room_number": getattr(location, "room_number", None),
            "description": getattr(location, "description", None),
        },
        "teacher": {
            "name": teacher.name if teacher else None,
        }
    }

    if schedule:
        response_data["schedule"] = {
            "day": schedule.day_of_week,
            "time": (
                f"{schedule.start_time} - {schedule.end_time}"
                if schedule.start_time and schedule.end_time
                else None
            ),
            "semester": schedule.semester
        }

    response_data["images"] = []
    if location and hasattr(location, "image_urls") and location.image_urls:
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

    map_links = {}
    if location and getattr(location, "amap_link", None) and location.amap_link != "https://uri.amap.com/xxx":
        map_links["amap_link"] = location.amap_link
    if location and getattr(location, "baidu_map_link", None) and location.baidu_map_link != "https://api.map.baidu.com/xxx":
        map_links["baidu_map_link"] = location.baidu_map_link

    if map_links:
        response_data["maps"] = map_links

    return response_data

def get_clarification_response(question):
    """Ask user to clarify whether they mean PE or handbook, with suggestions."""
    available_sports = get_available_sports_list()
    return jsonify({
        "response": (
            "I'm not quite sure what you're asking about. Could you clarify if you're asking "
            "about PE classes or university policies?"
        ),
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
    """Return list of available sports."""
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
            "sports": [
                "basketball", "swimming", "tennis", "badminton",
                "soccer", "volleyball", "table tennis", "tai chi"
            ],
            "status": "success",
            "note": "Using fallback sports list"
        })


@unified_chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with DB, AI, JSON status."""
    sports_count = 0

    try:
        db.session.execute(text('SELECT 1'))
        db_status = "connected"

        sports_count = SportClass.query.count()
        db_info = f"connected ({sports_count} sports classes)"

        ai_status = "available" if ai_service.ai_enabled else "disabled"

        try:
            json_status = json_handbook_service.get_status()
            json_handbook_status = "available" if json_status["loaded"] else "unavailable"
            json_categories = json_status["categories_count"]
            json_questions = json_status["total_questions"]
        except Exception as e:
            json_handbook_status = f"error: {e}"
            json_categories = 0
            json_questions = 0

    except Exception as e:
        db_status = f"error: {str(e)}"
        db_info = "disconnected"
        ai_status = "unknown"
        json_handbook_status = "unknown"

    return jsonify({
        "status": "healthy",
        "service": "HandyChat Assistant",
        "database": db_info,
        "ai_service": ai_status,
        "handbook_services": {
            "json_handbook": json_handbook_status,
            "pdf_handbook": "disabled",
            "json_categories": json_categories,
            "json_questions": json_questions
        },
        "capabilities": {
            "pe_classes": True,
            "handbook": True,
            "ai_understanding": ai_service.ai_enabled,
            "json_handbook": json_handbook_status == "available",
            "pdf_handbook": False,
            "bilingual_support": True
        },
        "stats": {
            "sports_classes": sports_count,
            "json_handbook_questions": json_questions
        }
    })


@unified_chat_bp.route('/handbook/json-status', methods=['GET'])
def json_handbook_status():
    """Get JSON handbook service status"""
    try:
        status = json_handbook_service.get_status()
        return jsonify({
            "status": "success",
            "json_handbook": status
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@unified_chat_bp.route('/analyze', methods=['POST'])
def analyze_question():
    """Debug endpoint to see AI + handbook classification for a question."""
    try:
        data = request.get_json()
        question = (data or {}).get('question', '').strip()

        if not question:
            return jsonify({"error": "Question is required"}), 400

        ai_analysis = ai_service.analyze_student_query(question)
        handbook_category = ai_service.classify_handbook_topic(question)

        return jsonify({
            "question": question,
            "ai_analysis": ai_analysis,
            "handbook_category": handbook_category,
            "ai_enabled": ai_service.ai_enabled,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@unified_chat_bp.route('/handbook/optimized-status', methods=['GET'])
def optimized_handbook_status():
    """Get optimized handbook service status"""
    try:
        status = optimized_handbook_service.get_status()
        sample_questions = optimized_handbook_service.get_all_questions()[:5]
        
        return jsonify({
            "status": "success",
            "optimized_handbook": status,
            "sample_questions": sample_questions
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@unified_chat_bp.route('/handbook/test-search', methods=['POST'])
def test_optimized_search():
    """Test optimized search directly"""
    try:
        data = request.get_json()
        question = (data or {}).get('question', '').strip()

        if not question:
            return jsonify({"error": "Question is required"}), 400

        result = optimized_handbook_service.search_handbook(question)
        
        return jsonify({
            "question": question,
            "search_result": result,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@unified_chat_bp.route('/handbook/debug-search', methods=['POST'])
def debug_handbook_search():
    """Debug endpoint to see search scoring"""
    try:
        data = request.get_json()
        question = (data or {}).get('question', '').strip()

        if not question:
            return jsonify({"error": "Question is required"}), 400

        debug_results = optimized_handbook_service.debug_search(question)
        
        return jsonify({
            "question": question,
            "debug_results": debug_results,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@unified_chat_bp.route('/handbook/debug-confidence', methods=['POST'])
def debug_confidence():
    """Debug endpoint to see confidence levels"""
    try:
        data = request.get_json()
        question = (data or {}).get('question', '').strip()

        if not question:
            return jsonify({"error": "Question is required"}), 400

        optimized_result = optimized_handbook_service.search_handbook(question)
        
        return jsonify({
            "question": question,
            "optimized_result": optimized_result,
            "confidence_used": optimized_result.get("confidence", "unknown"),
            "should_use_optimized": optimized_result.get("confidence", "none") != "none"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_available_sports_list():
    """Get list of available sports from DB, with safe fallback."""
    try:
        sports = SportClass.query.with_entities(SportClass.name).distinct().all()
        if sports:
            return [sport[0] for sport in sports]
        # fallback if table is empty
        return [
            "basketball", "swimming", "tennis", "badminton",
            "soccer", "volleyball", "table tennis", "tai chi"
        ]
    except Exception as e:
        logger.error(f"Error fetching sports from database: {e}")
        return [
            "basketball", "swimming", "tennis", "badminton",
            "soccer", "volleyball", "table tennis", "tai chi"
        ]