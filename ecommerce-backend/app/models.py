from app.database import db
from sqlalchemy.orm import relationship

class Customer(db.Model):
    __tablename__ = 'customers'  # Explicitly define table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

    # One-to-Many relationship with Order
    orders = relationship('Order', backref='customer', lazy=True)

class CustomerAccount(db.Model):
    __tablename__ = 'customer_accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)  # Reference 'customers'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_level = db.Column(db.Integer, nullable=False, default=0)

    # One-to-Many relationship with OrderItem
    order_items = relationship('OrderItem', backref='product', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)  # Reference 'customers'

    # One-to-Many relationship with OrderItem
    order_items = relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # Reference 'orders'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Reference 'products'
    quantity = db.Column(db.Integer, nullable=False)
