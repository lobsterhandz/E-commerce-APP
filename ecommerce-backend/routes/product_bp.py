from flask import Blueprint, request, jsonify
from services.product_service import ProductService
from schemas.product_schema import product_schema, products_schema
from utils.utils import error_response, role_required, jwt_required
from utils.limiter import create_limiter
from flasgger.utils import swag_from

# Allowed sortable fields (adjust as needed)
SORTABLE_FIELDS = ['name', 'price', 'stock_quantity']

def create_product_bp(cache, limiter):
    """
    Factory function to create the product blueprint with a shared cache instance.
    """
    product_bp = Blueprint('products', __name__)

    # ---------------------------
    # Create a Product
    # ---------------------------
    @product_bp.route('', methods=['POST'], endpoint='products_create')
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Products"],
        "summary": "Create a new product",
        "description": (
            "Creates a new product with the specified details. "
            "The payload must include 'name', 'price', and 'stock_quantity'. "
            "Optionally, include 'category_id'."
        ),
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": ["name", "price", "stock_quantity"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the product."
                        },
                        "price": {
                            "type": "number",
                            "format": "float",
                            "description": "Price of the product."
                        },
                        "stock_quantity": {
                            "type": "integer",
                            "description": "Stock quantity available."
                        },
                        "category_id": {
                            "type": "integer",
                            "description": "Optional category ID for the product."
                        }
                    }
                }
            }
        ],
        "responses": {
            "201": {"description": "Product created successfully."},
            "400": {"description": "Validation or creation error."},
            "500": {"description": "Internal server error."}
        }
    })
    def create_product():
        try:
            data = request.get_json()
            validated_data = product_schema.load(data)
            product = ProductService.create_product(**validated_data)
            return jsonify(product_schema.dump(product)), 201
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Get Paginated Products
    # ---------------------------
    @product_bp.route('', methods=['GET'], endpoint='products_get_paginated')
    @cache.cached(query_string=True)
    @limiter.limit("10 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Products"],
        "summary": "Retrieve paginated products",
        "description": "Retrieves a paginated list of products with optional sorting and metadata.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "page", "in": "query", "type": "integer", "description": "Page number (default: 1)."},
            {"name": "per_page", "in": "query", "type": "integer", "description": "Items per page (default: 10, max: 100)."},
            {"name": "sort_by", "in": "query", "type": "string", "description": "Field to sort by (default: 'name')."},
            {"name": "sort_order", "in": "query", "type": "string", "description": "Sort order ('asc' or 'desc')."},
            {"name": "include_meta", "in": "query", "type": "boolean", "description": "Include metadata (default: true)."}
        ],
        "responses": {
            "200": {"description": "Successfully retrieved paginated products."},
            "400": {"description": "Invalid parameters."},
            "500": {"description": "Internal server error."}
        }
    })
    def get_products():
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

            data = ProductService.get_paginated_products(
                page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=include_meta
            )

            response = {"products": products_schema.dump(data["items"])}
            if include_meta:
                response.update({k: v for k, v in data.items() if k != "items"})

            return jsonify(response), 200
        except Exception as e:
            return error_response(str(e), 500)

    # ---------------------------
    # Get Product by ID
    # ---------------------------
    @product_bp.route('/<int:product_id>', methods=['GET'], endpoint='products_get')
    @limiter.limit("10 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Products"],
        "summary": "Retrieve a product by ID",
        "description": "Fetches a product by its unique ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "product_id", "in": "path", "type": "integer", "required": True, "description": "Product ID."}
        ],
        "responses": {
            "200": {"description": "Product retrieved successfully."},
            "404": {"description": "Product not found."}
        }
    })
    def get_product(product_id):
        try:
            product = ProductService.get_product_by_id(product_id)
            return jsonify(product_schema.dump(product)), 200
        except Exception as e:
            return error_response(str(e), 404)

    # ---------------------------
    # Update Product
    # ---------------------------
    @product_bp.route('/<int:product_id>', methods=['PUT'], endpoint='products_update')
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Products"],
        "summary": "Update a product",
        "description": (
            "Updates a product's details by its unique ID. "
            "Fields that can be updated include name, price, stock_quantity, and optionally category_id."
        ),
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "product_id", "in": "path", "type": "integer", "required": True, "description": "Product ID."},
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Updated name of the product."},
                        "price": {"type": "number", "format": "float", "description": "Updated price of the product."},
                        "stock_quantity": {"type": "integer", "description": "Updated stock quantity."},
                        "category_id": {"type": "integer", "description": "Optional updated category ID."}
                    }
                }
            }
        ],
        "responses": {
            "200": {"description": "Product updated successfully."},
            "400": {"description": "Validation error."},
            "404": {"description": "Product not found."}
        }
    })
    def update_product(product_id):
        try:
            data = request.get_json()
            validated_data = product_schema.load(data, partial=True)
            product = ProductService.update_product(product_id, **validated_data)
            return jsonify(product_schema.dump(product)), 200
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Delete Product
    # ---------------------------
    @product_bp.route('/<int:product_id>', methods=['DELETE'], endpoint='products_delete')
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Products"],
        "summary": "Delete a product",
        "description": "Deletes a product by its unique ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "product_id", "in": "path", "type": "integer", "required": True, "description": "Product ID."}
        ],
        "responses": {
            "200": {"description": "Product deleted successfully."},
            "404": {"description": "Product not found."}
        }
    })
    def delete_product(product_id):
        try:
            ProductService.delete_product(product_id)
            return jsonify({"message": "Product deleted successfully"}), 200
        except Exception as e:
            return error_response(str(e), 404)

    return product_bp
