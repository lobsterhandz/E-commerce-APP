from flask import Blueprint, request, jsonify
from services.customer_account_service import CustomerAccountService
from schemas.customer_account_schema import customer_account_schema, customer_accounts_schema
from utils.utils import error_response, role_required
from flask_jwt_extended import jwt_required
from utils.limiter import limiter
from flasgger.utils import swag_from

SORTABLE_FIELDS = CustomerAccountService.SORTABLE_FIELDS

def create_customer_account_bp(cache):
    """
    Factory function to create the customer accounts blueprint with a shared cache instance.
    """
    customer_account_bp = Blueprint('customer_accounts', __name__)

    # ---------------------------
    # Create a Customer Account
    # ---------------------------
    @customer_account_bp.route('', methods=['POST'])
    @jwt_required()
    @role_required('admin')
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Customer Accounts"],
        "summary": "Create a new customer account",
        "description": "Creates a new customer account in the system.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": ["username", "password", "customer_id"],
                    "properties": {
                        "username": {"type": "string", "description": "Unique username for the account."},
                        "password": {"type": "string", "description": "Password for the account."},
                        "customer_id": {"type": "integer", "description": "Associated customer ID."}
                    }
                }
            }
        ],
        "responses": {
            "201": {"description": "Customer account created successfully."},
            "400": {"description": "Validation or creation error."},
            "500": {"description": "Internal server error."}
        }
    })
    def create_customer_account():
        """Creates a new customer account."""
        try:
            data = request.get_json()
            validated_data = customer_account_schema.load(data)
            account = CustomerAccountService.create_customer_account(**validated_data)
            return jsonify(customer_account_schema.dump(account)), 201
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Get Paginated Customer Accounts
    # ---------------------------
    @customer_account_bp.route('', methods=['GET'])
    @cache.cached(query_string=True)
    @jwt_required()
    @role_required('admin')
    @limiter.limit("10 per minute")
    @swag_from({
        "tags": ["Customer Accounts"],
        "summary": "Retrieve paginated customer accounts",
        "description": "Retrieves a paginated list of customer accounts with optional sorting and metadata.",
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
                "description": "Records per page (default: 10).",
                "example": 10
            },
            {
                "name": "sort_by",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Field to sort by (default: 'username'). Allowed fields: ['username', 'email', 'created_at'].",
                "example": "username"
            },
            {
                "name": "sort_order",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Sorting order ('asc' or 'desc').",
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
                "description": "Successfully retrieved customer accounts.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "customer_accounts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "integer",
                                        "example": 1,
                                        "description": "Unique identifier for the customer account."
                                    },
                                    "username": {
                                        "type": "string",
                                        "example": "johndoe",
                                        "description": "Username of the customer account."
                                    },
                                    "email": {
                                        "type": "string",
                                        "example": "johndoe@example.com",
                                        "description": "Email of the customer account."
                                    },
                                    "created_at": {
                                        "type": "string",
                                        "format": "date-time",
                                        "example": "2025-01-20T10:00:00Z",
                                        "description": "Account creation timestamp."
                                    }
                                }
                            }
                        },
                        "total": {
                            "type": "integer",
                            "example": 100,
                            "description": "Total number of customer accounts."
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

    def get_customer_accounts():
        """Retrieves paginated customer accounts."""
        try:
            # Retrieve and validate query parameters
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)
            sort_by = request.args.get('sort_by', default='username', type=str)
            sort_order = request.args.get('sort_order', default='asc', type=str)
            include_meta = str(request.args.get('include_meta', 'true')).lower() in ['true', '1']

            # Validate query parameters
            if page < 1 or per_page < 1 or per_page > 100:
                return error_response("Invalid pagination parameters.", 400)
            if sort_by not in SORTABLE_FIELDS:
                return error_response(f"Invalid sort_by field. Allowed fields: {', '.join(SORTABLE_FIELDS)}", 400)
            if sort_order not in ['asc', 'desc']:
                return error_response("Invalid sort_order. Allowed values: 'asc' or 'desc'.", 400)

            # Fetch data from the service
            data = CustomerAccountService.get_paginated_accounts(
                page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=include_meta
            )

            # Debug: Check data types before serialization
            for item in data["items"]:
                print(f"Item before serialization: {item}")

            # Build the response
            response = {"customer_accounts": [account.to_dict() for account in data["items"]]}
            if include_meta:
                response.update({k: v for k, v in data.items() if k != "items"})

            return jsonify(response), 200

        except ValueError as e:
            print(f"Validation Error: {e}")
            return error_response(f"Invalid input: {str(e)}", 400)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return error_response(f"An error occurred: {str(e)}", 500)


    # ---------------------------
    # Get/Modify/Delete by ID
    # ---------------------------
    @customer_account_bp.route('/<int:account_id>', methods=['GET'])
    @jwt_required()
    @role_required('admin')
    @limiter.limit("5 per minute")
    @cache.cached(query_string=True)
    @swag_from({
        "tags": ["Customer Accounts"],
        "summary": "Retrieve a customer account by ID",
        "description": "Fetches the details of a specific customer account by ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "account_id", "in": "path", "type": "integer", "required": True, "description": "Account ID."}
        ],
        "responses": {
            "200": {"description": "Customer account retrieved successfully."},
            "404": {"description": "Customer account not found."}
        }
    })
    def get_customer_account(account_id):
        """Handles GET for a customer account."""
        try:
            account = CustomerAccountService.get_customer_account_by_id(account_id)
            if not account:
                return error_response(f"Customer account with ID {account_id} not found.", 404)
            return jsonify(customer_account_schema.dump(account)), 200
        except Exception as e:
            return error_response(f"An error occurred: {str(e)}", 500)

    @customer_account_bp.route('/<int:account_id>', methods=['PUT', 'DELETE'])
    @jwt_required()
    @role_required('admin')
    @limiter.limit("5 per minute")
    @swag_from({
    "tags": ["Customer Accounts"],
    "summary": "Update or delete a customer account",
    "description": "Updates or deletes a customer account by its ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "account_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "Account ID of the customer account to update or delete.",
            "example": 1
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Updated username for the account.",
                        "example": "updated_username"
                    },
                    "email": {
                        "type": "string",
                        "description": "Updated email for the account.",
                        "example": "updated_email@example.com"
                    },
                    "role": {
                        "type": "string",
                        "description": "Updated role for the account.",
                        "example": "user"
                    }
                },
                "required": ["username", "email"]  # Adjust required fields as needed
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Customer account updated or deleted successfully.",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Customer account updated successfully."
                    }
                }
            }
        },
        "404": {
            "description": "Customer account not found.",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Customer account with ID 1 not found."
                    }
                }
            }
        }
    }
})

    def modify_or_delete_customer_account(account_id):
        """Handles PUT and DELETE for a customer account."""
        try:
            if request.method == 'PUT':
                data = request.get_json()
                validated_data = customer_account_schema.load(data, partial=True)
                account = CustomerAccountService.update_customer_account(account_id, **validated_data)
                return jsonify(customer_account_schema.dump(account)), 200
            elif request.method == 'DELETE':
                CustomerAccountService.delete_customer_account(account_id)
                return jsonify({"message": "Customer account deleted successfully"}), 200
        except Exception as e:
            return error_response(f"An error occurred: {str(e)}", 500)

    return customer_account_bp
