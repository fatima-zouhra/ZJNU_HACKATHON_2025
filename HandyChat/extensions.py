# extensions.py - ENHANCED EXTENSIONS
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
cors = CORS()

def init_extensions(app):
    """Initialize all extensions with the app"""
    db.init_app(app)
    cors.init_app(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"❌ Database table creation error: {e}")