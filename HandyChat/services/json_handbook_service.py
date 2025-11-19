import json
import os
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class JSONHandbookService:
    def __init__(self):
        self.handbook_data = None
        self.loaded = False

        self.file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "HandyChat", "static", "handbook", "handbook_2025.json"
        )
        self.load_handbook_data()

    def load_handbook_data(self):
        """Load handbook data from JSON file"""
        try:
            if not os.path.exists(self.file_path):
                logger.error(f"Handbook JSON file not found at: {self.file_path}")
                self.handbook_data = []
                return
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.handbook_data = json.load(f)
            
            self.loaded = True
            logger.info(f"JSON handbook loaded: {len(self.handbook_data)} categories")
        except Exception as e:
            logger.error(f"❌ Error loading JSON handbook: {e}")
            self.handbook_data = []

    def search_handbook(self, question: str, language: str = "en") -> Dict[str, Any]:
        """Improved handbook search that actually finds matches"""
        if not self.loaded:
            return {"found": False, "results": []}

        question_lower = question.lower().strip()
        if not question_lower:
            return {"found": False, "results": []}

        logger.info(f"🔍 Searching handbook for: '{question}'")
        
        results = []
        
        # Search through ALL categories without strict filtering first
        for category in self.handbook_data:
            category_name = category["category"]
            
            for subcat in category.get("subcategories", []):
                for qa in subcat.get("questions", []):
                    score = self._calculate_relevance_score(question_lower, qa, category_name)
                    
                    # LOWER THRESHOLD for testing - find more matches
                    if score >= 0.3:  # Lowered threshold
                        results.append({
                            "category": category_name,
                            "subcategory": subcat["title"],
                            "question_en": qa.get("question_en", ""),
                            "answer_en": qa.get("answer_en", ""),
                            "question_zh": qa.get("question_zh", ""),
                            "answer_zh": qa.get("answer_zh", ""),
                            "attachments": qa.get("attachments", []),
                            "relevance_score": score,
                            "source": "json_handbook"
                        })
                        logger.info(f"📝 Found match: '{qa.get('question_en', '')[:50]}...' | Score: {score}")

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        logger.info(f"📊 Total matches found: {len(results)}")
        
        return {
            "found": len(results) > 0,
            "results": results[:3],  # Return top 3 results
            "total_matches": len(results),
            "predicted_category": results[0]["category"] if results else None
        }

    def _calculate_relevance_score(self, question: str, qa: dict, category: str) -> float:
        """Calculate relevance score with improved matching"""
        score = 0.0
        
        qa_question_en = qa.get("question_en", "").lower()
        qa_question_zh = qa.get("question_zh", "").lower()
        qa_answer_en = qa.get("answer_en", "").lower()
        
        qa_text = f"{qa_question_en} {qa_question_zh} {qa_answer_en}"
        
        # 1. Exact question match (highest weight)
        if qa_question_en in question:
            score += 1.0
            logger.info(f"🎯 Exact question match: '{qa_question_en}'")
        
        # 2. Question contains QA question
        if qa_question_en and any(word in question for word in qa_question_en.split() if len(word) > 3):
            score += 0.6
        
        # 3. User question contains keywords from QA question
        question_words = set(re.findall(r'\w+', question))
        qa_question_words = set(re.findall(r'\w+', qa_question_en))
        
        common_words = question_words.intersection(qa_question_words)
        if common_words:
            score += len(common_words) * 0.2
            logger.info(f"🔑 Common words: {common_words}")
        
        # 4. Answer contains question keywords
        for word in question_words:
            if len(word) > 3 and word in qa_answer_en:
                score += 0.1
        
        # 5. Chinese character matching
        if any(char in qa_question_zh for char in question if '\u4e00' <= char <= '\u9fff'):
            score += 0.3
        
        # 6. Boost for exact phrase matches in answer
        if any(phrase in qa_answer_en for phrase in question.split() if len(phrase) > 4):
            score += 0.2
        
        return min(score, 1.0)

    def get_status(self):
        return {
            "loaded": self.loaded,
            "categories_count": len(self.handbook_data),
            "total_questions": sum(len(s["questions"]) for c in self.handbook_data for s in c["subcategories"]),
            "file_path": self.file_path
        }

json_handbook_service = JSONHandbookService()