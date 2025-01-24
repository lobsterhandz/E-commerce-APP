from models import db
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from werkzeug.exceptions import BadRequest


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_order = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=func.current_timestamp(), index=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('price_at_order >= 0', name='check_price_at_order_non_negative'),
    )

    # Relationships
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')
    # ---------------------------
    # Soft Deletion Methods
    # ---------------------------
    def soft_delete(self):
        try:
            self.deleted_at = func.now()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise BadRequest(f"Error during soft deletion: {str(e)}")

    def restore(self):
        try:
            self.deleted_at = None
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise BadRequest(f"Error during restoration: {str(e)}")

    # ---------------------------
    # Subtotal Calculation
    # ---------------------------
    def calculate_subtotal(self):
        if self.quantity <= 0 or self.price_at_order < 0:
            raise ValueError("Invalid quantity or price_at_order for subtotal calculation.")
        self.subtotal = self.quantity * self.price_at_order

    # ---------------------------
    # JSON Serialization
    # ---------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price_at_order": self.price_at_order,
            "subtotal": self.subtotal,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "product": {
                "id": self.product.id,
                "name": self.product.name,
                "price": self.price_at_order
            } if self.product else None,
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        return f"<OrderItem OrderID {self.order_id} - ProductID {self.product_id} - Quantity {self.quantity} - Subtotal {self.subtotal}>"
