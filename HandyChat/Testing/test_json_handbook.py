import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_json_handbook():
    try:
        from services.json_handbook_service import json_handbook_service
        
        print("🧪 Testing JSON Handbook Service...")
        
        # Test 1: Service status
        status = json_handbook_service.get_status()
        print(f"✅ Service Status: {status}")
        
        # Test 2: Search for common questions
        test_questions = [
            "How to apply for visa extension?",
            "What are graduation requirements?",
            "PE class credits",
            "学费多少钱?",
            "奖学金"
        ]
        
        for question in test_questions:
            print(f"\n Testing: '{question}'")
            result = json_handbook_service.search_handbook(question)
            if result["found"]:
                best_match = result["results"][0]
                print(f" Found: {best_match['category']} - {best_match['subcategory']}")
                print(f" Answer preview: {best_match['answer_en'][:100]}...")
            else:
                print("   ❌ No matches found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_json_handbook()
