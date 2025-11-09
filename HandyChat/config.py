

#========================================================#
# this file contains configuration settings for the HandyChat application
# including database connection details and OpenAI API key
# it uses environment variables if available, otherwise defaults are provided
#========================================================#
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'zjnu-student-assistant-secret-2025'
    
    # Database configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '6730875Fz'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'hackathon_team10_db'
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')