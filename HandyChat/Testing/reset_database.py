import pymysql
from app import create_app
from extensions import db

def drop_database_manually():
    """Manually drop the database if SQLAlchemy can't"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='6730875Fz',
            charset='utf8mb4'
        )
        
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("DROP DATABASE IF EXISTS hackathon_team10_db")
                cursor.execute("CREATE DATABASE hackathon_team10_db")
                print("Database recreated manually")
    
    except Exception as e:
        print(f"❌ Manual database reset failed: {e}")

def simple_reset():
    app = create_app()
    
    with app.app_context():
        try:
            # First try to drop all tables
            print("Attempting to drop tables...")
            db.drop_all()
            print("Tables dropped")
            
        except Exception as e:
            print(f"Drop tables failed: {e}")
            print("Trying manual database reset...")
            drop_database_manually()
        
        try:
            # Create all tables
            print("Creating tables...")
            db.create_all()
            print("Tables created successfully")
            
            # Create sample PE data only (skip handbook for now)
            from HandyChat.Testing.create_sample_data import create_sample_data
            create_sample_data()
            print("Sample PE data created")
            
            print("🎉Reset complete! You can now start the server.")
            
        except Exception as e:
            print(f"❌ Error during creation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    simple_reset()