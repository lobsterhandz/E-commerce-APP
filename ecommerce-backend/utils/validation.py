# app/utils/validation.py
import re
from flask import jsonify

def validate_email(email):
    """Validates an email address format."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        raise ValueError("Invalid email format")


def validate_required_fields(data, fields):
    """Validates that required fields are present in data."""
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
 ##add phone number validation

 def validate_phone_number(phone_number):
    """Validates a phone number format."""
    phone_number_regex = r'^\+?1?\d{9,15}$'
    if not re.match(phone_number_regex, phone_number):
        raise ValueError("Invalid phone number format")
        