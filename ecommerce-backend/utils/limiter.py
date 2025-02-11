from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import os
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# We'll create and return the limiter instance via create_limiter().

def create_limiter(app):
    """
    Attach and create the limiter for the given Flask app.
    Uses Redis if available; otherwise falls back to in-memory storage.
    Disables rate limiting if the app is in testing mode.
    
    Args:
        app: The Flask app instance.
    
    Returns:
        Limiter: An initialized Flask-Limiter instance.
    """
    # Disable rate limiting in testing environment, regardless of FLASK_ENV
    if app.config.get("TESTING", False):
        app.config["RATELIMIT_ENABLED"] = False
    else:
        # Otherwise, use environment variable or default to True
        app.config["RATELIMIT_ENABLED"] = os.getenv("RATELIMIT_ENABLED", "True").lower() in ["true", "1", "yes"]

    # Default to in-memory storage
    storage_uri = "memory://"

    if app.config.get("RATELIMIT_ENABLED", True):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            # Try to create a Redis client and ping to test connection
            redis_client = Redis.from_url(redis_url)
            redis_client.ping()
            app.logger.info("Redis is available at %s. Using it for rate limiting.", redis_url)
            storage_uri = redis_url  # Use Redis as the storage backend
        except Exception as e:
            app.logger.warning("Redis not available (%s). Falling back to in-memory storage.", str(e))

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["10 per minute"],
        storage_uri=storage_uri,
        enabled=app.config.get("RATELIMIT_ENABLED", True)
    )
    limiter.init_app(app)
    return limiter
