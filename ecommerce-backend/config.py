import os
import json
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from the .env file
load_dotenv()

ENV = os.getenv("FLASK_ENV", "development").lower()

class Config:
    """Base configuration class with shared settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_default_secret")
    PASSWORD_SALT = os.getenv("PASSWORD_SALT", "default_salt")
    TOKEN_EXPIRY_DAYS = int(os.getenv("TOKEN_EXPIRY_DAYS", 7))
    SWAGGER_HOST = os.getenv("SWAGGER_HOST", "localhost:5000")
    SWAGGER_SCHEMES = ["https"] if os.getenv("SWAGGER_SCHEMES", "http") == "https" else ["http"]

    DEBUG = False
    TESTING = False

    try:
        JWT_TOKEN_LOCATION = json.loads(os.getenv("JWT_TOKEN_LOCATION", '["headers"]'))
    except json.JSONDecodeError:
        JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = os.getenv("JWT_HEADER_NAME", "Authorization")
    JWT_HEADER_TYPE = os.getenv("JWT_HEADER_TYPE", "Bearer")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_database_uri():
        db_url = os.getenv("DATABASE_URL", "")
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url if db_url else "sqlite:///:memory:"

    RATELIMIT_DAILY = int(os.getenv("RATELIMIT_DAILY", 200))
    RATELIMIT_HOURLY = int(os.getenv("RATELIMIT_HOURLY", 50))
    RATELIMIT_DEFAULT = f"{RATELIMIT_DAILY} per day; {RATELIMIT_HOURLY} per hour"
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_REDIS_URL", "memory://")
    RATELIMIT_HEADERS_ENABLED = os.getenv("RATELIMIT_HEADERS_ENABLED", "True").lower() in ["true", "1", "yes"]

    USE_REDIS_CACHE = os.getenv("USE_REDIS_CACHE", "False").lower() in ["true", "1", "yes"]
    CACHE_TYPE = "RedisCache" if USE_REDIS_CACHE else "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")

    if not USE_REDIS_CACHE:
        print("⚠️ Redis is disabled. Using SimpleCache instead.")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    LOG_ROTATION_BYTES = int(os.getenv("LOG_ROTATION_BYTES", 10 * 1024 * 1024))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("sqlite:///:memory:")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_ENABLED = False # stop it from being enabled by default
    CACHE_TYPE = "NullCache"  # Disable caching during tests

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()
    
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

def get_config(env_name="development"):
    config_class = config_by_name.get(env_name, DevelopmentConfig)
    return config_class()  # ✅ Now it returns an instance instead of a class

