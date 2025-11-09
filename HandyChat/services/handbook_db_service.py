
#========================================================#
# this script provides database services specifically for managing the handbook data
# It initializes handbook categories, sections, and FAQs in the database
# It also provides enhanced search and classification functionalities for handbook queries
#========================================================#



from extensions import db
from models import HandbookCategory, HandbookSection, HandbookFAQ
import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class HandbookDBService:
    def __init__(self):
        self.initialized = False
    
    def initialize_handbook_data(self):
        """Initialize all handbook data in database with improved content"""
        if self.initialized:
            return True
            
        try:
            # Enhanced categories with better keywords
            categories_data = {
                "academic": {
                    "keywords": [
                        "course", "class", "registration", "enrollment", "credit", 
                        "study", "program", "major", "curriculum", "attendance", "schedule",
                        "选课", "课程", "注册", "学分", "专业", "课程表"
                    ],
                    "description": "Academic policies, course registration, program requirements, and class management"
                },
                "graduation": {
                    "keywords": [
                        "graduation", "degree", "certificate", "diploma", "completion", 
                        "requirements", "HSK", "thesis", "defense", "commencement",
                        "毕业", "学位", "要求", "汉语水平考试", "论文", "答辩"
                    ],
                    "description": "Graduation requirements, degree completion, and certification procedures"
                },
                "fees": {
                    "keywords": [
                        "tuition", "fee", "payment", "scholarship", "funding", 
                        "cost", "financial", "refund", "deposit", "money",
                        "学费", "费用", "付款", "奖学金", "退款", "押金"
                    ],
                    "description": "Tuition fees, payment procedures, scholarships, and financial information"
                },
                "visa": {
                    "keywords": [
                        "visa", "residence", "permit", "passport", "immigration", 
                        "entry", "extension", "JW202", "exit-entry", "health check",
                        "签证", "居留", "许可", "护照", "延期", "体检"
                    ],
                    "description": "Student visas, residence permits, immigration procedures, and documentation"
                },
                "accommodation": {
                    "keywords": [
                        "housing", "dormitory", "residence", "hostel", "apartment", 
                        "on-campus", "off-campus", "living", "facility", "canteen",
                        "住宿", "宿舍", "公寓", "校园", "食堂", "生活"
                    ],
                    "description": "Student housing, accommodation options, and living facilities"
                },
                "campus_life": {
                    "keywords": [
                        "campus", "life", "activity", "club", "sports", "facility",
                        "library", "internet", "wifi", "transportation", "shopping",
                        "校园生活", "活动", "社团", "体育", "设施", "图书馆"
                    ],
                    "description": "Campus facilities, student activities, clubs, and daily life"
                },
                "health": {
                    "keywords": [
                        "health", "medical", "insurance", "clinic", "hospital", "doctor",
                        "psychological", "counseling", "emergency", "treatment",
                        "健康", "医疗", "保险", "诊所", "心理", "紧急"
                    ],
                    "description": "Health services, medical insurance, counseling, and emergency care"
                }
            }

            # Create or update categories
            for category_name, category_info in categories_data.items():
                category = HandbookCategory.query.filter_by(name=category_name).first()
                if not category:
                    category = HandbookCategory(
                        name=category_name,
                        description=category_info["description"],
                        keywords=json.dumps(category_info["keywords"], ensure_ascii=False)
                    )
                    db.session.add(category)
                else:
                    # Update existing category
                    category.keywords = json.dumps(category_info["keywords"], ensure_ascii=False)
                    category.description = category_info["description"]
            
            db.session.commit()
            
            # Create enhanced sample content
            self.create_enhanced_sections()
            self.create_enhanced_faqs()
            
            self.initialized = True
            logger.info("✅ Handbook data initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing handbook data: {e}")
            db.session.rollback()
            return False
    
    def create_enhanced_sections(self):
        """Create enhanced handbook sections with better content"""
        sections_data = [
            {
                "title": "Academic Calendar and Important Dates",
                "content": (
                    "Zhejiang Normal University follows a two-semester system:\n\n"
                    "• Spring Semester: Late February to late June\n"
                    "• Autumn Semester: Early September to mid-January\n\n"
                    "Key dates for international students:\n"
                    "• Course Registration: 1 week before semester starts\n"
                    "• Add/Drop Period: First 2 weeks of semester\n"
                    "• Midterm Exams: Weeks 8-9\n"
                    "• Final Exams: Last 2 weeks of semester\n"
                    "• National Holidays: Spring Festival, National Day (check annual calendar)\n\n"
                    "Always check the official ZJNU academic calendar for exact dates each year."
                ),
                "category": "academic",
                "priority": 1
            },
            {
                "title": "Course Registration Procedures",
                "content": (
                    "International students must register for courses through the ZJNU Online Service System:\n\n"
                    "1. Login to http://ehall.zjnu.edu.cn\n"
                    "2. Select 'Course Registration' from the student services menu\n"
                    "3. Choose your courses based on your program requirements\n"
                    "4. Submit your selection before the deadline\n\n"
                    "Important notes:\n"
                    "• Registration is open for one week before each semester\n"
                    "• You can add/drop courses during the first two weeks\n"
                    "• Late registration requires approval from International Student Office\n"
                    "• Minimum credit load: 15 credits per semester\n"
                    "• Maximum credit load: 25 credits per semester"
                ),
                "category": "academic",
                "priority": 1
            },
            {
                "title": "Tuition Fees and Payment Methods",
                "content": (
                    "Tuition fees for international students (2025 academic year):\n\n"
                    "• Chinese-taught programs: 18,000-22,000 RMB/year\n"
                    "• English-taught programs: 22,000-28,000 RMB/year\n"
                    "• Accommodation: 4,000-8,000 RMB/year (depending on room type)\n\n"
                    "Payment methods:\n"
                    "• Online payment through university system\n"
                    "• Bank transfer to university account\n"
                    "• Cash payment at Finance Office (not recommended)\n\n"
                    "Payment deadlines:\n"
                    "• Fall semester: September 15\n"
                    "• Spring semester: March 1\n\n"
                    "Late payments may result in registration holds or late fees."
                ),
                "category": "fees",
                "priority": 1
            },
            {
                "title": "Visa and Residence Permit Procedures",
                "content": (
                    "All international students must maintain valid visa status:\n\n"
                    "1. Entry: Use X1 student visa for programs longer than 6 months\n"
                    "2. Registration: Register at local police station within 24 hours of arrival\n"
                    "3. Health Check: Complete at designated hospital within 30 days\n"
                    "4. Residence Permit: Apply within 30 days of entry\n\n"
                    "Required documents for residence permit:\n"
                    "• Valid passport and X1 visa\n"
                    "• JW202 form\n"
                    "• Admission notice\n"
                    "• Health examination certificate\n"
                    "• Temporary residence registration\n"
                    "• Passport photos (2-inch, white background)\n\n"
                    "Apply at: Jinhua Exit-Entry Administration Bureau, 1055 Bayi North Street"
                ),
                "category": "visa",
                "priority": 1
            },
            {
                "title": "Graduation Requirements for International Students",
                "content": (
                    "To graduate from ZJNU, international students must:\n\n"
                    "Academic Requirements:\n"
                    "• Complete all required courses and credits\n"
                    "• Maintain minimum GPA of 2.0 (on 4.0 scale)\n"
                    "• Pass final thesis/dissertation defense (if applicable)\n\n"
                    "Chinese Language Requirements:\n"
                    "• Chinese-taught programs: HSK Level 5\n"
                    "• English-taught undergraduate: HSK Level 4\n"
                    "• English-taught graduate: HSK Level 3\n\n"
                    "Other Requirements:\n"
                    "• Clear all financial obligations\n"
                    "• Return all library materials\n"
                    "• Complete exit procedures with International Office\n\n"
                    "Graduation ceremonies are held in January and July each year."
                ),
                "category": "graduation",
                "priority": 1
            }
        ]

        for section_data in sections_data:
            category = HandbookCategory.query.filter_by(name=section_data["category"]).first()
            if category:
                section = HandbookSection.query.filter_by(title=section_data["title"]).first()
                if not section:
                    section = HandbookSection(
                        title=section_data["title"],
                        content=section_data["content"],
                        category_id=category.id,
                        priority=section_data["priority"]
                    )
                    db.session.add(section)
        
        db.session.commit()
    
    def create_enhanced_faqs(self):
        """Create enhanced frequently asked questions"""
        faqs_data = [
            {
                "question": "What HSK level do I need to graduate?",
                "answer": (
                    "HSK requirements depend on your program:\n\n"
                    "• Chinese-taught degree programs: HSK Level 5 (minimum 180 points)\n"
                    "• English-taught undergraduate programs: HSK Level 4 (minimum 180 points)\n"
                    "• English-taught graduate programs (Master's/PhD): HSK Level 3 (minimum 180 points)\n\n"
                    "You must provide official HSK certificate before applying for graduation. "
                    "HSK tests are offered monthly at Zhejiang Normal University test center."
                ),
                "category": "graduation",
                "keywords": ["hsk", "graduate", "graduation", "chinese", "language", "requirement", "汉语水平考试"]
            },
            {
                "question": "How do I extend my student visa?",
                "answer": (
                    "Visa extension process:\n\n"
                    "1. Start 60 days before visa expiration\n"
                    "2. Login to ZJNU Online Service Hall\n"
                    "3. Upload required documents:\n"
                    "   - Passport copy (photo page and current visa page)\n"
                    "   - Latest tuition payment receipt\n"
                    "   - Academic performance record\n"
                    "   - Bank statement (minimum 10,000 RMB)\n"
                    "4. University reviews and issues supporting documents\n"
                    "5. Take documents to Exit-Entry Bureau for processing\n\n"
                    "Processing time: 15-20 working days. Do not overstay your visa!"
                ),
                "category": "visa",
                "keywords": ["visa", "extend", "extension", "residence", "permit", "renew", "签证延期"]
            },
            {
                "question": "What scholarships are available for international students?",
                "answer": (
                    "ZJNU offers several scholarships for international students:\n\n"
                    "• Chinese Government Scholarship (CSC)\n"
                    "• Zhejiang Provincial Government Scholarship\n"
                    "• ZJNU Excellent International Student Scholarship\n"
                    "• International Chinese Teachers Scholarship\n"
                    "• Belt and Road Scholarship\n\n"
                    "Application periods:\n"
                    "• Fall semester: March 1 - May 31\n"
                    "• Spring semester: September 1 - November 30\n\n"
                    "Contact International Student Office for application details: iso@zjnu.cn"
                ),
                "category": "fees",
                "keywords": ["scholarship", "financial", "aid", "funding", "apply", "奖学金"]
            },
            {
                "question": "How do I find accommodation?",
                "answer": (
                    "Accommodation options for international students:\n\n"
                    "On-campus (recommended for first-year students):\n"
                    "• International Student Dormitory\n"
                    "• Double rooms: 4,000 RMB/semester\n"
                    "• Single rooms: 8,000 RMB/semester\n"
                    "• Includes: bed, desk, WiFi, air conditioning, shared bathroom\n\n"
                    "Off-campus (requires approval):\n"
                    "• Must register with local police within 24 hours\n"
                    "• Provide rental contract to International Office\n"
                    "• Ensure location is safe and accessible to campus\n\n"
                    "Apply for on-campus housing when you receive admission notice."
                ),
                "category": "accommodation",
                "keywords": ["accommodation", "housing", "dormitory", "room", "live", "住宿", "宿舍"]
            },
            {
                "question": "What is the class attendance policy?",
                "answer": (
                    "ZJNU has strict attendance policies:\n\n"
                    "• Minimum attendance requirement: 80% of classes\n"
                    "• Absence exceeding 1/3 of total classes: automatic failure\n"
                    "• Leave requests must be submitted in advance\n"
                    "• Medical absences require doctor's certificate\n\n"
                    "Consequences of poor attendance:\n"
                    "• First warning: 70-79% attendance\n"
                    "• Academic probation: 60-69% attendance\n"
                    "• Course failure: below 60% attendance\n\n"
                    "Always inform your teacher and department office if you cannot attend class."
                ),
                "category": "academic",
                "keywords": ["attendance", "absent", "absence", "class", "policy", "出勤", "缺课"]
            }
        ]

        for faq_data in faqs_data:
            category = HandbookCategory.query.filter_by(name=faq_data["category"]).first()
            if category:
                faq = HandbookFAQ.query.filter_by(question=faq_data["question"]).first()
                if not faq:
                    faq = HandbookFAQ(
                        question=faq_data["question"],
                        answer=faq_data["answer"],
                        category_id=category.id,
                        keywords=json.dumps(faq_data["keywords"], ensure_ascii=False)
                    )
                    db.session.add(faq)
        
        db.session.commit()
    
    def search_handbook(self, question):
        """Enhanced search with better relevance scoring"""
        question_lower = question.lower().strip()
        
        if not question_lower:
            return {"faqs": [], "sections": []}
        
        # Search FAQs with improved matching
        all_faqs = HandbookFAQ.query.all()
        matched_faqs = []
        
        for faq in all_faqs:
            score = self._calculate_relevance_score(question_lower, faq.question, faq.answer, faq.keywords)
            if score > 0.3:  # Higher threshold for better quality
                matched_faqs.append((faq, score))
        
        # Search sections
        all_sections = HandbookSection.query.all()
        matched_sections = []
        
        for section in all_sections:
            score = self._calculate_relevance_score(question_lower, section.title, section.content, "")
            if score > 0.4:  # Sections need higher relevance
                matched_sections.append((section, score))
        
        # Sort by relevance and return top results
        matched_faqs.sort(key=lambda x: x[1], reverse=True)
        matched_sections.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "faqs": [faq for faq, score in matched_faqs[:3]],
            "sections": [section for section, score in matched_sections[:2]]
        }
    
    def _calculate_relevance_score(self, question, title, content, keywords_json):
        """Calculate relevance score with improved algorithm"""
        # Combine all text to search
        search_text = f"{title} {content}".lower()
        if keywords_json:
            try:
                keywords = json.loads(keywords_json)
                search_text += " " + " ".join(keywords)
            except:
                pass
        
        # Calculate score based on various factors
        score = 0
        
        # Exact phrase matches
        question_words = set(re.findall(r'\w+', question))
        text_words = set(re.findall(r'\w+', search_text))
        
        # Word overlap
        common_words = question_words.intersection(text_words)
        if common_words:
            score += len(common_words) * 0.1
        
        # Title matches are very important
        title_lower = title.lower()
        for word in question_words:
            if len(word) > 3 and word in title_lower:
                score += 0.5
        
        # Content matches
        content_lower = content.lower()
        for word in question_words:
            if len(word) > 3 and word in content_lower:
                score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def classify_question(self, question):
        """Enhanced question classification"""
        if not question:
            return "general"
            
        question_lower = question.lower()
        categories = HandbookCategory.query.all()
        
        best_category = "general"
        best_score = 0
        
        for category in categories:
            try:
                keywords = json.loads(category.keywords)
                score = sum(2 for keyword in keywords if keyword in question_lower)
                
                # Boost score for exact matches
                for keyword in keywords:
                    if f" {keyword} " in f" {question_lower} ":
                        score += 3
                
                if score > best_score:
                    best_score = score
                    best_category = category.name
            except:
                continue
        
        return best_category if best_score > 0 else "general"

# Global instance
handbook_db_service = HandbookDBService()