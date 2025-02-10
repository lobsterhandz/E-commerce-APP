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
        return db_url if db_url else "sqlite:///:memory:"  # ✅ Default to SQLite if missing


    # ✅ Rate Limiting Config (Restored)
    RATELIMIT_DAILY = int(os.getenv("RATELIMIT_DAILY", 200))
    RATELIMIT_HOURLY = int(os.getenv("RATELIMIT_HOURLY", 50))
    RATELIMIT_DEFAULT = f"{RATELIMIT_DAILY} per day; {RATELIMIT_HOURLY} per hour"
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_REDIS_URL", "memory://")
    RATELIMIT_HEADERS_ENABLED = os.getenv("RATELIMIT_HEADERS_ENABLED", "True").lower() in ["true", "1", "yes"]

    # ✅ Caching Configuration (Restored)
    USE_REDIS_CACHE = os.getenv("USE_REDIS_CACHE", "False").lower() in ["true", "1", "yes"]
    CACHE_TYPE = "RedisCache" if USE_REDIS_CACHE else "SimpleCache"  # ✅ Fix: Default to SimpleCache
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")

    if not USE_REDIS_CACHE:
        print("⚠️ Redis is disabled. Using SimpleCache instead.")

    # ✅ Logging Configuration (Restored)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    LOG_ROTATION_BYTES = int(os.getenv("LOG_ROTATION_BYTES", 10 * 1024 * 1024))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

    def __init__(self):
        """Ensure required environment variables are set and configure logging."""
        self._check_required_env_variables()
        if ENV in ["development", "production"]:
            self._configure_logging()

    def _check_required_env_variables(self):
        """Check if required environment variables are set."""
        required_vars = ["SECRET_KEY", "DATABASE_URL", "JWT_SECRET_KEY", "PASSWORD_SALT"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            if ENV == "production":
                raise ValueError(msg)
            else:
                logging.warning(msg)

    def _configure_logging(self):
        """Set up rotating file logging."""
        handler = RotatingFileHandler(
            self.LOG_FILE, maxBytes=self.LOG_ROTATION_BYTES, backupCount=self.LOG_BACKUP_COUNT
        )
        handler.setLevel(logging.getLevelName(self.LOG_LEVEL))
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)


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
