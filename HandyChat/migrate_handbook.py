
import json
import os
import re

def extract_keywords(question):
    """Extract important keywords from question"""
    stop_words = {'how', 'can', 'i', 'what', 'when', 'where', 'why', 'the', 'a', 'an', 'to', 'for', 'is', 'are', 'do', 'does', 'my', 'me'}
    words = re.findall(r'\w+', question.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    return list(set(keywords))[:8]  # Return top 8 unique keywords

def generate_variations(question):
    """Generate common variations of the question"""
    variations = []
    question_lower = question.lower()
    
    # Simple variations
    if "how can i" in question_lower:
        variations.append(question.replace("How can I", "How to"))
        variations.append(question.replace("How can I", "What is the process to"))
    
    if "what are" in question_lower:
        variations.append(question.replace("What are", "What is"))
    
    if "when should" in question_lower:
        variations.append(question.replace("When should", "When do I need to"))
    
    # Chinese variations
    if "如何" in question:
        variations.append(question.replace("如何", "怎样"))
    
    return variations

def migrate_handbook():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    handbook_path = os.path.join(current_dir,  "static", "handbook", "handbook_2025.json")
    output_path = os.path.join(current_dir, "static", "handbook", "handbook_optimized.json")
    
    print(f"📁 Loading handbook from: {handbook_path}")
    
    try:
    
        with open(handbook_path, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        
        optimized_data = {
            "qa_pairs": [],
            "metadata": {
                "total_questions": 0,
                "last_updated": "2025-01-01", 
                "version": "2.0",
                "source": "handbook_2025.json"
            }
        }
        
        question_id = 1
        
        for category in current_data:
            print(f"📂 Processing category: {category['category']}")
            
            for subcat in category.get("subcategories", []):
                print(f"  📝 Processing subcategory: {subcat['title']}")
                
                for qa in subcat.get("questions", []):
                    question_en = qa.get("question_en", "")
                    if not question_en:  # Skip if no English question
                        continue
                        
                    # Extract keywords from question
                    keywords = extract_keywords(question_en)
                    
                    # Generate variations
                    variations = generate_variations(question_en)
                    
                    optimized_qa = {
                        "id": f"q{question_id:03d}",
                        "question_en": question_en,
                        "question_zh": qa.get("question_zh", ""),
                        "answer_en": qa.get("answer_en", ""),
                        "answer_zh": qa.get("answer_zh", ""),
                        "category": category["category"],
                        "subcategory": subcat["title"],
                        "keywords": keywords,
                        "variations": variations,
                        "attachments": qa.get("attachments", []),
                        "priority": 1
                    }
                    
                    optimized_data["qa_pairs"].append(optimized_qa)
                    question_id += 1
        
        optimized_data["metadata"]["total_questions"] = len(optimized_data["qa_pairs"])
        
        # Save optimized version
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(optimized_data, f, ensure_ascii=False, indent=2)
        
        print(f"SUCCESS: Migrated {len(optimized_data['qa_pairs'])} questions to optimized format")
        print(f"Output file: {output_path}")
        
        # Show sample of migrated data
        print("\nSample migrated questions:")
        for i, qa in enumerate(optimized_data["qa_pairs"][:3]):
            print(f" {i+1}. {qa['question_en'][:60]}...")
            print(f"Keywords: {qa['keywords']}")
            print(f"Variations: {qa['variations']}")
            print()
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_handbook()