import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY') or 'your-secret-key-here'
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Database (using XAMPP's PHPMyAdmin/MySQL)
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'obituary_platform')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    
    # SEO/Site Settings
    SITE_NAME = "Memorial Obituaries"
    SITE_URL = os.getenv('SITE_URL', 'http://localhost:5000')
    SITE_DESCRIPTION = "A platform to honor and remember loved ones"
    
    # Flask-SQLAlchemy (if using)
    SQLALCHEMY_DATABASE_URI = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    MYSQL_HOST = os.getenv('PROD_MYSQL_HOST', 'localhost')
    # Add production-specific settings here

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}