
import requests
import json

def test_endpoints():
    base_url = "http://localhost:5000"
    
    print("Testing API endpoints...")
    
    # Test 1: Home endpoint
    print("\n1. Testing home endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Sports endpoint
    print("\n2. Testing sports endpoint...")
    try:
        response = requests.get(f"{base_url}/api/chat/sports")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Chat endpoint
    print("\n3. Testing chat endpoint...")
    try:
        payload = {"question": "Where is basketball today?"}
        response = requests.post(
            f"{base_url}/api/chat/ask",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints()