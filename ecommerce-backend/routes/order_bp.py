from flask import Blueprint, request, jsonify
from services.order_service import OrderService
from schemas.order_schema import order_schema, orders_schema
from utils.utils import error_response, role_required, jwt_required
from utils.limiter import limiter
from flasgger.utils import swag_from

# Allowed sortable fields
SORTABLE_FIELDS = ['created_at', 'quantity', 'total_price']

def create_order_bp(cache):
    """
    Factory function to create the <blueprint_name> blueprint with a shared cache instance.
    """
    order_bp = Blueprint("orders", __name__)
    # ---------------------------
    # Create an Order
    # ---------------------------
    @order_bp.route('', methods=['POST'])
    @limiter.limit("5 per minute")  # Rate limiting
    @jwt_required  # Requires valid JWT token
    @role_required('user')  # Restrict to 'user' role
    @swag_from({
        "tags": ["Orders"],
        "summary": "Create a new order",
        "description": "Creates a new order with the specified details.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": ["customer_id", "product_id", "quantity"],
                    "properties": {
                        "customer_id": {"type": "integer", "description": "ID of the customer placing the order."},
                        "product_id": {"type": "integer", "description": "ID of the product being ordered."},
                        "quantity": {"type": "integer", "description": "Quantity of the product ordered."}
                    }
                }
            }
        ],
        "responses": {
            "201": {"description": "Order created successfully."},
            "400": {"description": "Validation or creation error."},
            "500": {"description": "Internal server error."}
        }
    })
    def create_order():
        """
        Creates a new order.
        """
        try:
            data = request.get_json()
            validated_data = order_schema.load(data)
            order = OrderService.create_order(**validated_data)
            return jsonify(order_schema.dump(order)), 201
        except Exception as e:
            return error_response(str(e))
    
    # ---------------------------
    # Get Paginated Orders
    # ---------------------------
    @order_bp.route('', methods=['GET'])
    @cache.cached(query_string=True)  # Cache GET requests with query parameters
    @limiter.limit("10 per minute")  # Rate limiting
    @jwt_required  # Requires valid JWT token
    @role_required('admin')  # Admin-only access
    @swag_from({
        "tags": ["Orders"],
        "summary": "Retrieve paginated orders",
        "description": "Retrieves paginated orders with optional sorting and metadata.",
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
                "description": "Records per page (default: 10, max: 100).",
                "example": 10
            },
            {
                "name": "sort_by",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Field to sort by (default: 'created_at'). Allowed fields: ['created_at', 'status', 'total'].",
                "example": "created_at"
            },
            {
                "name": "sort_order",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Sorting order ('asc' or 'desc', default: 'asc').",
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
                "description": "Successfully retrieved paginated orders.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "orders": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "integer",
                                        "example": 1,
                                        "description": "Unique identifier for the order."
                                    },
                                    "created_at": {
                                        "type": "string",
                                        "format": "date-time",
                                        "example": "2025-01-20T10:00:00Z",
                                        "description": "Timestamp of when the order was created."
                                    },
                                    "status": {
                                        "type": "string",
                                        "example": "completed",
                                        "description": "Status of the order."
                                    },
                                    "total": {
                                        "type": "number",
                                        "format": "float",
                                        "example": 99.99,
                                        "description": "Total amount of the order."
                                    }
                                }
                            }
                        },
                        "total": {
                            "type": "integer",
                            "example": 100,
                            "description": "Total number of orders."
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
            "500": {"description": "Internal server error."}
        }
    })

    def get_orders():
        """
        Retrieves paginated orders with optional sorting and metadata.
        """
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)
            sort_by = request.args.get('sort_by', default='created_at', type=str)
            sort_order = request.args.get('sort_order', default='asc', type=str)
            include_meta = request.args.get('include_meta', default='true').lower() == 'true'

            if page < 1 or per_page < 1 or per_page > 100:
                return error_response("Invalid pagination parameters.")
            if sort_by not in SORTABLE_FIELDS:
                return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}")

            data = OrderService.get_paginated_orders(
                page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=include_meta
            )

            response = {"orders": orders_schema.dump(data["items"])}
            if include_meta:
                response.update({k: v for k, v in data.items() if k != "items"})

            return jsonify(response), 200
        except Exception as e:
            return error_response(str(e), 500)

    # ---------------------------
    # Get Order by ID
    # ---------------------------
    @order_bp.route('/<int:order_id>', methods=['GET'])
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Orders"],
        "summary": "Retrieve an order by its ID",
        "description": "Retrieves a specific order using its unique ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "order_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID of the order to retrieve.",
                "example": 123
            }
        ],
        "responses": {
            "200": {
                "description": "Successfully retrieved the order.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "example": 123,
                            "description": "Unique identifier of the order."
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2025-01-20T10:00:00Z",
                            "description": "Timestamp when the order was created."
                        },
                        "status": {
                            "type": "string",
                            "example": "completed",
                            "description": "Current status of the order."
                        },
                        "total": {
                            "type": "number",
                            "format": "float",
                            "example": 150.75,
                            "description": "Total amount for the order."
                        },
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_id": {
                                        "type": "integer",
                                        "example": 45,
                                        "description": "ID of the product."
                                    },
                                    "quantity": {
                                        "type": "integer",
                                        "example": 2,
                                        "description": "Quantity of the product in the order."
                                    },
                                    "price": {
                                        "type": "number",
                                        "format": "float",
                                        "example": 75.38,
                                        "description": "Price of a single unit of the product."
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "404": {
                "description": "Order not found.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Order with ID 123 not found."
                        }
                    }
                }
            },
            "500": {"description": "Internal server error."}
        }
    })

    def get_order(order_id):
        """
        Retrieve an order by its ID.
        """
        try:
            order = OrderService.get_order_by_id(order_id)
            if not order:
                return error_response(f"Order with ID {order_id} not found.", 404)
            return jsonify(order_schema.dump(order)), 200
        except Exception as e:
            return error_response(str(e), 500)

    @order_bp.route('/<int:order_id>', methods=['PUT'])
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Orders"],
        "summary": "Update an order by its ID",
        "description": "Updates the details of an order using its unique ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "order_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID of the order to update.",
                "example": 123
            }
        ],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "Updated status of the order.",
                                "example": "shipped"
                            },
                            "total": {
                                "type": "number",
                                "format": "float",
                                "description": "Updated total amount for the order.",
                                "example": 150.75
                            },
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "product_id": {
                                            "type": "integer",
                                            "description": "ID of the product.",
                                            "example": 45
                                        },
                                        "quantity": {
                                            "type": "integer",
                                            "description": "Quantity of the product in the order.",
                                            "example": 3
                                        },
                                        "price": {
                                            "type": "number",
                                            "format": "float",
                                            "description": "Updated price of the product.",
                                            "example": 50.25
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["status", "items"]  # Specify required fields
                    }
                }
            }
        },
        "responses": {
            "200": {
                "description": "Successfully updated the order.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Order updated successfully."
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
                "description": "Order not found.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Order with ID 123 not found."
                        }
                    }
                }
            },
            "500": {"description": "Internal server error."}
        }
    })

    def update_order(order_id):
        """
        Update an order by its ID.
        """
        try:
            data = request.get_json()
            validated_data = order_schema.load(data, partial=True)
            order = OrderService.update_order(order_id, **validated_data)
            return jsonify(order_schema.dump(order)), 200
        except Exception as e:
            return error_response(str(e), 500)

    # ---------------------------
    # Delete Order by ID
    # ---------------------------
    @order_bp.route('/<int:order_id>', methods=['DELETE'])
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Orders"],
        "summary": "Delete an order by its ID",
        "description": "Deletes a specific order using its unique ID.",
        "parameters": [
            {
                "name": "order_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID of the order to delete."
            }
        ],
        "responses": {
            "200": {"description": "Successfully deleted the order."},
            "404": {"description": "Order not found."},
            "500": {"description": "Internal server error."}
        }
    })
    def delete_order(order_id):
        """
        Delete an order by its ID.
        """
        try:
            OrderService.delete_order(order_id)
            return jsonify({"message": "Order deleted successfully"}), 200
        except Exception as e:
            return error_response(str(e), 500)


    return order_bp
