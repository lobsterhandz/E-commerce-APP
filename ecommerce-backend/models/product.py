from models import db
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Product(db.Model):
    __tablename__ = 'products'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    # Table-level constraints
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_non_negative'),  # Ensure non-negative price
        CheckConstraint('stock_quantity >= 0', name='check_stock_quantity_non_negative'),  # Ensure non-negative stock
    )

    # Relationships
    category = relationship('Category', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')
    shopping_cart_items = relationship('ShoppingCartItem', back_populates='product')
    # ---------------------------
    # Soft Deletion
    # ---------------------------
    def soft_delete(self):
        """Marks the product as deleted without removing it."""
        self.deleted_at = datetime.utcnow()
        db.session.commit()

    # ---------------------------
    # Restore Deleted Product
    # ---------------------------
    def restore(self):
        """Restores a soft-deleted product."""
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
            "price": float(self.price),  # Ensure price is returned as a float
            "stock_quantity": self.stock_quantity,
            "category": self.category.name if self.category else None,  # Include category name if available
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    # ---------------------------
    # Active Products Query
    # ---------------------------
    @staticmethod
    def active_products():
        """Returns products that are not soft-deleted."""
        return Product.query.filter_by(deleted_at=None)

    # ---------------------------
    # Validation Methods
    # ---------------------------
    @staticmethod
    def validate_name(name):
        """Validate product name is unique."""
        if Product.query.filter_by(name=name).first():
            raise ValueError("Product name must be unique.")

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        """Defines how the object is represented as a string."""
        return f"<Product {self.name} - ${float(self.price)}>"

