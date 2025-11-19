

# this script tests the MySQL connection using pymysql, 
# at first I tried to use non-root user (hackathon_user) for database connection instead of root
# but it failed, so I reverted to root user for testing purposes


import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def test_mysql():
    try:
        
        db_url = os.getenv("DATABASE_URL") # mysql+pymysql://hackathon_user:HK2025@localhost/hackathon_team10_db
        
        
        # Parse the URL
        parts = db_url.split('//')[1].split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        
        username = user_pass[0]
        password = user_pass[1]
        host = host_db[0]
        database = host_db[1]
        
        print(f"Testing connection to MySQL...")
        print(f"Host: {host}")
        print(f"User: {username}")
        print(f"Database: {database}")
        
        # Test connection
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )
        
        print("✅ MySQL connection successful!")
        
        # Test if we can query
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Database accessible! Found {len(tables)} tables")
            
        connection.close()
        
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("Please check:")
        print("1. Is MySQL running?")
        print("2. Did you run: CREATE USER 'hackathon_user'@'localhost' IDENTIFIED BY 'HK2025';")
        print("3. Did you run: GRANT ALL PRIVILEGES ON hackathon_team10_db.* TO 'hackathon_user'@'localhost';")

if __name__ == '__main__':
    test_mysql()