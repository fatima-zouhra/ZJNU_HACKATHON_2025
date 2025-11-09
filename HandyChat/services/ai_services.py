
#========================================================#
# this script provides AI services for analyzing student queries
# It uses OpenAI's GPT-4o-mini model to understand intent and extract key information
# It also enhances responses for both PE class queries and handbook questions
#========================================================#

import openai
import os
import json
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
            self.ai_enabled = True
            logger.info("AI Service initialized with OpenAI GPT-4o-mini")
        else:
            self.ai_enabled = False
            logger.warning("OpenAI API key not found. Using fallback mode.")
    
    def analyze_student_query(self, user_message):
        """
        Use AI to understand student intent and extract key information
        """
        if not self.ai_enabled:
            return self._fallback_intent_analysis(user_message)
        
        try:
            prompt = f"""
            Analyze this international student's question about ZJNU (Zhejiang Normal University) and determine:
            1. Primary intent: PE classes, university handbook, or both
            2. If PE: extract sport name and any time references
            3. If handbook: extract main topics and urgency
            4. Confidence level (0.0-1.0)

            Context: ZJNU has PE classes (basketball, swimming, tennis, badminton, soccer, volleyball, table tennis, tai chi)
            and handbook covers: academic policies, fees, visa, graduation, accommodation, grading, rules, calendar, support

            Return ONLY valid JSON format: {{
                "intent": "pe_class|handbook|combined|unknown",
                "sport": "sport_name_or_empty",
                "time_reference": "time_value_or_empty", 
                "handbook_topic": "topic_or_empty",
                "urgency": "low|medium|high",
                "language": "english|chinese|mixed",
                "confidence": 0.85
            }}

            Student Question: "{user_message}"
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You analyze ZJNU international student questions. Be accurate with sports names and handbook topics. Always return valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content.strip()
            return self._parse_ai_response(result)
            
        except Exception as e:
            logger.error(f"AI Service Error: {e}")
            return self._fallback_intent_analysis(user_message)
    
    def enhance_handbook_response(self, question, database_results, context=""):
        """
        Use AI to enhance handbook responses for better clarity and completeness
        """
        if not self.ai_enabled:
            return self._format_fallback_response(database_results)
        
        try:
            # Prepare context from database results
            context_text = ""
            if database_results.get("faqs"):
                for faq in database_results["faqs"][:2]:
                    context_text += f"Q: {faq.question}\nA: {faq.answer}\n\n"
            
            if database_results.get("sections"):
                for section in database_results["sections"][:2]:
                    context_text += f"Title: {section.title}\nContent: {section.content}\n\n"
            
            prompt = f"""
            You are a helpful assistant at Zhejiang Normal University (ZJNU). 
            An international student asked: "{question}"
            
            Here is relevant information from our official handbook:
            {context_text}
            
            Please provide a clear, helpful response that:
            1. Directly answers the student's question using the provided information
            2. Is accurate to ZJNU policies and procedures
            3. Is friendly and supportive for international students
            4. If information is incomplete, suggest where to find more help
            5. Keep responses concise but comprehensive (2-4 paragraphs max)
            6. Use simple, clear English suitable for non-native speakers

            Important: Only use the provided handbook information. Do not make up policies.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful ZJNU international student advisor. Provide accurate, clear information from the university handbook. Be supportive and professional."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI Handbook Enhancement Error: {e}")
            return self._format_fallback_response(database_results)
    
    def enhance_pe_response(self, question, pe_data):
        """
        Use AI to enhance PE class responses with better explanations and helpful tips
        """
        if not self.ai_enabled:
            return self._format_pe_fallback_response(pe_data)
        
        try:
            # Build context from PE data
            location = pe_data.get('location_details', {})
            teacher = pe_data.get('teacher', {})
            schedule = pe_data.get('schedule', {})
            
            context = f"""
            Sport: {pe_data.get('sport', 'Unknown')}
            Location: {location.get('name', 'Unknown')}
            Building: {location.get('building', 'Not specified')}
            Room: {location.get('room_number', 'Not specified')}
            Schedule: {schedule.get('day', 'Unknown')} {schedule.get('time', '')}
            Teacher: {teacher.get('name', 'Not assigned')}
            Contact: {teacher.get('contact', 'Not available')}
            """
            
            prompt = f"""
            A ZJNU international student asked: "{question}"
            
            Here is their PE class information:
            {context}
            
            Please provide a natural, helpful response that:
            1. Clearly states where and when the class is
            2. Mentions the teacher and any contact information if available
            3. Is friendly, welcoming, and easy to understand
            4. Offers one helpful tip (like what to bring or where to find the building)
            5. Ends with an offer for additional help
            
            Keep it concise (2-3 sentences) and student-friendly.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You help ZJNU international students find their PE classes. Be clear, friendly, and helpful. Provide practical information."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI PE Enhancement Error: {e}")
            return self._format_pe_fallback_response(pe_data)
    
    def handle_complex_queries(self, question):
        """
        Handle complex queries that need combined information from both systems
        """
        if not self.ai_enabled:
            return self._fallback_complex_response(question)
        
        try:
            prompt = f"""
            A ZJNU international student asked this complex question: "{question}"
            
            This question seems to need information from both PE classes and university handbook policies.
            
            As a helpful assistant, provide a thoughtful response that:
            1. Acknowledges the complexity of their question
            2. Explains how PE classes and academic policies relate at ZJNU
            3. Offers to help them find specific information about either aspect
            4. Suggests they might want to contact the International Student Office for detailed personal advice
            
            Be supportive and informative, but don't make up specific policies or requirements.
            Keep it helpful and encouraging (3-4 sentences).
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You help ZJNU students with complex questions involving both academic policies and PE requirements. Be honest about what you can help with."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI Complex Query Error: {e}")
            return self._fallback_complex_response(question)
    
    def _parse_ai_response(self, response_text):
        """Parse AI response safely with better error handling"""
        try:
            if isinstance(response_text, str):
                # Clean the response
                cleaned_text = response_text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]
                
                result = json.loads(cleaned_text)
            else:
                result = response_text
            
            # Ensure all required fields with defaults
            return {
                "intent": result.get("intent", "unknown"),
                "sport": result.get("sport", ""),
                "time_reference": result.get("time_reference", ""),
                "handbook_topic": result.get("handbook_topic", ""),
                "urgency": result.get("urgency", "low"),
                "language": result.get("language", "english"),
                "confidence": min(max(result.get("confidence", 0.5), 0.0), 1.0)
            }
        except Exception as e:
            logger.error(f"AI Response parsing error: {e}")
            logger.error(f"Original response: {response_text}")
            return self._fallback_intent_analysis("")
    
    def _fallback_intent_analysis(self, user_message):
        """Improved fallback intent analysis without AI"""
        if not user_message:
            return {
                "intent": "unknown",
                "sport": "",
                "time_reference": "",
                "handbook_topic": "",
                "urgency": "low",
                "language": "english",
                "confidence": 0.1
            }
            
        message_lower = user_message.lower()
        
        # Enhanced PE class keywords with Chinese support
        pe_keywords = {
            'basketball', 'swimming', 'tennis', 'badminton', 'soccer', 
            'volleyball', 'table tennis', 'tai chi', 'ping pong',
            'class', 'schedule', 'location', 'teacher', 'coach', 'practice',
            '篮球', '游泳', '网球', '羽毛球', '足球', '排球', '乒乓球', '太极',
            '体育课', '运动', '训练'
        }
        
        # Enhanced handbook keywords
        handbook_keywords = {
            'handbook', 'policy', 'requirement', 'deadline', 'academic',
            'visa', 'scholarship', 'graduation', 'fee', 'tuition', 'housing',
            'accommodation', 'grading', 'gpa', 'credit', 'course', 'register',
            'registration', 'admission', 'application', '国际学生', '手册',
            '政策', '要求', '签证', '毕业', '住宿', '费用'
        }
        
        pe_score = sum(3 for keyword in pe_keywords if keyword in message_lower)
        handbook_score = sum(3 for keyword in handbook_keywords if keyword in message_lower)
        
        # Detect language
        has_chinese = any(char in user_message for char in ['篮球', '游泳', '网球', '羽毛球', '足球', '排球', '乒乓球', '太极'])
        language = "chinese" if has_chinese and not any(c.isalpha() for c in user_message if c.isascii()) else "mixed" if has_chinese else "english"
        
        # Determine intent
        if pe_score > 0 and handbook_score > 0:
            intent = "combined"
            confidence = 0.7
        elif pe_score > handbook_score:
            intent = "pe_class"
            confidence = 0.8
        elif handbook_score > 0:
            intent = "handbook"
            confidence = 0.8
        else:
            intent = "unknown"
            confidence = 0.3
        
        # Sport detection
        sport_found = ""
        sports_mapping = {
            'basketball': 'basketball', '篮球': 'basketball',
            'swimming': 'swimming', '游泳': 'swimming',
            'tennis': 'tennis', '网球': 'tennis',
            'badminton': 'badminton', '羽毛球': 'badminton',
            'soccer': 'soccer', '足球': 'soccer',
            'volleyball': 'volleyball', '排球': 'volleyball',
            'table tennis': 'table tennis', 'ping pong': 'table tennis', '乒乓球': 'table tennis',
            'tai chi': 'tai chi', '太极': 'tai chi', '太极拳': 'tai chi'
        }
        
        for keyword, sport in sports_mapping.items():
            if keyword in message_lower:
                sport_found = sport
                break
        
        return {
            "intent": intent,
            "sport": sport_found,
            "time_reference": "today",
            "handbook_topic": "",
            "urgency": "low",
            "language": language,
            "confidence": confidence
        }
    
    def _format_fallback_response(self, database_results):
        """Improved fallback response formatting without AI"""
        if database_results.get("faqs"):
            return database_results["faqs"][0].answer
        elif database_results.get("sections"):
            return database_results["sections"][0].content
        else:
            return "I couldn't find specific information about your question in the ZJNU handbook. Please contact the International Student Office at iso@zjnu.cn or call +86 (579) 82283155 for more help."
    
    def _format_pe_fallback_response(self, pe_data):
        """Improved PE fallback response"""
        sport = pe_data.get('sport', 'PE')
        location = pe_data.get('location_details', {})
        schedule = pe_data.get('schedule', {})
        
        response = f"Your {sport} class is at {location.get('name', 'the sports facility')}"
        if location.get('building'):
            response += f" in {location['building']}"
        if schedule.get('day'):
            response += f" on {schedule['day']}"
        if schedule.get('time'):
            response += f" from {schedule['time']}"
        
        response += ". You can find more details in your student portal or contact the PE department."
        return response
    
    def _fallback_complex_response(self, question):
        """Fallback for complex queries"""
        return "This is an interesting question that touches on both PE classes and university policies. At ZJNU, PE classes contribute to your academic credits and follow the university's academic calendar. For specific details about how this applies to your situation, I recommend contacting the International Student Office who can provide personalized advice."

# Global instance
ai_service = AIService()