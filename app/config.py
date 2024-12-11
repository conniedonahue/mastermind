import os
from dotenv import load_dotenv

environment = os.getenv("FLASK_ENV", "development")
env_file = f".env.{environment}"
load_dotenv(env_file, override=True)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_key")
    SESSION_TIMEOUT = 3600  
    ENV = os.getenv("FLASK_ENV", "development")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

 

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    

class ProductionConfig(Config):
    DEBUG = False
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")  

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SESSION_TIMEOUT = 1800  # 30 minutes for testing
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  

