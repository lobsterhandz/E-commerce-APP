from marshmallow import Schema, fields, validate, post_dump


class UserSchema(Schema):
    # Fields
    id = fields.Int(dump_only=True)

    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=80, error="Username must be between 3 and 80 characters."),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error="Username can only contain letters, numbers, and underscores.")
        ]
    )

    email = fields.Email(
        required=True,
        error_messages={"required": "Email is required.", "invalid": "Invalid email format."}
    )

    password = fields.Str(
        required=True,
        load_only=True,  # Do not expose password in responses
        validate=validate.Length(min=6, error="Password must be at least 6 characters long.")
    )

    role = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['super_admin', 'admin', 'user'],
            error="Role must be one of 'super_admin', 'admin', or 'user'."
        )
    )

    created_at = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M:%S")

    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Preserve field order in serialized output

    # ---------------------------
    # Custom Serialization Rules
    # ---------------------------
    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """Remove null fields from the serialized output."""
        return {key: value for key, value in data.items() if value is not None}


# Single user schema
user_schema = UserSchema()

# Multiple users schema
users_schema = UserSchema(many=True)
