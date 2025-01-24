from flask import Blueprint, request, jsonify
from services.shopping_cart_service import ShoppingCartService
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.utils import error_response
from utils.limiter import limiter
from flasgger.utils import swag_from
# Allowed sortable fields
SORTABLE_FIELDS = ['name', 'price']

def create_shopping_cart_bp(cache):
    """
    Factory function to create the <blueprint_name> blueprint with a shared cache instance.
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
                "description": f"Field to sort by. Allowed: {SORTABLE_FIELDS}. Default: 'name'.",
                "required": False,
                "example": "name"
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
                                    "product_id": {"type": "integer"},
                                    "quantity": {"type": "integer"},
                                    "subtotal": {"type": "float"}
                                }
                            }
                        },
                        "total_items": {"type": "integer", "description": "Total number of items in the cart."},
                        "page": {"type": "integer", "description": "Current page number."},
                        "per_page": {"type": "integer", "description": "Number of items per page."}
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
            sort_by = request.args.get('sort_by', 'name', type=str)
            sort_order = request.args.get('sort_order', 'asc', type=str)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            # Validate sort_by and sort_order
            if sort_by not in SORTABLE_FIELDS:
                return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}.", 400)
            if sort_order not in ['asc', 'desc']:
                return error_response("Invalid sort_order value. Allowed: 'asc', 'desc'.", 400)

            # Fetch cart and sort items
            cart = ShoppingCartService.get_cart_by_customer(customer_id)
            if not cart:
                return error_response("Shopping cart not found.", 404)

            items = sorted(
                cart.items,
                key=lambda x: getattr(x, sort_by),
                reverse=(sort_order == 'desc')
            )

            # Paginate items
            total_items = len(items)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_items = items[start:end]

            # Prepare the response
            return jsonify({
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "subtotal": item.subtotal
                    } for item in paginated_items
                ],
                "total_items": total_items,
                "page": page,
                "per_page": per_page
            }), 200
        except Exception as e:
            return error_response(str(e), 500)


    # ---------------------------
    # Add Item to Shopping Cart
    # ---------------------------
    @shopping_cart_bp.route('', methods=['POST'])
    @jwt_required()
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Shopping Cart"],
        "summary": "Add an item to the cart",
        "description": "Adds a product to the shopping cart or updates its quantity.",
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
                        "quantity": {"type": "integer", "description": "Quantity of the product to add."}
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
    def add_item():
        """Add an item to the shopping cart."""
        try:
            customer_id = get_jwt_identity()
            data = request.get_json()
            item = ShoppingCartService.add_item_to_cart(
                customer_id, data['product_id'], data['quantity']
            )
            return jsonify({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "subtotal": item.subtotal
            }), 201
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Remove Item from Shopping Cart
    # ---------------------------
    @shopping_cart_bp.route('/<int:product_id>', methods=['DELETE'])
    @jwt_required()
    @limiter.limit("5 per minute")
    @swag_from({
        "tags": ["Shopping Cart"],
        "summary": "Remove an item from the cart",
        "description": "Removes a product from the shopping cart by its product ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "product_id",
                "in": "path",
                "type": "integer",
                "description": "ID of the product to remove from the cart.",
                "required": True
            }
        ],
        "responses": {
            "200": {"description": "Item removed successfully."},
            "404": {"description": "Item not found in the cart."},
            "500": {"description": "Internal server error."}
        }
    })
    def remove_item(product_id):
        """Remove an item from the shopping cart."""
        try:
            customer_id = get_jwt_identity()
            ShoppingCartService.remove_item_from_cart(customer_id, product_id)
            return jsonify({"message": "Item removed successfully."}), 200
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Checkout Shopping Cart
    # ---------------------------
    @shopping_cart_bp.route('/checkout', methods=['POST'])
    @jwt_required()
    @limiter.limit("2 per minute")
    @swag_from({
        "tags": ["Shopping Cart"],
        "summary": "Checkout the shopping cart",
        "description": "Finalizes the shopping cart and converts it into an order.",
        "security": [{"Bearer": []}],
        "responses": {
            "200": {"description": "Checkout successful."},
            "400": {"description": "Validation error or invalid cart state."},
            "500": {"description": "Internal server error."}
        }
    })

    def checkout():
        """Checkout the shopping cart."""
        try:
            customer_id = get_jwt_identity()
            ShoppingCartService.checkout_cart(customer_id)
            return jsonify({"message": "Checkout successful."}), 200
        except Exception as e:
            return error_response(str(e))

    return shopping_cart_bp
