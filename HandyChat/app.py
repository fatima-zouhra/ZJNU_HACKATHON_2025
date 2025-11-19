from flask import Flask, jsonify, render_template, send_from_directory
from extensions import db, cors
import logging
from datetime import datetime   
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    from config import Config
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app)

    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
           
        except Exception as e:
            print(f"Database table creation error: {e}")

    # Register unified chat
    from routes.unified_chat import unified_chat_bp
    app.register_blueprint(unified_chat_bp, url_prefix='/api/chat')

    # Serve static files
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory('static', filename)

    @app.route('/')
    def home_page():
        return render_template('index.html')

    @app.route('/chat')
    def chat_page():
        return render_template('chat.html')

    @app.route('/signin')
    def signin_page():
        return render_template('student.html')


    @app.route('/signup')
    def signup_page():
        return render_template('signup.html')


    # Health check endpoint (for frontend status)
    @app.route('/health')
    @app.route('/api/health')
    @app.route('/api/chat/health')
    def health_check():
        """Health check endpoint that shows JSON and PDF service status"""
        try:
            from models import SportClass, HandbookCategory
            from services.ai_services import ai_service
            
            sports_count = SportClass.query.count()
            categories_count = HandbookCategory.query.count()
            
            # Check JSON handbook status
            json_status = "unknown"
            json_categories = 0
            json_questions = 0
            try:
                from services.json_handbook_service import json_handbook_service
                json_info = json_handbook_service.get_status()
                json_status = "available" if json_info["loaded"] else "unavailable"
                json_categories = json_info["categories_count"]
                json_questions = json_info["total_questions"]
            except ImportError:
                json_status = "not_configured"
            except Exception as e:
                json_status = f"error: {e}"
            
            # Check PDF service status
            pdf_status = "unknown"
            pdf_has_content = False
            pdf_file_exists = False
            try:
                from services.handbook_pdf_service import get_handbook_status
                pdf_info = get_handbook_status()
                pdf_status = pdf_info.get('status', 'unknown')
                pdf_has_content = pdf_info.get('has_content', False)
                pdf_file_exists = pdf_info.get('file_exists', False)
            except ImportError:
                pdf_status = "not_configured"
            except Exception as e:
                pdf_status = f"error: {e}"
            
            return jsonify({
                "status": "healthy",
                "service": "ZJNU Student Assistant - Unified AI System",
                "timestamp": datetime.now().isoformat(),
                "capabilities": {
                    "pe_classes": True,
                    "handbook": True,
                    "ai_understanding": ai_service.ai_enabled,
                    "bilingual_support": True,
                    "json_handbook": json_status == "available",
                    "pdf_handbook": pdf_status == "available"
                },
                "handbook_services": {
                    "json_handbook": {
                        "status": json_status,
                        "categories": json_categories,
                        "questions": json_questions
                    },
                    "pdf_handbook": {
                        "status": pdf_status,
                        "has_content": pdf_has_content,
                        "file_exists": pdf_file_exists
                    }
                },
                "database": {
                    "sports_classes": sports_count,
                    "handbook_categories": categories_count
                },
                "ai_service": "available" if ai_service.ai_enabled else "disabled"
            })
        except Exception as e:
            return jsonify({
                "status": "degraded",
                "error": str(e),
                "service": "ZJNU Student Assistant",
                "timestamp": datetime.now().isoformat()
            }), 500

    # API info
    @app.route('/api/info')
    def api_info():
        return jsonify({
            "message": "ZJNU Student Assistant - HandyChat API",
            "version": "3.0", 
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "features": [
                "PE Class Information & Locations",
                "University Handbook Policies", 
                "AI-Powered Natural Language Understanding",
                "Bilingual Support (English/Chinese)",
                "Combined Query Handling"
            ],
            "endpoints": {
                "main_chat": "/api/chat/ask (POST)",
                "available_sports": "/api/chat/sports (GET)",
                "health_check": "/health (GET)",
                "question_analysis": "/api/chat/analyze (POST)"
            }
        })

    return app

if __name__ == '__main__':
    app = create_app()
    print("ZJNU Student Assistant started successfully!")
    print("HandyChat system ready")
    print("PE Class System: ✅ ENABLED")
    print("Handbook System: ✅ ENABLED (JSON Primary + PDF Fallback)")
    print("AI Service: ✅ ENABLED")
    print("Bilingual Support: ✅ ENABLED")
    print("Combined Queries: ✅ ENABLED")
    
    # Show handbook service status
    try:
        from services.json_handbook_service import json_handbook_service
        json_status = json_handbook_service.get_status()
        if json_status["loaded"]:
            print(f"JSON Handbook: ✅ LOADED ({json_status['categories_count']} categories, {json_status['total_questions']} questions)")
        else:
            print("JSON Handbook: ❌ NOT LOADED")
    except Exception as e:
        print(f"JSON Handbook: ❌ ERROR - {e}")
    
    print("Server running at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
