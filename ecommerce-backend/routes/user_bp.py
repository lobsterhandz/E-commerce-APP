from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.utils import encode_token, role_required, error_response
from utils.limiter import limiter
from flasgger.utils import swag_from
from sqlalchemy.exc import IntegrityError
from schemas.user_schema import user_schema, users_schema
from services.user_service import UserService

# Allowed sortable fields
SORTABLE_FIELDS = ['username', 'created_at']


def create_user_bp(cache):
    """
    Factory function to create the user blueprint with a shared cache instance.
    """
    user_bp = Blueprint('users', __name__)

    # ---------------------------
    # User Registration
    # ---------------------------
    @user_bp.route('/register', methods=['POST'])
    @swag_from({
        "tags": ["Users"],
        "summary": "Register a new user",
        "description": "Registers a new user with username, email, password, and role.",
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "required": True,
                "description": "User registration data including username, email, password, and role.",
                "schema": {
                    "type": "object",
                    "required": ["username", "email", "password", "role"],
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Unique username for the user.",
                            "example": "testuser"
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "Email address for the user.",
                            "example": "testuser@example.com"
                        },
                        "password": {
                            "type": "string",
                            "description": "Password for the user.",
                            "example": "SecurePassword123"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["super_admin", "admin", "user"],
                            "description": "Role of the user.",
                            "example": "user"
                        }
                    }
                }
            }
        ],
        "responses": {
            "201": {
                "description": "User registered successfully.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "username": {"type": "string", "example": "testuser"},
                                "email": {"type": "string", "example": "testuser@example.com"},
                                "role": {"type": "string", "example": "user"},
                                "created_at": {"type": "string", "format": "date-time", "example": "2025-01-01T12:00:00Z"}
                            }
                        }
                    }
                }
            },
            "400": {
                "description": "Validation error or username/email already exists.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string", "example": "Username already exists."}
                            }
                        }
                    }
                }
            },
            "500": {
                "description": "Internal server error.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string", "example": "Unexpected error occurred."}
                            }
                        }
                    }
                }
            }
        }
    })

    def register_user():
        try:
            data = user_schema.load(request.get_json())

            # Check if username or email already exists
            if User.query.filter_by(username=data['username']).first():
                return jsonify({"error": "Username already exists."}), 400
            if User.query.filter_by(email=data['email']).first():
                return jsonify({"error": "Email already exists."}), 400
            new_user = UserService.create_user(**data)
            return jsonify(user_schema.dump(new_user)), 201
        except IntegrityError:
            return jsonify({"error": "Username already exists."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ---------------------------
    # User Login
    # ---------------------------
    @user_bp.route('/login', methods=['POST'])
    @limiter.limit("10 per minute")
    @swag_from({
        "tags": ["Users"],
        "summary": "User login",
        "description": "Authenticates a user and returns a JWT token.",
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "required": True,
                "description": "Login credentials including username and password.",
                "schema": {
                    "type": "object",
                    "required": ["username", "password"],
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "User's username.",
                            "example": "admin"
                        },
                        "password": {
                            "type": "string",
                            "description": "User's password.",
                            "example": "adminpassword"
                        }
                    }
                }
            }
        ],
        "responses": {
            "200": {
                "description": "Login successful with a JWT token.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "token": {
                                    "type": "string",
                                    "description": "JWT token for user authentication.",
                                    "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                                }
                            }
                        }
                    }
                }
            },
            "400": {
                "description": "Validation error.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {
                                    "type": "string",
                                    "example": "Validation error: Missing username or password."
                                }
                            }
                        }
                    }
                }
            },
            "401": {
                "description": "Invalid credentials.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {
                                    "type": "string",
                                    "example": "Invalid username or password."
                                }
                            }
                        }
                    }
                }
            },
            "500": {
                "description": "Internal server error.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {
                                    "type": "string",
                                    "example": "An unexpected error occurred."
                                }
                            }
                        }
                    }
                }
            }
        }
    })

    def login_user():
        """Authenticates a user and generates a JWT token."""
        try:
            data = request.get_json()
            if not data.get('username') or not data.get('password'):
                return error_response("Both username and password are required.", 400)

            user = UserService.authenticate_user(data['username'], data['password'])
            token = encode_token(user.id, user.role)
            return jsonify({"token": token}), 200
        except ValueError as e:
            return error_response(str(e), 401)
        except Exception as e:
            return error_response(str(e), 500)

    # ---------------------------
    # List All Users
    # ---------------------------
    @user_bp.route('', methods=['GET'])
    @cache.cached(query_string=True)
    @limiter.limit("10 per minute")
    @role_required('admin')
    @swag_from({
        "tags": ["Users"],
        "summary": "List all users",
        "description": "Lists all users with pagination and sorting.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "page", "in": "query", "required": False, "schema": {"type": "integer"}, "description": "Page number (default: 1)."},
            {"name": "per_page", "in": "query", "required": False, "schema": {"type": "integer"}, "description": "Items per page (default: 10)."},
            {"name": "sort_by", "in": "query", "required": False, "schema": {"type": "string"}, "description": "Field to sort by."},
            {"name": "sort_order", "in": "query", "required": False, "schema": {"type": "string"}, "description": "Sort order ('asc' or 'desc')."}
        ],
        "responses": {
            "200": {"description": "List of users retrieved successfully."},
            "400": {"description": "Invalid query parameter."},
            "403": {"description": "Unauthorized access."},
            "500": {"description": "Internal server error."}
        }
    })
    def list_users():
        """Lists all users with pagination and sorting."""
        try:
            # Retrieve query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            sort_by = request.args.get('sort_by', 'username', type=str)
            sort_order = request.args.get('sort_order', 'asc', type=str)

            # Validate sorting parameters
            if sort_by not in SORTABLE_FIELDS:
                return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}", 400)
            if sort_order not in ['asc', 'desc']:
                return error_response("Invalid sort_order. Allowed: ['asc', 'desc']", 400)

            # Fetch paginated users
            data = UserService.get_paginated_users(
                page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order
            )

            # Prepare response
            response = {
                "users": users_schema.dump(data["items"]),
                "total": data["total"],
                "pages": data["pages"],
                "page": data["page"],
                "per_page": data["per_page"],
                "sort_by": sort_by,
                "sort_order": sort_order
            }

            return jsonify(response), 200
        except ValueError as e:
            # Handle user-level errors (validation, bad input)
            return error_response(str(e), 400)
        except Exception as e:
            # Handle unexpected errors
            return error_response(f"An unexpected error occurred: {str(e)}", 500)

    # ---------------------------
    # Update User
    # ---------------------------
    @user_bp.route('/<int:user_id>', methods=['PUT'])
    @limiter.limit("5 per minute")
    @role_required('super_admin')
    @swag_from({
        "tags": ["Users"],
        "summary": "Update user details",
        "description": "Updates details of an existing user by their ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
                "description": "ID of the user to update.",
                "example": 1
            },
            {
                "in": "body",
                "name": "body",
                "required": True,
                "description": "Details to update, such as username, email, password, and role.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Updated username for the user.",
                            "example": "new_username"
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "Updated email for the user.",
                            "example": "new_email@example.com"
                        },
                        "password": {
                            "type": "string",
                            "description": "Updated password for the user.",
                            "example": "new_secure_password"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["super_admin", "admin", "user"],
                            "description": "Updated role of the user.",
                            "example": "admin"
                        }
                    },
                    "required": ["username", "email"]  # Specify required fields
                }
            }
        ],
        "responses": {
            "200": {
                "description": "User details updated successfully.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "username": {"type": "string", "example": "new_username"},
                                "email": {"type": "string", "example": "new_email@example.com"},
                                "role": {"type": "string", "example": "admin"},
                                "created_at": {"type": "string", "format": "date-time", "example": "2025-01-21T19:39:24Z"},
                                "updated_at": {"type": "string", "format": "date-time", "example": "2025-01-22T12:34:56Z"}
                            }
                        }
                    }
                }
            },
            "400": {
                "description": "Validation error or invalid input.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string", "example": "Validation error: Missing required fields."}
                            }
                        }
                    }
                }
            },
            "404": {
                "description": "User not found.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string", "example": "User not found."}
                            }
                        }
                    }
                }
            },
            "500": {
                "description": "Internal server error.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string", "example": "An unexpected error occurred."}
                            }
                        }
                    }
                }
            }
        }
    })
    def update_user(user_id):
        """Updates user details."""
        try:
            data = request.get_json()
            updated_user = UserService.update_user(user_id, **data)
            return jsonify(user_schema.dump(updated_user)), 200
        except Exception as e:
            return error_response(str(e), 500)


    # ---------------------------
    # List User by ID
    # ---------------------------
    @user_bp.route('/<int:user_id>', methods=['GET'])
    @jwt_required()
    @role_required('admin')  # Adjust this based on your application's permissions
    @swag_from({
        "tags": ["Users"],
        "summary": "Get user by ID",
        "description": "Fetches details of a user by their ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
                "description": "ID of the user to retrieve."
            }
        ],
        "responses": {
            "200": {
                "description": "User details retrieved successfully.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "username": {"type": "string", "example": "testuser"},
                                "email": {"type": "string", "example": "testuser@example.com"},
                                "role": {"type": "string", "example": "user"},
                                "created_at": {"type": "string", "example": "2025-01-01T12:00:00Z"},
                                "updated_at": {"type": "string", "example": "2025-01-01T12:00:00Z"}
                            }
                        }
                    }
                }
            },
            "404": {"description": "User not found."},
            "500": {"description": "Internal server error."}
        }
    })
    def get_user_by_id(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found."}, 404
            return user_schema.dump(user), 200
        except Exception as e:
            app.logger.error(f"Error fetching user: {str(e)}")
            return {"error": "Internal server error."}, 500
    # ---------------------------
    # Delete User
    # ---------------------------
    @user_bp.route('/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    @role_required('admin')  # Adjust this based on your application's permissions
    @swag_from({
        "tags": ["Users"],
        "summary": "Delete user by ID",
        "description": "Deletes a user from the system using their ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
                "description": "ID of the user to delete."
            }
        ],
        "responses": {
            "200": {
                "description": "User deleted successfully.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string", "example": "User deleted successfully."}
                            }
                        }
                    }
                }
            },
            "404": {"description": "User not found."},
            "500": {"description": "Internal server error."}
        }
    })
    def delete_user(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found."}, 404
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully."}, 200
        except Exception as e:
            app.logger.error(f"Error deleting user: {str(e)}")
            return {"error": "Internal server error."}, 500


    return user_bp
