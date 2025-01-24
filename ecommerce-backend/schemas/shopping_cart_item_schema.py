from marshmallow import Schema, fields, validate, post_dump


class ShoppingCartItemSchema(Schema):
    # ---------------------------
    # Fields
    # ---------------------------
    id = fields.Int(dump_only=True)

    cart_id = fields.Int(
        required=True,
        error_messages={"required": "Cart ID is required."}
    )

    product_id = fields.Int(
        required=True,
        error_messages={"required": "Product ID is required."}
    )

    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Quantity must be at least 1."),
        error_messages={"required": "Quantity is required."}
    )

    subtotal = fields.Float(
        dump_only=True,
        error_messages={"invalid": "Invalid subtotal format."}
    )

    product = fields.Dict(dump_only=True)  # Nested product details if needed

    created_at = fields.DateTime(dump_only=True)  # Read-only field for creation timestamp

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
shopping_cart_item_schema = ShoppingCartItemSchema()
shopping_cart_items_schema = ShoppingCartItemSchema(many=True)
