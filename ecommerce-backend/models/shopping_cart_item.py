from models import db
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship

class ShoppingCartItem(db.Model):
    __tablename__ = 'shopping_cart_items'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('shopping_carts.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False, default=0.0)
    subtotal = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Table-level constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_quantity_unique'),
        CheckConstraint('price >= 0', name='check_non_negative_price'),
    )

    # Relationships
    cart = relationship('ShoppingCart', back_populates='items')
    product = relationship('Product', back_populates='shopping_cart_items')

    # ---------------------------
    # Methods
    # ---------------------------
    def to_dict(self):
        """Converts the shopping cart item to a dictionary."""
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "subtotal": self.subtotal,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "product": {
                "id": self.product.id,
                "name": self.product.name,
                "price": self.product.price
            } if self.product else None
        }

    def update_quantity(self, new_quantity):
        """Updates the quantity and recalculates the subtotal."""
        if new_quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        self.quantity = new_quantity
        self.subtotal = self.quantity * self.product.price
        db.session.commit()

    def delete_item(self):
        """Deletes the item from the shopping cart."""
        db.session.delete(self)
        db.session.commit()

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        return f"<ShoppingCartItem CartID: {self.cart_id}, ProductID: {self.product_id}, Quantity: {self.quantity}>"
