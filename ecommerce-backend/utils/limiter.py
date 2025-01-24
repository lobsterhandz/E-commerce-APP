from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import os
import logging

# Initialize Logger
logger = logging.getLogger(__name__)

# Initialize the Limiter
limiter = Limiter(
    key_func=get_remote_address,  # Use the client's IP address for rate limiting
    default_limits=["200 per day", "50 per hour"],  # Default rate limits
)

def limiter_setup(app):
    """
    Attach the limiter to the app with Redis validation.
    Args:
        app: The Flask app instance.
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")  # Default Redis URL
    try:
        # Test Redis connection
        redis_client = Redis.from_url(redis_url)
        redis_client.ping()
        app.logger.info("Redis is available at %s. Rate limiting enabled.", redis_url)
    except Exception as e:
        app.logger.warning("Redis not available (%s). Falling back to in-memory storage.", str(e))
        limiter.storage_uri = None  # Switch to in-memory storage
    limiter.init_app(app)
