from models import db
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship

class ShoppingCart(db.Model):
    __tablename__ = 'shopping_carts'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, unique=True)  # One-to-one
    created_at = db.Column(db.DateTime, server_default=func.now(), index=True)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)  # Soft deletion column

    # Relationships
    customer = relationship('Customer', back_populates='shopping_cart')
    items = relationship('ShoppingCartItem', back_populates='cart')
    # ---------------------------
    # Soft Deletion Methods
    # ---------------------------
    def soft_delete(self):
        """Marks the shopping cart as deleted."""
        self.deleted_at = func.now()
        db.session.commit()

    def restore(self):
        """Restores a soft-deleted shopping cart."""
        self.deleted_at = None
        db.session.commit()

    def to_dict(self):
        """Converts the shopping cart to a dictionary."""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "items": [item.to_dict() for item in self.items]  # Include items as dicts
        }

    # ---------------------------
    # Total Calculation
    # ---------------------------
    def calculate_total(self):
        """Calculates the total cost of all items in the cart."""
        return sum(item.subtotal for item in self.items)

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        return f"<ShoppingCart ID: {self.id}, CustomerID: {self.customer_id}>"
