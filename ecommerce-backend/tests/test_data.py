import os
import sys
import json
from flask import jsonify
from unittest.mock import patch
from app import create_app
from models import db, User, Category, Product, Order, OrderItem, ShoppingCart, ShoppingCartItem, Customer

MOCK_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock_data.json"))

def load_mock_data():
    """Load mock data from JSON file."""
    try:
        with open(MOCK_DATA_PATH, "r") as file:
            return json.load(file)
    except Exception as e:
        raise RuntimeError(f"Failed to load mock data: {e}")

def seed_users(data):
    """Seed user data."""
    for user_data in data:
        user = User(
            username=user_data["username"],
            email=user_data["email"],  # Add this line to include the email field
            role=user_data["role"],
            is_active=user_data["is_active"],
        )
        user.set_password(user_data["password"])  # Hash the password
        db.session.add(user)
    db.session.commit()


def seed_categories(data):
    """Seed category data."""
    for category_data in data:
        category = Category(id=category_data["id"], name=category_data["name"])
        db.session.add(category)
    db.session.commit()


def seed_products(data):
    """Seed product data."""
    for product_data in data:
        product = Product(
            id=product_data["id"],
            name=product_data["name"],
            price=product_data["price"],
            stock_quantity=product_data["stock_quantity"],
            category_id=product_data["category_id"],
        )
        db.session.add(product)
    db.session.commit()


def seed_customers(data):
    """Seed customer data."""
    for customer_data in data:
        customer = Customer(
            id=customer_data["id"],
            name=customer_data['name'],
            email=customer_data["email"],
            phone=customer_data["phone"],
        )
        db.session.add(customer)
    db.session.commit()


def seed_orders(data):
    """Seed order data."""
    for order_data in data:
        order = Order(
            id=order_data["id"],
            customer_id=order_data["customer_id"],
            total_price=order_data["total_price"],
            created_at=order_data["created_at"],
        )
        db.session.add(order)
        db.session.commit()  # Commit to get the order ID for foreign key

        # Seed order items
        for item_data in order_data["items"]:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                price_at_order=item_data["price_at_order"],
                subtotal=item_data["subtotal"],
            )
            db.session.add(order_item)
    db.session.commit()


def seed_shopping_carts(data):
    """Seed shopping cart data."""
    for cart_data in data:
        shopping_cart = ShoppingCart(
            id=cart_data["id"],
            customer_id=cart_data["customer_id"],
        )
        db.session.add(shopping_cart)
        db.session.commit()  # Commit to get the shopping cart ID

        # Seed shopping cart items
        for item_data in cart_data["items"]:
            shopping_cart_item = ShoppingCartItem(
                cart_id=shopping_cart.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                subtotal=item_data["subtotal"],
            )
            db.session.add(shopping_cart_item)
    db.session.commit()


def seed_all():
    """Seed all data into the database."""
    mock_data = load_mock_data()
    print("Seeding users...")
    seed_users(mock_data["users"])
    print("Seeding categories...")
    seed_categories(mock_data["categories"])
    print("Seeding products...")
    seed_products(mock_data["products"])
    print("Seeding customers...")
    seed_customers(mock_data["customers"])
    print("Seeding orders...")
    seed_orders(mock_data["orders"])
    print("Seeding shopping carts...")
    seed_shopping_carts(mock_data["shopping_carts"])
    print("Seeding complete!")


def mock_jwt_required(func):
    """Mock JWT decorator for testing without requiring a token."""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


if __name__ == "__main__":
    app = create_app("testing")  # Use "testing" configuration for seeding
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Patch JWT decorators to skip token validation during tests
        with patch("utils.utils.jwt_required", mock_jwt_required), patch("utils.utils.role_required", mock_jwt_required):
            seed_all()
