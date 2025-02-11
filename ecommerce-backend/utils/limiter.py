from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import os
import logging

# Initialize Logger
logger = logging.getLogger(__name__)

def limiter_setup(app):
    """
    Attach the limiter to the Flask app. Tries to use Redis for storage; if Redis is not available,
    it falls back to in-memory storage.

    Args:
        app: The Flask app instance.
    """
    # Disable rate limiting in testing environment
    if os.getenv("FLASK_ENV") == "testing":
        app.config["RATELIMIT_ENABLED"] = False
    else:
        app.config["RATELIMIT_ENABLED"] = True

    # Default to in-memory storage
    storage_uri = "memory://"

    if app.config.get("RATELIMIT_ENABLED", True):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            # Try to create a Redis client and ping to test connection
            redis_client = Redis.from_url(redis_url)
            redis_client.ping()
            app.logger.info("Redis is available at %s. Rate limiting enabled.", redis_url)
            storage_uri = redis_url  # Use Redis as the storage backend
        except Exception as e:
            app.logger.warning("Redis not available (%s). Falling back to in-memory storage.", str(e))

    # Initialize the Limiter
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["10 per minute"],  # Adjust limit as needed
        storage_uri=storage_uri,
        enabled=app.config.get("RATELIMIT_ENABLED", True)
    )
    limiter.init_app(app)
    return limiter
