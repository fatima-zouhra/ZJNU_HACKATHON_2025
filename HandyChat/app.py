
# -------------------------------------------------------------
# HandyChat Application Setup
#
# This file is the starting point of the HandyChat web app.
#
# 1. It creates and configures the Flask application
#    - Flask is the framework used to run the web app.
#    - This part sets basic settings like security keys,
#      debug mode, and database details.
#
# 2. It connects the app to the MySQL database
#    - The connection uses a specific user (not root)
#      to keep the database secure.
#    - This lets the app read, save, and update data safely.
#
# 3. It registers different app sections (called blueprints)
#    - Each blueprint handles one feature of the app,
#      such as login, chat, or admin pages.
#    - This helps keep the project organized and easier to manage.
#
# 4. It defines simple routes like:
#    - The main or home page (where users first land)
#    - A health check route that shows the app is running properly
#
# In short:
# This file brings everything together—settings, database,
# routes, and features—so the HandyChat app can run smoothly.
# -------------------------------------------------------------


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
            
            # Initialize handbook data
            try:
                from services.handbook_db_service import handbook_db_service
                handbook_db_service.initialize_handbook_data()
                print("Handbook data initialized")
            except Exception as e:
                print(f"Handbook data warning: {e}")
                print("Continuing with AI-powered handbook responses...")
            
        except Exception as e:
            print(f"Database table creation error: {e}")

    # Register unified chat
    from routes.unified_chat import unified_chat_bp
    app.register_blueprint(unified_chat_bp, url_prefix='/api/chat')

    # Serve static files
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory('static', filename)

    # Serve frontend
    @app.route('/')
    def chat_frontend():
        return render_template('chat.html')

    # Health check endpoint (for frontend status)
    @app.route('/health')
    @app.route('/api/health')
    @app.route('/api/chat/health')
    def health_check():
        """Health check endpoint that shows PDF service status"""
        try:
            from models import SportClass, HandbookCategory
            from services.ai_services import ai_service
            
            sports_count = SportClass.query.count()
            categories_count = HandbookCategory.query.count()
            
            # Check PDF service status
            pdf_status = "unknown"
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
                    "pdf_handbook": pdf_status == "available"
                },
                "pdf_service": {
                    "status": pdf_status,
                    "has_content": pdf_has_content if 'pdf_has_content' in locals() else False,
                    "file_exists": pdf_file_exists if 'pdf_file_exists' in locals() else False
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
    print("Handbook System: ✅ ENABLED (AI-Powered)")
    print("AI Service: ✅ ENABLED")
    print("Bilingual Support: ✅ ENABLED")
    print("Combined Queries: ✅ ENABLED")
    print("Server running at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)