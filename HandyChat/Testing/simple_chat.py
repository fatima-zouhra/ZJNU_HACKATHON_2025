

#======== Simplified version for unified_chat.py  FOR TESTING ========#


from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/chat/ask', methods=['POST'])
def simple_ask():
    try:
        data = request.get_json()
        question = data.get('question', '').lower()
        
        # Simple sport detection
        sports = {
            'basketball': {'location': 'Main Gym', 'building': 'Sports Complex'},
            'swimming': {'location': 'Swimming Pool', 'building': 'Aquatics Center'},
            'tennis': {'location': 'Tennis Courts', 'building': 'Outdoor Complex'}
        }
        
        detected_sport = None
        for sport in sports:
            if sport in question:
                detected_sport = sport
                break
        
        if detected_sport:
            return jsonify({
                "response": f"Your {detected_sport} class is at {sports[detected_sport]['location']} ({sports[detected_sport]['building']})",
                "sport": detected_sport,
                "status": "success",
                "location_details": sports[detected_sport]
            })
        else:
            return jsonify({
                "response": "Please mention a sport like basketball, swimming, or tennis",
                "status": "clarify_needed",
                "available_sports": list(sports.keys())
            })
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/')
def home():
    return jsonify({"message": "Simple Find My PE Class API", "status": "running"})

if __name__ == '__main__':
    print("🚀 Starting SIMPLE Find My PE Class API...")
    app.run(debug=True, port=5001)