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
            # ✅ Correct initialization for old SDK
            openai.api_key = api_key
            self.client = openai
            self.ai_enabled = True
            logger.info("AI Service initialized with OpenAI GPT-4o-mini (old SDK mode)")
        else:
            self.ai_enabled = False
            logger.warning("OpenAI API key not found. Using fallback mode.")
    
    def analyze_student_query(self, user_message):
        if not self.ai_enabled:
            return self._fallback_intent_analysis(user_message)
        
        try:
            prompt = f"""
            Analyze this international student's question about ZJNU (Zhejiang Normal University) and determine:
            1. Primary intent: PE classes, university handbook, or both
            2. If PE: extract sport name and any time references
            3. If handbook: extract main topics and urgency
            4. Confidence level (0.0-1.0)

            Return ONLY valid JSON.

            Student Question: "{user_message}"
            """
            
            # ✅ Old SDK syntax
            response = self.client.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You analyze ZJNU international student questions. Return JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result = response.choices[0].message['content'].strip()
            return self._parse_ai_response(result)
            
        except Exception as e:
            logger.error(f"AI Service Error: {e}")
            return self._fallback_intent_analysis(user_message)
    
    def enhance_handbook_response(self, question, database_results, context=""):
        if not self.ai_enabled:
            return self._format_fallback_response(database_results)
        
        try:
            context_text = ""
            if database_results.get("faqs"):
                for faq in database_results["faqs"][:2]:
                    context_text += f"Q: {faq.question}\nA: {faq.answer}\n\n"
            
            if database_results.get("sections"):
                for section in database_results["sections"][:2]:
                    context_text += f"Title: {section.title}\nContent: {section.content}\n\n"
            
            prompt = f"""
            A student asked: "{question}"

            Here is information from the ZJNU handbook:
            {context_text}

            Provide a clear, helpful, accurate response in 2-4 paragraphs. Use simple English.
            """
            
            # ✅ Old SDK
            response = self.client.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a ZJNU handbook assistant. Use provided info only."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message['content'].strip()
            
        except Exception as e:
            logger.error(f"AI Handbook Enhancement Error: {e}")
            return self._format_fallback_response(database_results)
    
    def enhance_pe_response(self, question, pe_data):
        if not self.ai_enabled:
            return self._format_pe_fallback_response(pe_data)
        
        try:
            location = pe_data.get('location_details', {})
            teacher = pe_data.get('teacher', {})
            schedule = pe_data.get('schedule', {})
            
            context = f"""
            Sport: {pe_data.get('sport', 'Unknown')}
            Location: {location.get('name', 'Unknown')}
            Building: {location.get('building')}
            Room: {location.get('room_number')}
            Schedule: {schedule.get('day')} {schedule.get('time')}
            Teacher: {teacher.get('name')}
            Contact: {teacher.get('contact')}
            """
            
            prompt = f"""
            A ZJNU student asked: "{question}"

            Use this PE class data:
            {context}

            Provide a friendly 2-3 sentence answer.
            """
            
            
            response = self.client.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You help ZJNU students find PE classes."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.2
            )
            
            return response.choices[0].message['content'].strip()
            
        except Exception as e:
            logger.error(f"AI PE Enhancement Error: {e}")
            return self._format_pe_fallback_response(pe_data)
    
    def handle_complex_queries(self, question):
        if not self.ai_enabled:
            return self._fallback_complex_response(question)
        
        try:
            prompt = f"""
            A student asked: "{question}"

            Provide a helpful explanation involving both handbook + PE information.
            """
            
            # ✅ Old SDK
            response = self.client.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You help ZJNU students with complex questions."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,
                temperature=0.3
            )
            
            return response.choices[0].message['content'].strip()
            
        except Exception as e:
            logger.error(f"AI Complex Query Error: {e}")
            return self._fallback_complex_response(question)

    def classify_handbook_topic(self, user_message):
        """More accurate handbook topic classification"""
        message = user_message.lower()
        
        # Enhanced category mapping that matches your JSON structure
        category_keywords = {
            "Visa Application / 签证申请": [
                "visa", "passport", "renew", "出入境", "签证", "residence", "permit", 
                "entry", "exit", "overstay", "immigration", "jw202", "jw201", "lost passport",
                "护照", "续签", "居留", "出入境管理局"
            ],
            "Academic Affairs / 学业指南": [
                "course", "class", "credit", "exam", "grade", "attendance", "absence",
                "register", "enroll", "major", "program", "degree", "non-degree", "study",
                "学分", "考试", "成绩", "注册", "专业", "学位", "学习", "课程", "选课"
            ],
            "Regulations on Tuition and Accommodation / 学费与住宿规定": [
                "tuition", "fee", "payment", "refund", "accommodation", "dorm", "housing",
                "rent", "insurance", "scholarship", "宿舍", "住宿", "退款", "保险", "缴费",
                "学费", "住宿费", "押金"
            ],
            "Guide to Campus Life / 校园生活指南": [
                "campus", "library", "wifi", "internet", "card", "medical", "hospital",
                "心理", "counseling", "insurance", "校园", "图书馆", "网络", "医院", "一卡通",
                "心理咨询", "校医院"
            ],
            "Scholarships for International Students / 国际学生奖学金指南": [
                "scholarship", "stipend", "financial", "funding", "csc", "award", "allowance",
                "奖学金", "资助", "生活费", "奖学金申请"
            ],
            "Student Status & Degree Regulations / 学籍与学位规定": [
                "status", "degree", "graduation", "withdrawal", "suspension", "transfer",
                "certificate", "diploma", "学籍", "学位", "毕业", "休学", "转专业", "退学",
                "毕业要求", "学位授予"
            ],
            "Disciplinary & Attendance Rules / 纪律与考勤规定": [
                "disciplinary", "attendance", "absence", "warning", "violation", "rules",
                "punishment", "cheating", "plagiarism", "纪律", "考勤", "处分", "警告", "作弊",
                "旷课"
            ],
            "Useful Laws and Forms / 常用法律与表格": [
                "law", "regulation", "form", "download", "legal", "document", "police",
                "法律", "法规", "表格", "下载", "派出所", "住宿登记"
            ]
        }
        
        # Score each category
        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(2 if f" {kw} " in f" {message} " else 1 for kw in keywords if kw in message)
            if score > 0:
                scores[category] = score
        
        if scores:
            best_category = max(scores, key=scores.get)
            # Only return if we have reasonable confidence
            if scores[best_category] >= 2:
                return best_category
        
        return None  # Return None instead of "Unknown" for better filtering

    def _parse_ai_response(self, response_text):
        try:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            result = json.loads(cleaned_text)

            return {
                "intent": result.get("intent", "unknown"),
                "sport": result.get("sport", ""),
                "time_reference": result.get("time_reference", ""),
                "handbook_topic": result.get("handbook_topic", ""),
                "urgency": result.get("urgency", "low"),
                "language": result.get("language", "english"),
                "confidence": result.get("confidence", 0.5)
            }

        except Exception as e:
            logger.error(f"AI Response parsing error: {e}")
            return self._fallback_intent_analysis("")
    
    def _fallback_intent_analysis(self, user_message):
        """Fallback intent analysis when AI is disabled"""
        message_lower = user_message.lower()
        
        # Simple sport detection
        sports = {
            'basketball': 'basketball', '篮球': 'basketball',
            'swimming': 'swimming', '游泳': 'swimming', 
            'tennis': 'tennis', '网球': 'tennis',
            'badminton': 'badminton', '羽毛球': 'badminton',
            'soccer': 'soccer', '足球': 'soccer',
            'volleyball': 'volleyball', '排球': 'volleyball',
            'table tennis': 'table tennis', 'ping pong': 'table tennis', '乒乓球': 'table tennis',
            'tai chi': 'tai chi', '太极': 'tai chi', '太极拳': 'tai chi'
        }
        
        detected_sport = None
        for keyword, sport in sports.items():
            if keyword in message_lower:
                detected_sport = sport
                break
        
        # Simple handbook detection
        handbook_keywords = ['visa', 'passport', 'tuition', 'fee', 'accommodation', 
                           'dorm', 'scholarship', 'grade', 'exam', 'credit', 'attendance']
        
        is_handbook = any(keyword in message_lower for keyword in handbook_keywords)
        
        if detected_sport and is_handbook:
            intent = "combined"
        elif detected_sport:
            intent = "pe_class"
        elif is_handbook:
            intent = "handbook"
        else:
            intent = "unknown"
            
        return {
            "intent": intent,
            "sport": detected_sport or "",
            "time_reference": "",
            "handbook_topic": "",
            "urgency": "low",
            "language": "english",
            "confidence": 0.3  # Low confidence for fallback
        }
    
    def _format_fallback_response(self, database_results):
        """Format fallback response when AI enhancement fails"""
        if database_results.get("faqs"):
            faq = database_results["faqs"][0]
            return f"{faq.answer}"
        
        if database_results.get("sections"):
            section = database_results["sections"][0]
            return f"{section.content}"
        
        return "I found some information but couldn't format it properly. Please contact the International Student Office for detailed assistance."
    
    def _format_pe_fallback_response(self, pe_data):
        """Format fallback PE response"""
        sport = pe_data.get('sport', 'Unknown sport')
        location = pe_data.get('location_details', {})
        
        response = f"Your {sport} class"
        
        if location.get('name'):
            response += f" is at {location['name']}"
            if location.get('building'):
                response += f" ({location['building']})"
        
        schedule = pe_data.get('schedule', {})
        if schedule.get('day'):
            response += f" on {schedule['day']}"
            if schedule.get('time'):
                response += f" from {schedule['time']}"
        
        teacher = pe_data.get('teacher', {})
        if teacher.get('name'):
            response += f" with {teacher['name']}"
        
        return response + "."
    
    def _fallback_complex_response(self, question):
        """Fallback for complex queries"""
        return f"I understand you're asking about '{question}'. For detailed information about both PE classes and university policies, please contact the International Student Office at iso@zjnu.cn or visit Room 100, North Building, Administration Center."


# Global instance
ai_service = AIService()