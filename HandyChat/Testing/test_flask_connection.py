from app import create_app
from models import db

app = create_app()

with app.app_context():
    try:
        print("Testing Flask + MySQL connection...")
        
        # Test basic connection
        result = db.session.execute('SELECT 1')
        print("Flask can connect to MySQL!")
        
        # Check current database
        result = db.session.execute('SELECT DATABASE()')
        current_db = result.fetchone()[0]
        print(f"Connected to database: {current_db}")
        
    except Exception as e:
        print(f"❌ Error: {e}")