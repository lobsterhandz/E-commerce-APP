from marshmallow import Schema, fields, validate, post_dump


class CustomerAccountSchema(Schema):
    # Fields
    id = fields.Int(dump_only=True)

    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50)
    )

    password = fields.Str(
        required=True,
        load_only=True,  # Exclude password from being returned in the response
        validate=validate.Length(min=6, max=128)
    )

    customer_id = fields.Int(
        required=True,
        description="ID of the associated customer."
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)  # Added updated_at field
    deleted_at = fields.DateTime(dump_only=True)  # Added soft delete support

    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Preserve field order in JSON output

    # ---------------------------
    # Custom Serialization Rules
    # ---------------------------
    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """Remove null fields from the serialized output."""
        return {key: value for key, value in data.items() if value is not None}


# Example Usage
customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)
