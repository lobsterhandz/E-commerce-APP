import jwt
import logging
from datetime import datetime, timezone, timedelta
from flask import request, jsonify, g
from functools import wraps
from config import Config


# Initialize Logger
logger = logging.getLogger(__name__)


# ---------------------------
# Error Response Utility
# ---------------------------
def error_response(message, status_code=400):
    logger.warning(f"Error {status_code}: {message}")
    if Config.DEBUG:
        logger.debug("Traceback:", exc_info=True)
    return jsonify({"error": message}), status_code

# ---------------------------
# JWT Token Handling
# ---------------------------

def encode_token(user_id, role):
    """
    Encodes a JWT token with user_id and role.
    """
    try:
        payload = {
            'exp': datetime.now(timezone.utc) + timedelta(days=Config.TOKEN_EXPIRY_DAYS),
            'iat': datetime.now(timezone.utc),
            'sub': str(user_id),  # Convert user_id to string
            'role': role
        }
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
        logger.info(f"Token generated for user {user_id} with role {role}.")
        logger.debug(f"Token expiration set to: {payload['exp']}")
        return token
    except Exception as e:
        logger.error(f"Token generation error: {str(e)}")
        raise e


def decode_token(token):
    """
    Decodes a JWT token and returns the payload.
    """
    try:
        # Use Config.JWT_SECRET_KEY directly
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token expired.")
        raise Exception("Token expired. Please log in again.")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise Exception("Invalid token. Please log in again.")

# ---------------------------
# JWT Required Decorator
# ---------------------------
def jwt_required(f):
    """
    Decorator to ensure a valid JWT token is present in the request headers.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        logger.debug(f"Authorization header: {token}") # debug token
        if not token:
            return error_response("Token is missing!", 403)
        try:
            token = token.split(" ")[1]  # Remove "Bearer" prefix
            payload = decode_token(token)
            logger.debug(f"Decoded payload: {payload}")
            if isinstance(payload, str):  # Check if payload is an error message
                return error_response(payload, 403)
            g.user = payload  # Attach the payload to Flask's g object for access
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return error_response("Token is invalid!", 403)
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Role-Based Access Control
# ---------------------------

ROLE_HIERARCHY = {
    "user": 1,
    "admin": 2,
    "super_admin": 3,
}

def role_required(required_role):
    """
    Decorator to restrict access based on roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "Token is missing!"}), 403

            try:
                parts = token.split(" ")
                if len(parts) != 2 or parts[0] != "Bearer":
                    return jsonify({"error": "Invalid token format."}), 403
                token = parts[1]
                payload = decode_token(token)
                user_role = payload.get("role")
                
                # Debug logging
                current_app.logger.info(f"🔍 Role check: user role '{user_role}', required '{required_role}'")
                
                if ROLE_HIERARCHY.get(user_role, 0) < ROLE_HIERARCHY.get(required_role, 0):
                    current_app.logger.warning(f"Unauthorized access attempt with role '{user_role}' (required: '{required_role}')")
                    return jsonify({"error": "Unauthorized access!"}), 403
            except Exception as e:
                current_app.logger.error(f"Role validation error: {e}")
                return jsonify({"error": "Token is invalid!"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator



# ---------------------------
# Pagination Helper
# ---------------------------
def paginate(query, page, per_page, schema=None, sort=None):
    """
    Paginates query results with optional sorting and serialization.
    """
    try:
        if sort:
            query = query.order_by(sort)
        items = query.paginate(page, per_page, error_out=False)
        return {
            "items": schema.dump(items.items) if schema else [item.to_dict() for item in items.items],
            "total": items.total,
            "pages": items.pages,
            "page": items.page,
            "per_page": items.per_page
        }
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        raise ValueError("Error paginating results.")

