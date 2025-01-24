from flask_caching import Cache
import logging
import os

# Initialize Logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CacheManager:
    def __init__(self, app=None):
        self.cache_type = os.getenv("CACHE_TYPE", "SimpleCache")
        self.redis_url = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")
        self.cache = Cache()

        if app:
            self.init_app(app)

    def init_app(self, app):
        try:
            if self.cache_type == "RedisCache":
                app.config["CACHE_TYPE"] = "RedisCache"
                app.config["CACHE_REDIS_URL"] = self.redis_url
            else:
                app.config["CACHE_TYPE"] = "SimpleCache"

            # Properly initialize the Cache object with the Flask app
            self.cache.init_app(app)

            if self.cache_type == "RedisCache":
                # Verify Redis connectivity
                self.redis_client = self.cache._client
                self.redis_client.ping()
        except Exception as e:
            # Fallback to SimpleCache
            app.config["CACHE_TYPE"] = "SimpleCache"
            self.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
            self.cache.init_app(app)


    def ping(self):
        """
        Pings the Redis server to ensure it's available.
        Returns True if Redis is available; False otherwise.
        """
        if self.cache_type == "RedisCache" and self.redis_client:
            try:
                return self.redis_client.ping()
            except Exception as e:
                logger.error(f"Redis ping failed: {str(e)}")
                return False
        return False  # SimpleCache doesn't support ping

    def set(self, key, value, timeout=300):
        """
        Sets a value in the cache.

        :param key: Cache key
        :param value: Value to store
        :param timeout: Expiration time in seconds (default: 300 seconds)
        """
        try:
            self.cache.set(key, value, timeout=timeout)
            logger.info("Cache set for key: %s (Timeout: %s seconds)", key, timeout)
        except Exception as e:
            logger.error("Error setting cache for key %s: %s", key, str(e))

    def get(self, key):
        """
        Retrieves a value from the cache.

        :param key: Cache key
        :return: Cached value or None if the key does not exist or has expired
        """
        try:
            value = self.cache.get(key)
            if value is not None:
                logger.info("Cache hit for key: %s", key)
            else:
                logger.info("Cache miss for key: %s", key)
            return value
        except Exception as e:
            logger.error("Error retrieving cache for key %s: %s", key, str(e))
            return None

    def delete(self, key):
        """
        Deletes a key-value pair from the cache.

        :param key: Cache key
        """
        try:
            self.cache.delete(key)
            logger.info("Cache deleted for key: %s", key)
        except Exception as e:
            logger.error("Error deleting cache for key %s: %s", key, str(e))

    def clear(self):
        """
        Clears all data from the cache.
        """
        try:
            self.cache.clear()
            logger.info("Cache cleared.")
        except Exception as e:
            logger.error("Error clearing cache: %s", str(e))
