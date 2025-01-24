from marshmallow import Schema, fields, post_dump
from schemas.shopping_cart_item_schema import ShoppingCartItemSchema  # Assuming the schema is in schemas

class ShoppingCartSchema(Schema):
    # ---------------------------
    # Fields
    # ---------------------------
    id = fields.Int(dump_only=True)

    customer_id = fields.Int(
        required=True,
        error_messages={"required": "Customer ID is required."}
    )

    created_at = fields.DateTime(dump_only=True)  # Read-only field for creation timestamp
    updated_at = fields.DateTime(dump_only=True)  # Read-only field for last update timestamp
    deleted_at = fields.DateTime(dump_only=True)  # Read-only field for soft-deletion timestamp

    items = fields.Nested(
        ShoppingCartItemSchema,
        many=True,
        dump_only=True,  # Items are populated on fetch, not creation
        description="List of items in the shopping cart."
    )

    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Preserve order of fields in serialized output.

    # ---------------------------
    # Custom Serialization Rules
    # ---------------------------
    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """
        Removes null fields from serialized output.
        """
        return {key: value for key, value in data.items() if value is not None}


# ---------------------------
# Example Usage
# ---------------------------
shopping_cart_schema = ShoppingCartSchema()
shopping_carts_schema = ShoppingCartSchema(many=True)
