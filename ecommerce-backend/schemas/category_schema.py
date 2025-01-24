from marshmallow import Schema, fields, validate, post_dump


class CategorySchema(Schema):
    # ---------------------------
    # Fields
    # ---------------------------
    id = fields.Int(dump_only=True)

    name = fields.Str(
        required=True,
        validate=validate.Length(
            min=1,
            max=100,
            error="Category name must be between 1 and 100 characters."
        )
    )

    created_at = fields.DateTime(dump_only=True)  # Automatically set on creation
    updated_at = fields.DateTime(dump_only=True)  # Automatically updated on changes
    deleted_at = fields.DateTime(dump_only=True)  # Tracks soft deletes

    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Ensures fields appear in the defined order.

    # ---------------------------
    # Custom Serialization Rules
    # ---------------------------
    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """
        Removes null fields from the serialized output.

        Args:
            data (dict): Serialized data.
            **kwargs: Additional arguments.

        Returns:
            dict: Data without null fields.
        """
        return {key: value for key, value in data.items() if value is not None}


# ---------------------------
# Example Usage
# ---------------------------
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
