from flask import Blueprint, request, jsonify
from services.shopping_cart_item_service import ShoppingCartItemService
from flask_jwt_extended import jwt_required
from utils.utils import error_response
from utils.limiter import create_limiter
from flasgger.utils import swag_from

# Allowed sortable fields for shopping cart items.
SORTABLE_FIELDS = ['quantity', 'subtotal', 'product_id']

def create_shopping_cart_item_bp(cache):
    """
    Factory function to create the shopping cart item blueprint with a shared cache instance.
    """
    shopping_cart_item_bp = Blueprint('shopping_cart_item', __name__)

    # ---------------------------
    # Get All Items in Cart
    # ---------------------------
    @shopping_cart_item_bp.route('/<int:cart_id>/items', methods=['GET'])
    @cache.cached(query_string=True)
    @jwt_required()
    @limiter.limit("10 per minute")
    @swag_from({
        "tags": ["Shopping Cart Items"],
        "summary": "Fetch all items in a shopping cart",
        "description": "Fetches all items for a specific shopping cart with optional sorting.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "cart_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID of the shopping cart."
            },
            {
                "name": "sort_by",
                "in": "query",
                "type": "string",
                "required": False,
                "description": f"Field to sort by. Allowed: {SORTABLE_FIELDS}. Default: 'quantity'.",
                "example": "quantity"
            },
            {
                "name": "sort_order",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Sort order ('asc' or 'desc'). Default: 'asc'.",
                "example": "asc"
            }
        ],
        "responses": {
            "200": {
                "description": "Successfully retrieved cart items.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "product_id": {"type": "integer"},
                            "quantity": {"type": "integer"},
                            "subtotal": {"type": "number", "format": "float"}
                        }
                    }
                }
            },
            "404": {"description": "Shopping cart not found."},
            "500": {"description": "Internal server error."}
        }
    })
    def get_cart_items(cart_id):
        """Fetch all items in a specific shopping cart with optional sorting."""
        try:
            # Fetch query parameters
            sort_by = request.args.get('sort_by', default='quantity', type=str)
            sort_order = request.args.get('sort_order', default='asc', type=str)

            # Validate sort parameters
            if sort_by not in SORTABLE_FIELDS:
                return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}.", 400)
            if sort_order not in ['asc', 'desc']:
                return error_response("Invalid sort_order value. Allowed: 'asc', 'desc'.", 400)

            # Fetch and sort items using the service layer
            items = ShoppingCartItemService.list_items_by_cart(cart_id)
            sorted_items = sorted(
                items,
                key=lambda x: getattr(x, sort_by),
                reverse=(sort_order == 'desc')
            )

            return jsonify([item.to_dict() for item in sorted_items]), 200
        except Exception as e:
            return error_response(str(e), 500)

    # ---------------------------
    # Add an Item to Cart
    # ---------------------------
    @shopping_cart_item_bp.route('/<int:cart_id>/items', methods=['POST'])
    @jwt_required()
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Shopping Cart Items"],
        "summary": "Add an item to a shopping cart",
        "description": "Adds an item to a shopping cart or updates the quantity if the item already exists.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": ["product_id", "quantity"],
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "ID of the product to add."
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Quantity to add to the cart."
                        }
                    }
                }
            }
        ],
        "responses": {
            "201": {"description": "Item successfully added to the cart."},
            "400": {"description": "Validation error or invalid input."},
            "500": {"description": "Internal server error."}
        }
    })
    def add_item_to_cart(cart_id):
        """Add an item to a shopping cart."""
        try:
            data = request.get_json()
            item = ShoppingCartItemService.add_item(
                cart_id=cart_id,
                product_id=data['product_id'],
                quantity=data['quantity']
            )
            return jsonify(item.to_dict()), 201
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Update an Item in Cart
    # ---------------------------
    @shopping_cart_item_bp.route('/<int:cart_id>/items/<int:item_id>', methods=['PUT'])
    @jwt_required()
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Shopping Cart Items"],
        "summary": "Update an item in a shopping cart",
        "description": "Updates the quantity of a specific item in a shopping cart.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "cart_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID of the shopping cart."
            },
            {
                "name": "item_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID of the shopping cart item."
            },
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "quantity": {
                            "type": "integer",
                            "description": "Updated quantity for the item."
                        }
                    }
                }
            }
        ],
        "responses": {
            "200": {"description": "Item updated successfully."},
            "400": {"description": "Validation error or invalid input."},
            "404": {"description": "Item not found."},
            "500": {"description": "Internal server error."}
        }
    })
    def update_cart_item(cart_id, item_id):
        """Update an item in the shopping cart."""
        try:
            data = request.get_json()
            item = ShoppingCartItemService.update_item_quantity(
                cart_id=cart_id,
                item_id=item_id,
                new_quantity=data['quantity']
            )
            return jsonify(item.to_dict()), 200
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Remove an Item from Cart
    # ---------------------------
    @shopping_cart_item_bp.route('/<int:cart_id>/items/<int:item_id>', methods=['DELETE'])
    @jwt_required()
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Shopping Cart Items"],
        "summary": "Remove an item from a shopping cart",
        "description": "Removes a specific item from a shopping cart.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "cart_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID of the shopping cart."
            },
            {
                "name": "item_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID of the shopping cart item to remove."
            }
        ],
        "responses": {
            "200": {"description": "Item removed successfully."},
            "404": {"description": "Item not found."},
            "500": {"description": "Internal server error."}
        }
    })
    def remove_cart_item(cart_id, item_id):
        """Remove an item from the shopping cart."""
        try:
            ShoppingCartItemService.remove_item(cart_id=cart_id, item_id=item_id)
            return jsonify({"message": "Item removed successfully."}), 200
        except Exception as e:
            return error_response(str(e))

    return shopping_cart_item_bp
