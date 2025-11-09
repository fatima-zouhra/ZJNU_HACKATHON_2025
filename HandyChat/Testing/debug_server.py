



from app import create_app
from extensions import db

app = create_app()

print("Starting server in debug mode...")

if __name__ == '__main__':
    try:
        with app.app_context():
            # Test database connection
            print("Testing database connection...")
            result = db.session.execute('SELECT 1')
            print("Database connection successful")
            
            # Test if tables exist
            from models import SportClass
            count = SportClass.query.count()
            print(f"Database tables exist, found {count} sport classes")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("Make sure MySQL is running and your database exists!")
    
    print("Starting Flask server...")
    print("Access: http://localhost:5000")
    print("Chat: http://localhost:5000/chat")
    app.run(debug=True, host='0.0.0.0', port=5000)