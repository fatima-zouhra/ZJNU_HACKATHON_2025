
import json
import os
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class OptimizedHandbookService:
    def __init__(self):
        self.qa_pairs = []
        self.loaded = False
        
        self.file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "HandyChat", "static", "handbook", "handbook_optimized.json"  
        )
        
        # Debug: Log the path we're using
        logger.info(f"Optimized handbook path: {self.file_path}")
        logger.info(f"File exists: {os.path.exists(self.file_path)}")
        
        self.load_handbook_data()

    def load_handbook_data(self):
        """Load optimized handbook data"""
        try:
            if not os.path.exists(self.file_path):
                logger.error(f"❌ Optimized handbook not found at: {self.file_path}")
                
                
                alternative_paths = [
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static", "handbook", "handbook_optimized.json"),
                    "G:\\Documents\\Theam 10\\ZJNU_HACKATHON_2025_TEAM10\\HandyChaN_2025_TEAM10\\static\\handbook\\handbook_optimized.json"
                ]
                
                for alt_path in alternative_paths:
                    if os.path.exists(alt_path):
                        logger.info(f"Found handbook at alternative path: {alt_path}")
                        self.file_path = alt_path
                        break
                else:
                    logger.error("❌ Handbook not found at any alternative path")
                    return
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.qa_pairs = data.get("qa_pairs", [])
            self.loaded = True
            logger.info(f"Optimized handbook loaded: {len(self.qa_pairs)} Q&A pairs")
            
        except Exception as e:
            logger.error(f"❌ Error loading optimized handbook: {e}")

    def _try_migrate(self):
        """Try to run migration if optimized handbook doesn't exist"""
        try:
            logger.info("Optimized handbook not found, attempting migration...")
            migration_script = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "migrate_handbook.py"
            )
            
            if os.path.exists(migration_script):
                import subprocess
                result = subprocess.run(['python', migration_script], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("✅ Migration successful, reloading...")
                    self.load_handbook_data()
                else:
                    logger.error(f"❌ Migration failed: {result.stderr}")
            else:
                logger.error("❌ Migration script not found")
        except Exception as e:
            logger.error(f"❌ Migration attempt failed: {e}")

    def search_handbook(self, question: str) -> Dict[str, Any]:
        """Optimized search with STRICTER matching"""
        if not self.loaded or not self.qa_pairs:
            return {"found": False, "results": [], "error": "Handbook not loaded"}

        question_lower = question.lower().strip()
        if not question_lower:
            return {"found": False, "results": []}

        logger.info(f"🔍 OPTIMIZED search for: '{question}'")
        
        results = []
        
        for qa in self.qa_pairs:
            score = self._calculate_comprehensive_score(question_lower, qa)
            
            # STRICTER threshold to reduce noise
            if score > 0.3:  # Increased from 0.1 to 0.3
                results.append({
                    **qa,
                    "relevance_score": round(score, 3),
                    "match_type": self._get_match_type(question_lower, qa)
                })
        
        # Sort by relevance (highest first)
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Only return high-confidence matches
        high_confidence = [r for r in results if r["relevance_score"] >= 0.7]
        medium_confidence = [r for r in results if 0.5 <= r["relevance_score"] < 0.7]  
        low_confidence = [r for r in results if 0.3 <= r["relevance_score"] < 0.5]     
        
        logger.info(f"Match breakdown: {len(high_confidence)} high, {len(medium_confidence)} medium, {len(low_confidence)} low")
        
        # Return only high and medium confidence results
        if high_confidence:
            return {
                "found": True,
                "results": high_confidence[:3],
                "confidence": "high",
                "total_matches": len(high_confidence),
                "best_match_score": high_confidence[0]["relevance_score"]
            }
        elif medium_confidence:
            return {
                "found": True, 
                "results": medium_confidence[:2],
                "confidence": "medium",
                "total_matches": len(medium_confidence),
                "best_match_score": medium_confidence[0]["relevance_score"] if medium_confidence else 0
            }
        else:
            return {
                "found": False, 
                "results": [],
                "total_matches": 0,
                "confidence": "none"
            }

    def _calculate_comprehensive_score(self, user_question: str, qa: dict) -> float:
        """Calculate score with IMPROVED relevance and precision"""
        scores = []
        
        # Get all searchable text
        stored_en = qa["question_en"].lower().strip()
        stored_zh = qa["question_zh"].lower().strip()
        answer_en = qa.get("answer_en", "").lower()
        keywords = qa.get("keywords", [])
        variations = qa.get("variations", [])
        category = qa.get("category", "").lower()
        
        user_question_clean = user_question.lower().strip()
        
        # 1. EXACT MATCH - Highest priority (1.0)
        exact_score = self._exact_question_match(user_question_clean, qa)
        scores.append(exact_score)
        
        # 2. QUESTION CONTAINS - Very high priority (0.9-0.95)
        contains_score = self._question_contains_match(user_question_clean, stored_en, stored_zh)
        scores.append(contains_score)
        
        # 3. KEYWORD MATCH - High priority (0.3-0.8)
        keyword_score = self._keyword_match(user_question_clean, qa)
        scores.append(keyword_score)
        
        # 4. VARIATION MATCH - Medium priority (0.6-0.8)
        variation_score = self._variation_match(user_question_clean, qa)
        scores.append(variation_score)
        
        # 5. SEMANTIC SIMILARITY - Medium priority (0.2-0.7)
        semantic_score = self._semantic_similarity(user_question_clean, qa)
        scores.append(semantic_score)
        
        # 6. ANSWER CONTENT MATCH - Low priority (0.1-0.5)
        answer_score = self._answer_content_match(user_question_clean, qa)
        scores.append(answer_score)
        
        # 7. CATEGORY MATCH - Context priority (0.3-0.6)
        category_score = self._category_match(user_question_clean, qa)
        scores.append(category_score)
        
        
        best_score = max(scores)
        
        # DEBUG: Log high-scoring matches to understand scoring
        if best_score > 0.5:
            logger.info(f"High score: '{stored_en[:60]}...' | Score: {best_score:.2f} | Type: {self._get_match_type(user_question_clean, qa)}")
        
        return min(best_score, 1.0)

    def _question_contains_match(self, user_question: str, stored_en: str, stored_zh: str) -> float:
        """Check if user question contains stored question or vice versa"""
        # Clean the questions for better matching
        user_clean = user_question.replace('?', '').replace('how', '').replace('what', '').replace('when', '').strip()
        stored_en_clean = stored_en.replace('?', '').strip()
        
        # User question contains the main part of stored question
        if stored_en_clean and stored_en_clean in user_clean:
            return 0.95
        
        # Stored question contains user question
        if user_clean and user_clean in stored_en_clean:
            return 0.9
        
        # Check for significant word overlap
        user_words = set(re.findall(r'\w+', user_clean))
        stored_words = set(re.findall(r'\w+', stored_en_clean))
        
        common_words = user_words.intersection(stored_words)
        if len(common_words) >= 3:  # At least 3 common significant words
            return 0.85
        
        return 0.0

    def _keyword_match(self, user_question: str, qa: dict) -> float:
        """IMPROVED Keyword-based matching with context awareness"""
        score = 0.0
        keywords = qa.get("keywords", [])
        question_en = qa["question_en"].lower()
        
        user_words = set(re.findall(r'\w+', user_question))
        
        # Check explicit keywords first (highest weight)
        keyword_matches = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in user_question:
                # Exact keyword match
                if f" {keyword_lower} " in f" {user_question} ":
                    score += 0.4
                    keyword_matches += 1
                else:
                    score += 0.2
                    keyword_matches += 1
        
        # Boost for multiple keyword matches
        if keyword_matches >= 2:
            score += 0.3
        elif keyword_matches >= 3:
            score += 0.5 
        # Check if question contains important words from user question
        important_words = [word for word in user_words if len(word) > 4]  # Only longer, more meaningful words
        
        for word in important_words:
            if word in question_en:
                score += 0.15
        
        return min(score, 1.0)

    def _semantic_similarity(self, user_question: str, qa: dict) -> float:
        """IMPROVED semantic similarity with better word filtering"""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
        
        user_words = set(re.findall(r'\w+', user_question.lower()))
        question_words = set(re.findall(r'\w+', qa["question_en"].lower()))
        
        # Filter out stop words and short words
        user_words_filtered = {word for word in user_words if word not in stop_words and len(word) > 2}
        question_words_filtered = {word for word in question_words if word not in stop_words and len(word) > 2}
        
        if not user_words_filtered or not question_words_filtered:
            return 0.0
        
        # Jaccard similarity
        intersection = user_words_filtered.intersection(question_words_filtered)
        union = user_words_filtered.union(question_words_filtered)
        
        similarity = len(intersection) / len(union)
        
        # Boost for multiple common meaningful words
        if len(intersection) >= 2:
            similarity += 0.2
        if len(intersection) >= 3:
            similarity += 0.3
            
        return min(similarity, 1.0)

    def _answer_content_match(self, user_question: str, qa: dict) -> float:
        """Match based on answer content"""
        answer_en = qa.get("answer_en", "").lower()
        user_words = set(re.findall(r'\w+', user_question))
        
        score = 0.0
        for word in user_words:
            if len(word) > 3 and word in answer_en:
                score += 0.15
        
        return min(score, 0.8)

    def _category_match(self, user_question: str, qa: dict) -> float:
        """Match based on category keywords"""
        category = qa.get("category", "").lower()
        
        # Common category keywords
        category_keywords = {
            "visa": ["visa", "签证"],
            "academic": ["academic", "学业", "study", "学习"],
            "tuition": ["tuition", "学费", "fee", "费用"],
            "accommodation": ["accommodation", "住宿", "dorm", "housing"],
            "insurance": ["insurance", "保险"],
            "scholarship": ["scholarship", "奖学金"],
            "attendance": ["attendance", "出勤", "考勤"],
            "disciplinary": ["disciplinary", "纪律", "处分"]
        }
        
        user_question_lower = user_question.lower()
        
        for cat_type, keywords in category_keywords.items():
            if any(keyword in user_question_lower for keyword in keywords):
                # Check if this QA belongs to the matching category
                if any(keyword in category for keyword in keywords):
                    return 0.6
        
        return 0.0

    def _exact_question_match(self, user_question: str, qa: dict) -> float:
        """Exact or near-exact question matches with better precision"""
        stored_en = qa["question_en"].lower().strip()
        stored_zh = qa["question_zh"].lower().strip()
        
        # Remove question marks and normalize
        user_q_clean = user_question.replace('?', '').strip()
        stored_en_clean = stored_en.replace('?', '').strip()
        stored_zh_clean = stored_zh.replace('?', '').strip()
        
        # Exact match (highest confidence)
        if user_q_clean == stored_en_clean or user_q_clean == stored_zh_clean:
            return 1.0
        
        # User question contains the stored question
        if stored_en_clean in user_q_clean:
            return 0.95
        
        # Stored question contains user question
        if user_q_clean in stored_en_clean:
            return 0.9
        
        # Chinese character matching
        if stored_zh_clean and any(char in stored_zh_clean for char in user_q_clean if '\u4e00' <= char <= '\u9fff'):
            return 0.85
            
        return 0.0

    def _variation_match(self, user_question: str, qa: dict) -> float:
        """Match against question variations"""
        variations = qa.get("variations", [])
        for variation in variations:
            variation_lower = variation.lower().strip()
            if user_question == variation_lower or variation_lower in user_question or user_question in variation_lower:
                return 0.8
        return 0.0

    def _get_match_type(self, user_question: str, qa: dict) -> str:
        """Determine what type of match occurred"""
        stored_en = qa["question_en"].lower()
        
        if user_question == stored_en:
            return "exact"
        elif stored_en in user_question or user_question in stored_en:
            return "contains"
        elif any(keyword in user_question for keyword in qa.get("keywords", [])):
            return "keyword"
        elif any(variation.lower() in user_question or user_question in variation.lower() for variation in qa.get("variations", [])):
            return "variation"
        else:
            return "semantic"

    def debug_search(self, question: str) -> Dict[str, Any]:
        """Debug method to see why searches aren't matching"""
        question_lower = question.lower().strip()
        debug_results = []
        
        for qa in self.qa_pairs[:10]:  # Check first 10 Q&A pairs
            scores = {
                "question": qa["question_en"][:50] + "...",
                "exact": self._exact_question_match(question_lower, qa),
                "keyword": self._keyword_match(question_lower, qa),
                "variation": self._variation_match(question_lower, qa),
                "semantic": self._semantic_similarity(question_lower, qa),
                "answer": self._answer_content_match(question_lower, qa),
                "category": self._category_match(question_lower, qa),
                "total": self._calculate_comprehensive_score(question_lower, qa)
            }
            debug_results.append(scores)
        
        return debug_results

    def get_all_questions(self):
        """Get all questions for debugging"""
        return [{"question_en": qa["question_en"], "category": qa["category"]} for qa in self.qa_pairs]

    def get_status(self):
        return {
            "loaded": self.loaded,
            "total_questions": len(self.qa_pairs),
            "file_path": self.file_path
        }

optimized_handbook_service = OptimizedHandbookService()