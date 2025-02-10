import os
import json
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from the .env file
load_dotenv()

# Determine the current environment
ENV = os.getenv("FLASK_ENV", "development").lower()


class Config:
    """Base configuration class with shared settings."""

    # General Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_default_secret")
    PASSWORD_SALT = os.getenv("PASSWORD_SALT", "default_salt")
    TOKEN_EXPIRY_DAYS = int(os.getenv("TOKEN_EXPIRY_DAYS", 7))
    SWAGGER_HOST = os.getenv("SWAGGER_HOST", "localhost:5000")  # ✅ Default to localhost if missing
    SWAGGER_SCHEMES = ["https"] if os.getenv("SWAGGER_SCHEMES", "http") == "https" else ["http"]
    DEBUG = False
    TESTING = False

    # JWT Configuration
    try:
        JWT_TOKEN_LOCATION = json.loads(os.getenv("JWT_TOKEN_LOCATION", '["headers"]'))
    except json.JSONDecodeError:
        JWT_TOKEN_LOCATION = ["headers"]  # Fallback to default if parsing fails
    JWT_HEADER_NAME = os.getenv("JWT_HEADER_NAME", "Authorization")
    JWT_HEADER_TYPE = os.getenv("JWT_HEADER_TYPE", "Bearer")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_database_uri():
        """Return database URI based on environment."""
        db_url = os.getenv("DATABASE_URL", "")
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)  # Fix for SQLAlchemy 1.4+
        return db_url if db_url else "sqlite:///:memory:"  # Default to SQLite if missing


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Enable SQL logging for debugging
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "NullCache"  # Disable caching during tests


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()


# Map configurations by name
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name="development"):
    """Retrieve the appropriate configuration class based on the environment."""
    return config_by_name.get(env_name, DevelopmentConfig)
