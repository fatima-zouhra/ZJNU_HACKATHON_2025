
#========================================================#
# this script provides a simple keyword-based handbook service for answering common questions about ZJNU policies and procedures
# it uses predefined question-answer pairs for quick responses, and that helps with testing and development before implementing more complex AI-based solutions
#========================================================#

import logging

logger = logging.getLogger(__name__)

class SimpleHandbookService:
    def __init__(self):
        self.qa_pairs = {
            # Graduation & Credits
            "pe credits graduation": "Yes, PE classes count toward academic credits required for graduation at ZJNU. Most PE classes are 1-2 credits each. The total credit requirements depend on your specific program.",
            
            "graduation requirements": "To graduate from ZJNU, international students must: 1) Complete all required courses and credits, 2) Maintain minimum GPA of 2.0, 3) Meet HSK requirements (Level 5 for Chinese-taught, Level 4 for English-taught undergraduate, Level 3 for English-taught graduate), 4) Clear all financial obligations.",
            
            "credit requirements": "Credit requirements vary by program. Bachelor's programs typically require 120-140 credits, Master's programs 30-40 credits. PE classes contribute to these totals.",
            
            # Combined queries
            "pe credit graduation": "Yes, PE classes provide academic credits that count toward your graduation requirements at ZJNU. Most sports classes are 1-2 credits each.",
            
            "sport class credit": "All PE classes at ZJNU provide academic credits: Basketball (2 credits), Swimming (2 credits), Tennis (1 credit), Badminton (1 credit), etc. These count toward your total graduation credits.",
            
            # Visa & Immigration
            "visa extension": "Apply for visa extension 60 days before expiration through ZJNU Online Service Hall. Required: passport copy, tuition receipt, academic record, bank statement (10,000 RMB minimum).",
            
            # Fees & Scholarships
            "tuition fees": "2025 Tuition: Chinese-taught programs 18,000-22,000 RMB/year, English-taught programs 22,000-28,000 RMB/year.",
            
            "scholarships": "Available scholarships: Chinese Government Scholarship, Zhejiang Provincial Scholarship, ZJNU Excellent International Student Scholarship.",
        }
    
    def search(self, question):
        """Simple keyword-based search"""
        question_lower = question.lower()
        
        # Find best matching QA pair
        best_match = None
        best_score = 0
        
        for key, answer in self.qa_pairs.items():
            score = self._calculate_match_score(question_lower, key)
            if score > best_score:
                best_score = score
                best_match = answer
        
        if best_score > 0.3:  # Reasonable match threshold
            return best_match
        else:
            return None
    
    def _calculate_match_score(self, question, key):
        """Calculate how well the question matches a key"""
        question_words = set(question.split())
        key_words = set(key.split())
        
        common_words = question_words.intersection(key_words)
        return len(common_words) / len(key_words) if key_words else 0

# Global instance
simple_handbook = SimpleHandbookService()