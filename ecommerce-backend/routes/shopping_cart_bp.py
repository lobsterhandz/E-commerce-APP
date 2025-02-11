from flask import Blueprint, request, jsonify
from services.shopping_cart_service import ShoppingCartService
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.utils import error_response
from utils.limiter import limiter
from flasgger.utils import swag_from

# Allowed sortable fields for cart items.
SORTABLE_FIELDS = ['quantity', 'subtotal']

def create_shopping_cart_bp(cache):
    """
    Factory function to create the shopping cart blueprint with a shared cache instance.
    """
    shopping_cart_bp = Blueprint('shopping_cart', __name__)

    # ---------------------------
    # Fetch Shopping Cart
    # ---------------------------
    @shopping_cart_bp.route('', methods=['GET'])
    @cache.cached(query_string=True)
    @jwt_required()
    @limiter.limit("10 per minute")
    @swag_from({
        "tags": ["Shopping Cart"],
        "summary": "Fetch the shopping cart",
        "description": "Fetches the current user's shopping cart with optional sorting and pagination.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "sort_by",
                "in": "query",
                "type": "string",
                "description": f"Field to sort by. Allowed: {SORTABLE_FIELDS}. Default: 'quantity'.",
                "required": False,
                "example": "quantity"
            },
            {
                "name": "sort_order",
                "in": "query",
                "type": "string",
                "description": "Sort order ('asc' or 'desc'). Default: 'asc'.",
                "required": False,
                "example": "asc"
            },
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "description": "Page number for pagination. Default: 1.",
                "required": False,
                "example": 1
            },
            {
                "name": "per_page",
                "in": "query",
                "type": "integer",
                "description": "Number of items per page for pagination. Default: 10.",
                "required": False,
                "example": 10
            }
        ],
        "responses": {
            "200": {
                "description": "Successfully retrieved the shopping cart.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_id": {"type": "integer", "example": 45},
                                    "quantity": {"type": "integer", "example": 2},
                                    "subtotal": {"type": "number", "format": "float", "example": 49.99}
                                }
                            }
                        },
                        "total_items": {"type": "integer", "description": "Total number of items in the cart.", "example": 5},
                        "page": {"type": "integer", "description": "Current page number.", "example": 1},
                        "per_page": {"type": "integer", "description": "Number of items per page.", "example": 10}
                    }
                }
            },
            "400": {"description": "Validation error or invalid input."},
            "500": {"description": "Internal server error."}
        }
    })
    def get_cart():
        """Fetch the current user's shopping cart with pagination and sorting."""
        try:
            customer_id = get_jwt_identity()
            sort_by = request.args.get('sort_by', 'quantity', type=str)
            sort_order = request.args.get('sort_order', 'asc', type=str)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            if sort_by not in SORTABLE_FIELDS:
                return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}.", 400)
            if sort_order not in ['asc', 'desc']:
                return error_response("Invalid sort_order value. Allowed: 'asc', 'desc'.", 400)

            cart = ShoppingCartService.get_cart_by_customer(customer_id)
            if not cart:
                return error_response("Shopping cart not found.", 404)

            # Sort items
            sorted_items = sorted(
                cart.items,
                key=lambda x: getattr(x, sort_by),
                reverse=(sort_order == 'desc')
            )
            total_items = len(sorted_items)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_items = sorted_items[start:end]

            response_data = {
                "items": [item.to_dict() for item in paginated_items],
                "total_items": total_items,
                "page": page,
                "per_page": per_page
            }
            return jsonify(response_data), 200
        except Exception as e:
            return error_response(str(e), 500)

    # ---------------------------
    # Add Item to Cart
    # ---------------------------
    @shopping_cart_bp.route('', methods=['POST'])
    @jwt_required()
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Shopping Cart"],
        "summary": "Add an item to the cart",
        "description": "Adds a product to the shopping cart or updates its quantity if it already exists.",
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
                        "product_id": {"type": "integer", "description": "ID of the product to add."},
                        "quantity": {"type": "integer", "description": "Quantity to add to the cart."}
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
    def add_item_to_cart():
        """Add an item to the shopping cart."""
        try:
            customer_id = get_jwt_identity()
            data = request.get_json()
            item = ShoppingCartItemService.add_item_to_cart(
                customer_id=customer_id,
                product_id=data['product_id'],
                quantity=data['quantity']
            )
            return jsonify(item.to_dict()), 201
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Update an Item in Cart
    # ---------------------------
    @shopping_cart_bp.route('/<int:cart_id>/items/<int:item_id>', methods=['PUT'])
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
                        "quantity": {"type": "integer", "description": "Updated quantity for the item."}
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
    @shopping_cart_bp.route('/<int:cart_id>/items/<int:item_id>', methods=['DELETE'])
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

    return shopping_cart_bp
