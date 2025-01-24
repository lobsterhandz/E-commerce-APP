from flask import Blueprint, request, jsonify
from services.customer_service import CustomerService
from schemas.customer_schema import customer_schema, customers_schema
from utils.utils import error_response, role_required
from flask_jwt_extended import jwt_required
from utils.limiter import limiter
from flasgger.utils import swag_from

# Allowed sortable fields
SORTABLE_FIELDS = ['name', 'email', 'phone']

def create_customer_bp(cache):
    """
    Factory function to create the customers blueprint with dependency injection for cache.
    """
    customer_bp = Blueprint('customers', __name__)

    # ---------------------------
    # Create a Customer
    # ---------------------------
    @customer_bp.route('', methods=['POST'])
    @jwt_required()
    @role_required('admin')
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Customers"],
        "summary": "Create a new customer",
        "description": "Creates a new customer in the system.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": ["name", "email", "phone"],
                    "properties": {
                        "name": {"type": "string", "description": "Customer's name."},
                        "email": {"type": "string", "description": "Customer's email."},
                        "phone": {"type": "string", "description": "Customer's phone number."}
                    }
                }
            }
        ],
        "responses": {
            "201": {"description": "Customer created successfully."},
            "400": {"description": "Validation or creation error."},
            "500": {"description": "Internal server error."}
        }
    })
    def create_customer():
        """Creates a new customer."""
        try:
            data = request.get_json()
            validated_data = customer_schema.load(data)
            customer = CustomerService.create_customer(**validated_data)
            return jsonify(customer_schema.dump(customer)), 201
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Get Paginated Customers
    # ---------------------------
    @customer_bp.route('', methods=['GET'])
    @cache.cached(query_string=True)
    @jwt_required()
    @role_required('admin')
    @limiter.limit("10 per minute")
    @swag_from({
        "tags": ["Customers"],
        "summary": "Retrieve paginated customers",
        "description": "Retrieves a paginated list of customers with optional sorting and metadata.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "required": False,
                "description": "Page number (default: 1).",
                "example": 1
            },
            {
                "name": "per_page",
                "in": "query",
                "type": "integer",
                "required": False,
                "description": "Items per page (default: 10).",
                "example": 10
            },
            {
                "name": "sort_by",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Field to sort by (default: 'name'). Allowed fields: ['name', 'email', 'created_at'].",
                "example": "name"
            },
            {
                "name": "sort_order",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Sort order ('asc' or 'desc').",
                "example": "asc"
            },
            {
                "name": "include_meta",
                "in": "query",
                "type": "boolean",
                "required": False,
                "description": "Include metadata in the response (default: true).",
                "example": True
            }
        ],
        "responses": {
            "200": {
                "description": "Successfully retrieved customers.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "customers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "integer",
                                        "example": 1,
                                        "description": "Unique identifier for the customer."
                                    },
                                    "name": {
                                        "type": "string",
                                        "example": "John Doe",
                                        "description": "Name of the customer."
                                    },
                                    "email": {
                                        "type": "string",
                                        "example": "johndoe@example.com",
                                        "description": "Email address of the customer."
                                    },
                                    "created_at": {
                                        "type": "string",
                                        "format": "date-time",
                                        "example": "2025-01-20T10:00:00Z",
                                        "description": "Timestamp of when the customer was created."
                                    }
                                }
                            }
                        },
                        "total": {
                            "type": "integer",
                            "example": 100,
                            "description": "Total number of customers."
                        },
                        "pages": {
                            "type": "integer",
                            "example": 10,
                            "description": "Total number of pages."
                        },
                        "page": {
                            "type": "integer",
                            "example": 1,
                            "description": "Current page number."
                        },
                        "per_page": {
                            "type": "integer",
                            "example": 10,
                            "description": "Number of records per page."
                        }
                    }
                }
            },
            "400": {"description": "Invalid parameters."},
            "500": {"description": "Internal server error."}
        }
    })

    def get_customers():
        """Retrieves paginated customers."""
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)
            sort_by = request.args.get('sort_by', default='name', type=str)
            sort_order = request.args.get('sort_order', default='asc', type=str)
            include_meta = request.args.get('include_meta', default='true').lower() == 'true'

            if page < 1 or per_page < 1 or per_page > 100:
                return error_response("Invalid pagination parameters.", 400)
            if sort_by not in SORTABLE_FIELDS:
                return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}", 400)

            data = CustomerService.get_paginated_customers(
                page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=include_meta
            )

            response = {"customers": customers_schema.dump(data["items"])}
            if include_meta:
                response.update({k: v for k, v in data.items() if k != "items"})

            return jsonify(response), 200
        except Exception as e:
            return error_response(str(e), 500)

    # ---------------------------
    # Get Customer by ID
    # ---------------------------
    @customer_bp.route('/<int:customer_id>', methods=['GET'])
    @cache.cached()
    @jwt_required()
    @role_required('admin')
    @limiter.limit("10 per minute")
    @swag_from({
        "tags": ["Customers"],
        "summary": "Retrieve a customer by ID",
        "description": "Fetches a customer's details by their ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "customer_id", "in": "path", "type": "integer", "required": True, "description": "Customer ID."}
        ],
        "responses": {
            "200": {"description": "Customer retrieved successfully."},
            "404": {"description": "Customer not found."}
        }
    })
    def get_customer(customer_id):
        """Fetches a customer by ID."""
        try:
            customer = CustomerService.get_customer_by_id(customer_id)
            return jsonify(customer_schema.dump(customer)), 200
        except Exception as e:
            return error_response(str(e), 404)

    # ---------------------------
    # Update Customer
    # ---------------------------
    @customer_bp.route('/<int:customer_id>', methods=['PUT'])
    @jwt_required()
    @role_required('admin')
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Customers"],
        "summary": "Update a customer",
        "description": "Updates a customer's details by their ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "customer_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "Customer ID.",
                "example": 1
            }
        ],
        "requestBody": {  # OpenAPI 3.0 style for body parameters
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the customer.",
                                "example": "John Doe"
                            },
                            "email": {
                                "type": "string",
                                "description": "Email address of the customer.",
                                "example": "johndoe@example.com"
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number of the customer.",
                                "example": "+1234567890"
                            }
                        },
                        "required": ["name", "email"]  # Specify required fields as needed
                    }
                }
            }
        },
        "responses": {
            "200": {
                "description": "Customer updated successfully.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Customer updated successfully."
                        }
                    }
                }
            },
            "400": {
                "description": "Validation error.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Validation error occurred."
                        }
                    }
                }
            },
            "404": {
                "description": "Customer not found.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Customer with ID 1 not found."
                        }
                    }
                }
            }
        }
    })

    def update_customer(customer_id):
        """Updates a customer by ID."""
        try:
            data = request.get_json()
            validated_data = customer_schema.load(data, partial=True)
            customer = CustomerService.update_customer(customer_id, **validated_data)
            return jsonify(customer_schema.dump(customer)), 200
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Delete Customer
    # ---------------------------
    @customer_bp.route('/<int:customer_id>', methods=['DELETE'])
    @jwt_required()
    @role_required('admin')
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Customers"],
        "summary": "Delete a customer",
        "description": "Deletes a customer by their unique ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "customer_id", "in": "path", "type": "integer", "required": True, "description": "Customer ID."}
        ],
        "responses": {
            "200": {"description": "Customer deleted successfully."},
            "404": {"description": "Customer not found."}
        }
    })
    def delete_customer(customer_id):
        """Deletes a customer by ID."""
        try:
            CustomerService.delete_customer(customer_id)
            return jsonify({"message": "Customer deleted successfully"}), 200
        except Exception as e:
            return error_response(str(e), 404)

    return customer_bp
