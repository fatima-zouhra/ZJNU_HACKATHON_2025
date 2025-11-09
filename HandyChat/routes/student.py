from flask import Blueprint, request, jsonify
from models import ClassInfo
from extensions import db

student_bp = Blueprint("student", __name__)

@student_bp.route("/query", methods=["POST"])
def query_class():
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400
        
        question = data.get("question", "").strip()
        
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400
        
        # Extract sport using AI
        sport = extract_sport_from_question(question)
        
        if not sport:
            return jsonify({
                "error": "Could not identify a sport from your question. Try: 'Where is basketball?', 'Swimming class location', etc.",
                "available_sports": ["basketball", "swimming", "badminton", "ping pong", "tennis", "soccer", "volleyball"]
            }), 400
        
        # Find class information
        class_info = ClassInfo.query.filter(ClassInfo.sport.ilike(f"%{sport}%")).first()
        
        if not class_info:
            return jsonify({
                "error": f"Sorry, no {sport} class found in the current schedule.",
                "sport_asked": sport
            }), 404
        
        # Build response
        result = {
            "sport": class_info.sport,
            "location": {
                "building": class_info.location.building,
                "floor": class_info.location.floor,
                "map_url": class_info.location.map_url,
                "photo_url": class_info.location.photo_url
            },
            "teacher": {
                "name": class_info.teacher.name,
                "contact": class_info.teacher.contact
            },
            "question_asked": question
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@student_bp.route("/sports", methods=["GET"])
def get_available_sports():
    """Get list of all available sports"""
    try:
        sports = db.session.query(ClassInfo.sport).distinct().all()
        sport_list = [sport[0] for sport in sports]
        
        return jsonify({
            "sports": sport_list
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500