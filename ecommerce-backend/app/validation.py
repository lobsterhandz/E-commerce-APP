import re

# Function to validate email format
def validate_email(email):
    """
    Validates the format of an email address.
    Raises:
        ValueError: If the email format is invalid.
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError('Invalid email format')


# Function to validate phone number format
def validate_phone_number(phone_number):
    """
    Validates the format of a phone number.
    Supports international numbers in E.164 format.
    Raises:
        ValueError: If the phone number format is invalid.
    """
    if not re.match(r"^\+?[1-9]\d{1,14}$", phone_number):  # E.164 format
        raise ValueError('Invalid phone number format')


# Function to validate required fields are present in the data
def validate_required_fields(data, fields):
    """
    Ensures that all required fields are present in the input data.
    Args:
        data (dict): The input data to validate.
        fields (list): A list of required field names.
    Raises:
        ValueError: If any required fields are missing.
    """
    missing_fields = [field for field in fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")


# Function to validate that a value is a positive float
def validate_positive_float(value, field_name):
    """
    Ensures that a value is a positive float.
    Args:
        value (float or int): The value to validate.
        field_name (str): The name of the field for error messages.
    Raises:
        ValueError: If the value is not a positive number.
    """
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{field_name} must be a positive number")


# Function to validate non-negative integer for fields like stock level
def validate_non_negative_integer(value, field_name):
    """
    Ensures that a value is a non-negative integer.
    Args:
        value (int): The value to validate.
        field_name (str): The name of the field for error messages.
    Raises:
        ValueError: If the value is not a non-negative integer.
    """
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
