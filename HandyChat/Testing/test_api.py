

# Testing script for the API

import requests
import json

def test_api(port=5001):
    base_url = f"http://localhost:{port}"
    
    print(f"🧪 Testing Find My PE Class API on port {port}...")
    
    try:
        # Test 1: Home endpoint
        print("\n1. Testing home endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 2: Chat ask endpoint
        print("\n2. Testing chat ask endpoint...")
        test_questions = [
            "Where is basketball class?",
            "游泳课在哪里？",
            "tennis",
            "basketball"
        ]
        # Iterate through test questions and print responses 
        for question in test_questions:
            print(f"Question: '{question}'")
            response = requests.post(
                f"{base_url}/api/chat/ask",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            try: # Try to parse JSON response safely 
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except Exception as e:
                print(f"❌ JSON Error: {e}")
                print(f"Raw response: {response.text[:500]}...")
            print("   " + "-" * 50)
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server. Make sure it's running on {base_url}")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_api(5001)  