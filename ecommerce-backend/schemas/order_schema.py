from marshmallow import Schema, fields, validate, post_dump
from schemas.order_item_schema import order_item_schema

class OrderSchema(Schema):
    # ---------------------------
    # Fields
    # ---------------------------
    id = fields.Int(dump_only=True)
    customer_id = fields.Int(
        required=True,
        error_messages={"required": "Customer ID is required."}
    )
    # Use a List field to ensure proper input type.
    order_items = fields.List(
        fields.Nested(order_item_schema, exclude=("order_id",)),
        required=True,
        error_messages={"required": "Order items are required."}
    )
    total_price = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Preserve order of fields in serialized output.

    # ---------------------------
    # Custom Serialization Rule
    # ---------------------------
    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """Removes null fields from serialized output."""
        return {key: value for key, value in data.items() if value is not None}

# ---------------------------
# Schema Instances
# ---------------------------
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
