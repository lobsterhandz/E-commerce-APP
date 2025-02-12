from marshmallow import Schema, fields, validate, post_dump

class OrderItemSchema(Schema):
    # ---------------------------
    # Fields
    # ---------------------------
    id = fields.Int(dump_only=True)

    order_id = fields.Int(dump_only=True)

    product_id = fields.Int(
        required=True,
        error_messages={"required": "Product ID is required."}
    )

    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Quantity must be at least 1.")
    )

    price_at_order = fields.Float(
        required=True,
        validate=validate.Range(min=0, error="Price must be non-negative."),
        error_messages={"required": "Price at order is required."}
    )

    subtotal = fields.Float(
        dump_only=True
    )

    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)

    product = fields.Nested(
        "ProductSchema",  # Reference to the product schema
        only=("id", "name", "price"),
        dump_only=True
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
    def calculate_subtotal(self, data, **kwargs):
        """Calculate and include the subtotal if not already present."""
        if "quantity" in data and "price_at_order" in data and "subtotal" not in data:
            data["subtotal"] = data["quantity"] * data["price_at_order"]
        return data

    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """Removes null fields from serialized output."""
        return {key: value for key, value in data.items() if value is not None}


# ---------------------------
# Example Usage
# ---------------------------
order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)
