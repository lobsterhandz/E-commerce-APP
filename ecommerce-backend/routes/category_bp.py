from flask import Blueprint, request, jsonify
from services.category_service import CategoryService
from schemas.category_schema import category_schema, categories_schema
from utils.utils import error_response, role_required, jwt_required
from utils.limiter import create_limiter
from flasgger.utils import swag_from

# Allowed sortable fields
SORTABLE_FIELDS = ['name']

def create_category_bp(cache):
    """
    Factory function to create the category blueprint with a shared cache instance.
    """
    category_bp = Blueprint('categories', __name__)

    # ---------------------------
    # Create a Category
    # ---------------------------
    @category_bp.route('', methods=['POST'])
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Categories"],
        "summary": "Create a new category",
        "description": "Creates a new category with the specified details.",
        "security": [{"Bearer": []}],
        "parameters": [
    {
        "in": "body",
        "name": "body",
        "required": True,
        "schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the category.",
                    "example": "Electronics"
                }
            },
            "required": ["name"]
        }
    }
],

        "responses": {
            "201": {"description": "Category created successfully."},
            "400": {"description": "Validation or creation error."},
            "500": {"description": "Internal server error."}
        }
    })

    def create_category():
        """Creates a new category."""
        try:
            data = request.get_json()
            validated_data = category_schema.load(data)
            category = CategoryService.create_category(**validated_data)
            return jsonify(category_schema.dump(category)), 201
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Get All Categories
    # ---------------------------
    @category_bp.route('', methods=['GET'])
    @cache.cached(query_string=True)
    @limiter.limit("10 per minute")
    @jwt_required
    @swag_from({
        "tags": ["Categories"],
        "summary": "Retrieve all categories",
        "description": "Fetches all categories with optional sorting parameters.",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "sort_by",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Field to sort by (default: 'name'). Allowed fields: ['name', 'id'].",
                "example": "name"
            },
            {
                "name": "sort_order",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Sort order ('asc' or 'desc', default: 'asc').",
                "example": "asc"
            }
        ],
        "responses": {
            "200": {
                "description": "List of categories retrieved successfully.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                                "example": 1,
                                "description": "Unique identifier of the category."
                            },
                            "name": {
                                "type": "string",
                                "example": "Electronics",
                                "description": "Name of the category."
                            }
                        }
                    }
                }
            },
            "400": {"description": "Invalid query parameters."},
            "500": {"description": "Internal server error."}
        }
    })

    def get_categories():
        """Retrieves all categories with optional sorting."""
        try:
            sort_by = request.args.get('sort_by', default='name', type=str)
            sort_order = request.args.get('sort_order', default='asc', type=str)

            if sort_by not in SORTABLE_FIELDS:
                return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}", 400)
            if sort_order not in ['asc', 'desc']:
                return error_response("Invalid sort_order value. Allowed: 'asc', 'desc'.", 400)

            categories = CategoryService.get_all_categories(sort_by=sort_by, sort_order=sort_order)
            return jsonify(categories_schema.dump(categories)), 200
        except Exception as e:
            return error_response(f"An error occurred while fetching categories: {str(e)}", 500)

    # ---------------------------
    # Get Category by ID
    # ---------------------------
    @category_bp.route('/<int:category_id>', methods=['GET'])
    @cache.cached(query_string=True)
    @limiter.limit("10 per minute")
    @jwt_required
    @swag_from({
        "tags": ["Categories"],
        "summary": "Retrieve a category by ID",
        "description": "Fetches a category by its unique ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "category_id", "in": "path", "type": "integer", "required": True, "description": "Category ID.", "example": 1}
        ],
        "responses": {
            "200": {"description": "Category retrieved successfully."},
            "404": {"description": "Category not found."},
            "500": {"description": "Internal server error."}
        }
    })
    def get_category(category_id):
        """Retrieves a category by ID."""
        try:
            category = CategoryService.get_category_by_id(category_id)
            if not category:
                return error_response(f"Category with ID {category_id} not found.", 404)
            return jsonify(category_schema.dump(category)), 200
        except Exception as e:
            return error_response(f"An error occurred: {str(e)}", 500)

    # ---------------------------
    # Update Category
    # ---------------------------
    @category_bp.route('/<int:category_id>', methods=['PUT'])
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Categories"],
        "summary": "Update a category",
        "description": "Updates a category's details by its unique ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "category_id", "in": "path", "type": "integer", "required": True, "description": "Category ID.", "example": 1},
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Updated name of the category.", "example": "New Category Name"}
                    }
                }
            }
        ],
        "responses": {
            "200": {"description": "Category updated successfully."},
            "400": {"description": "Validation error."},
            "404": {"description": "Category not found."}
        }
    })
    def update_category(category_id):
        """Updates a category by ID."""
        try:
            data = request.get_json()
            validated_data = category_schema.load(data, partial=True)
            category = CategoryService.update_category(category_id, **validated_data)
            return jsonify(category_schema.dump(category)), 200
        except Exception as e:
            return error_response(str(e))

    # ---------------------------
    # Delete Category
    # ---------------------------
    @category_bp.route('/<int:category_id>', methods=['DELETE'])
    @limiter.limit("5 per minute")
    @jwt_required
    @role_required('admin')
    @swag_from({
        "tags": ["Categories"],
        "summary": "Delete a category",
        "description": "Deletes a category by its unique ID.",
        "security": [{"Bearer": []}],
        "parameters": [
            {"name": "category_id", "in": "path", "type": "integer", "required": True, "description": "Category ID.", "example": 1}
        ],
        "responses": {
            "200": {"description": "Category deleted successfully."},
            "404": {"description": "Category not found."}
        }
    })
    def delete_category(category_id):
        """Deletes a category by ID."""
        try:
            CategoryService.delete_category(category_id)
            return jsonify({"message": "Category deleted successfully"}), 200
        except Exception as e:
            return error_response(str(e), 404)

    return category_bp
