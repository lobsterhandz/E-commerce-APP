import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger
from sqlalchemy import text
from flask_jwt_extended import JWTManager

from models import db
from config import config_by_name
from utils.limiter import create_limiter
from utils.caching import CacheManager
from routes import (
    create_customer_bp,
    create_customer_account_bp,
    create_product_bp,
    create_order_bp,
    create_order_item_bp,
    create_shopping_cart_bp,
    create_shopping_cart_item_bp,
    create_user_bp,
    create_category_bp,
)

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

# Initialize CacheManager globally
cache_manager = CacheManager()

def setup_logging(app):
    """Set up logging for the application."""
    if not app.debug and not app.testing:
        os.makedirs("logs", exist_ok=True)
        file_handler = RotatingFileHandler("logs/ecommerce.log", maxBytes=10240, backupCount=10)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("E-Commerce Application Startup")

def validate_configuration(app):
    """Validate critical application configurations."""
    required_keys = ["SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "JWT_SECRET_KEY"]
    missing_keys = [key for key in required_keys if not app.config.get(key)]
    if missing_keys:
        app.logger.error(f"Missing configuration keys: {', '.join(missing_keys)}")
        raise RuntimeError(f"Application misconfigured: {', '.join(missing_keys)}")

def create_app(config_name="development", *args, **kwargs):
    """
    Factory function to create and configure the Flask application.
    
    Args:
        config_name (str): Configuration name ('development', 'testing', 'production').
    
    Returns:
        Flask: Configured Flask application.
    """
    config_name = config_name or os.getenv("FLASK_CONFIG", "development")
    app = Flask(__name__)
    # Ensure config_by_name is correctly referenced
    if isinstance(config_by_name, dict) and config_name in config_by_name:
        app.config.update(config_by_name[config_name])  # Correct way to load dict config
    else:
        raise ValueError(f"Invalid configuration name: {config_name}")

    print(f"SWAGGER_HOST: {app.config.get('SWAGGER_HOST')}")  # Debug

    # Initialize rate limiter
    create_limiter(app)

    # Enable CORS
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    cache_manager.init_app(app)
    JWTManager(app)

    # Setup and validate configuration
    validate_configuration(app)
    setup_logging(app)

    # Swagger Configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/swagger.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/",
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "E-Commerce API",
            "description": "API documentation for managing e-commerce operations.",
            "version": "1.0.0",
        },
        "host": app.config.get("SWAGGER_HOST", "localhost:5000"),
        "basePath": "/",
        "schemes": ["http"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'",
            }
        },
        "security": [{"Bearer": []}],
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Register blueprints
    app.register_blueprint(create_customer_bp(cache_manager.cache, app.limiter), url_prefix="/customers")
    app.register_blueprint(create_customer_account_bp(cache_manager.cache, app.limiter), url_prefix="/customer_accounts")
    app.register_blueprint(create_product_bp(cache_manager.cache, app.limiter), url_prefix="/products")
    app.register_blueprint(create_order_bp(cache_manager.cache, app.limiter), url_prefix="/orders")
    app.register_blueprint(create_order_item_bp(cache_manager.cache, app.limiter), url_prefix="/order_items")
    app.register_blueprint(create_shopping_cart_bp(cache_manager.cache, app.limiter), url_prefix="/shopping_cart")
    app.register_blueprint(create_shopping_cart_item_bp(cache_manager.cache, app.limiter), url_prefix="/shopping_cart_items")
    app.register_blueprint(create_user_bp(cache_manager.cache, app.limiter), url_prefix="/users")
    app.register_blueprint(create_category_bp(cache_manager.cache, app.limiter), url_prefix="/categories")

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        health_status = {"status": "healthy", "details": {}}
        try:
            db.session.execute(text("SELECT 1"))
            health_status["details"]["database"] = "connected"
        except Exception as e:
            app.logger.error(f"Database health check failed: {str(e)}")
            health_status["status"] = "unhealthy"
            health_status["details"]["database"] = str(e)
        try:
            if cache_manager.cache_type == "RedisCache":
                redis_connected = cache_manager.cache and cache_manager.cache.ping()
                health_status["details"]["redis"] = "connected" if redis_connected else "not connected"
            else:
                health_status["details"]["redis"] = "SimpleCache fallback in use"
        except Exception as e:
            app.logger.warning(f"Redis health check failed: {str(e)}")
            health_status["status"] = "unhealthy"
            health_status["details"]["redis"] = str(e)
        return jsonify(health_status), 200 if health_status["status"] == "healthy" else 500

    @app.route('/routes', methods=['GET'])
    def list_routes():
        """Lists all routes in the application for debugging."""
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            output.append(f"{rule.endpoint}: {rule.rule} [{methods}]")
        return jsonify(output)

    # Unified Error Handlers
    def generate_error_response(message, status_code):
        return jsonify({"error": message}), status_code

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"404 Error: {request.url}")
        return generate_error_response("Not Found", 404)

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 Error: {str(error)}")
        return generate_error_response("Internal Server Error", 500)

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        app.logger.warning(f"Rate limit exceeded: {request.url}")
        return generate_error_response("Rate limit exceeded", 429)

    return app

if __name__ == "__main__":
    config_name = os.getenv("FLASK_CONFIG", "development")
    app = create_app(config_name)
    app.run(debug=(config_name == "development"), host="0.0.0.0", port=5000)
