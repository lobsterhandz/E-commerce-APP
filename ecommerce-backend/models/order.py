from models import db
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Table-level constraints
    __table_args__ = (
        CheckConstraint('total_price >= 0', name='check_non_negative_total_price'),
    )

    # Relationships
    customer = relationship('Customer', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")

    # ---------------------------
    # Soft Deletion
    # ---------------------------
    def soft_delete(self):
        """Marks the order as deleted without removing it."""
        self.deleted_at = datetime.utcnow()  # Use client-side timestamp
        db.session.commit()

    # ---------------------------
    # Restore Deleted Order
    # ---------------------------
    def restore(self):
        """Restores a soft-deleted order."""
        self.deleted_at = None
        db.session.commit()

    # ---------------------------
    # JSON Serialization
    # ---------------------------
    def to_dict(self):
        """Converts the model instance into a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "total_price": self.total_price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "customer": {
                "id": self.customer.id,
                "name": self.customer.name,
                "email": self.customer.email
            } if self.customer else None,
            "items": [item.to_dict() for item in self.items] if self.items else []
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        """Defines how the object is represented as a string."""
        return f"<Order {self.id} - ${self.total_price}>"
