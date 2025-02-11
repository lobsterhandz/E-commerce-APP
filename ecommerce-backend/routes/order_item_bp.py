from flask import Blueprint, request, jsonify, current_app
from services.order_item_service import OrderItemService
from schemas.order_item_schema import order_item_schema, order_items_schema
from utils.utils import error_response, role_required, jwt_required
from flasgger.utils import swag_from

# Allowed sortable fields
SORTABLE_FIELDS = ['quantity', 'price_at_order', 'subtotal']

def create_order_item_bp(cache, limiter):
    """
    Factory function to create the order items blueprint with a shared cache instance.
    """
    order_item_bp = Blueprint('order_items', __name__)

    # ---------------------------
    # Create Order Item
    # ---------------------------
    @order_item_bp.route('', methods=['POST'])
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Order Items"],
        "summary": "Create a new order item",
        "description": "Creates a new order item for a specific order. Requires a valid JWT token for authentication.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "in": "query",
                "name": "order_id",
                "required": True,
                "schema": {"type": "integer"},
                "description": "ID of the order.",
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
                            "order_id": {
                                "type": "integer",
                                "description": "ID of the order.",
                                "example": 123
                            },
                            "product_id": {
                                "type": "integer",
                                "description": "ID of the product.",
                                "example": 456
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "Quantity of the product.",
                                "example": 2
                            },
                            "price_at_order": {
                                "type": "number",
                                "format": "float",
                                "description": "Price of the product at the time of the order.",
                                "example": 19.99
                            }
                        },
                        "required": ["order_id", "product_id", "quantity", "price_at_order"]
                    }
                }
            }
        },
        "responses": {
            "201": {
                "description": "Order item created successfully.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "order_item_id": {"type": "integer", "example": 789},
                                "order_id": {"type": "integer", "example": 123},
                                "product_id": {"type": "integer", "example": 456},
                                "quantity": {"type": "integer", "example": 2},
                                "price_at_order": {"type": "number", "format": "float", "example": 19.99},
                                "created_at": {"type": "string", "example": "2025-01-22T12:34:56Z"}
                            }
                        }
                    }
                }
            },
            "400": {"description": "Validation or creation error."},
            "403": {"description": "Authentication error. Invalid or missing token."},
            "500": {"description": "Internal server error."}
        }
    })
    def create_order_item():
        try:
            data = request.get_json()
            validated_data = order_item_schema.load(data)
            order_item = OrderItemService.create_item(**validated_data)
            return jsonify(order_item_schema.dump(order_item)), 201
        except Exception as e:
            current_app.logger.error(f"Error creating order item: {str(e)}")
            return error_response(str(e))

    # ---------------------------
    # Get Order Items by Order ID
    # ---------------------------
    @order_item_bp.route('/order/<int:order_id>', methods=['GET'])
    @cache.cached(query_string=True)
    @limiter.limit("10 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Order Items"],
        "summary": "Retrieve order items by order ID",
        "description": "Fetches all order items associated with a specific order.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "order_id", "in": "path", "required": True, "schema": {"type": "integer"}, "description": "Order ID."}
        ],
        "responses": {
            "200": {
                "description": "Order items retrieved successfully.",
                "schema": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/OrderItem"}
                }
            },
            "404": {"description": "Order not found."}
        }
    })
    def get_order_items(order_id):
        try:
            order_items = OrderItemService.get_items_by_order_id(order_id)
            return jsonify(order_items_schema.dump(order_items)), 200
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Update Order Item
    # ---------------------------
    @order_item_bp.route('/<int:order_item_id>', methods=['PUT'])
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Order Items"],
        "summary": "Update an order item",
        "description": "Updates an order item's details.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "order_item_id", "in": "path", "required": True, "schema": {"type": "integer"}, "description": "Order item ID."}
        ],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "quantity": {"type": "integer", "description": "Updated quantity of the order item."}
                        }
                    }
                }
            }
        },
        "responses": {
            "200": {"description": "Order item updated successfully."},
            "400": {"description": "Validation error."},
            "404": {"description": "Order item not found."}
        }
    })
    def update_order_item(order_item_id):
        try:
            data = request.get_json()
            validated_data = order_item_schema.load(data, partial=True)
            order_item = OrderItemService.updater_item(order_item_id, **validated_data)
            return jsonify(order_item_schema.dump(order_item)), 200
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Delete Order Item
    # ---------------------------
    @order_item_bp.route('/<int:order_item_id>', methods=['DELETE'])
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Order Items"],
        "summary": "Delete an order item",
        "description": "Deletes an order item by its unique ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "order_item_id", "in": "path", "required": True, "schema": {"type": "integer"}, "description": "Order item ID."}
        ],
        "responses": {
            "200": {"description": "Order item deleted successfully."},
            "404": {"description": "Order item not found."}
        }
    })
    def delete_order_item(order_item_id):
        try:
            OrderItemService.delete_item(order_item_id)
            return jsonify({"message": "Order item deleted successfully"}), 200
        except Exception as e:
            return error_response(str(e))

    return order_item_bp
