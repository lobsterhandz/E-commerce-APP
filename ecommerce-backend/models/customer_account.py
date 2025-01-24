from models import db
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
class CustomerAccount(db.Model):
    __tablename__ = 'customer_accounts'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)  # Indexed for faster lookups
    password_hash = db.Column(db.String(200), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Active status for quick deactivation
    created_at = db.Column(db.DateTime, default=func.current_timestamp(), index=True)
    updated_at = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)  # Indexed for soft-deletion queries

    # Table-level constraints
    __table_args__ = (
        CheckConstraint("LENGTH(username) >= 3 AND LENGTH(username) <= 80", name="check_username_length"),
    )

    # Relationships
    customer = relationship('Customer', back_populates='account')
    # ---------------------------
    # Password Management
    # ---------------------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ---------------------------
    # Soft Deletion Methods
    # ---------------------------
    def soft_delete(self):
        self.deleted_at = func.now()
        self.is_active = False
        db.session.commit()

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        db.session.commit()

    # ---------------------------
    # JSON Serialization
    # ---------------------------
   
    def to_dict(self):
        from datetime import datetime

        def format_datetime(value):
            if isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, str):  # Handle unexpected string
                try:
                    parsed_date = datetime.fromisoformat(value)
                    return parsed_date.isoformat()
                except ValueError:
                    print(f"WARNING: Invalid date string: {value}")
                    return value  # Leave as-is for inspection
            return None

        return {
            "id": self.id,
            "username": self.username,
            "customer_id": self.customer_id,
            "is_active": self.is_active,
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
            "deleted_at": format_datetime(self.deleted_at),
        }



    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        return f"<CustomerAccount {self.username} - CustomerID {self.customer_id}>"

    # ---------------------------
    # Validation Methods
    # ---------------------------
    @staticmethod
    def validate_username(username):
        if len(username) < 3 or len(username) > 80:
            raise ValueError("Username must be between 3 and 80 characters.")
        if not username.isalnum():
            raise ValueError("Username must contain only alphanumeric characters.")
        if CustomerAccount.query.filter(CustomerAccount.username.ilike(username)).first():
            raise ValueError("Username already exists.")
