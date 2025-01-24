from models import db
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime


class Customer(db.Model):
    __tablename__ = 'customers'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name cannot be null
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Unique email with index
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Unique phone with index
    created_at = db.Column(db.DateTime, default=func.current_timestamp(), index=True)  # Indexed for queries
    updated_at = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)  # Indexed for soft-deletion queries

    # Table-level constraints
    __table_args__ = (
        CheckConstraint("LENGTH(phone) >= 7", name="check_phone_length"),  # Ensure minimum phone length
    )

    # Relationships
    orders = relationship('Order', back_populates='customer')
    shopping_cart = relationship('ShoppingCart', back_populates='customer', uselist=False)
    account = relationship('CustomerAccount', back_populates='customer', uselist=False)
    # ---------------------------
    # Soft Deletion Methods
    # ---------------------------
    def soft_delete(self):
        """Marks the customer as deleted without removing it."""
        self.deleted_at = datetime.utcnow()
        db.session.commit()

    def restore(self):
        """Restores a soft-deleted customer."""
        self.deleted_at = None
        db.session.commit()

    # ---------------------------
    # JSON Serialization
    # ---------------------------
    def to_dict(self):
        """Converts the model instance into a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "account": self.account.to_dict() if self.account else None,  # Include account details if present
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        """Defines how the object is represented as a string."""
        return f"<Customer {self.name} - {self.email}>"

    # ---------------------------
    # Validation Methods
    # ---------------------------
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError("Invalid email format.")

    @staticmethod
    def validate_phone(phone):
        """Validate phone number format (e.g., length, digits only)."""
        if not phone.isdigit() or len(phone) < 7:
            raise ValueError("Invalid phone number format.")
