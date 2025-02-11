from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import os
import logging

logger = logging.getLogger(__name__)

# Global instance (if needed elsewhere, you can import create_limiter)
limiter_instance = None

def create_limiter(app):
    """
    Attach and create the limiter for the given Flask app.
    Uses Redis if available; otherwise falls back to in-memory storage.
    Disables rate limiting if FLASK_ENV is "testing".
    
    Args:
        app: The Flask app instance.
    
    Returns:
        Limiter: An initialized Flask-Limiter instance.
    """
    global limiter_instance
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
            redis_client = Redis.from_url(redis_url)
            redis_client.ping()
            app.logger.info("Redis is available at %s. Using it for rate limiting.", redis_url)
            storage_uri = redis_url  # Use Redis as the storage backend
        except Exception as e:
            app.logger.warning("Redis not available (%s). Falling back to in-memory storage.", str(e))

    limiter_instance = Limiter(
        key_func=get_remote_address,
        default_limits=["10 per minute"],
        storage_uri=storage_uri,
        enabled=app.config.get("RATELIMIT_ENABLED", True)
    )
    limiter_instance.init_app(app)
    return limiter_instance
