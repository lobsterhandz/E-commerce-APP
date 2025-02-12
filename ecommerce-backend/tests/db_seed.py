import json
import os
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from models import db, User, Category, Product, Customer, Order, OrderItem, ShoppingCart, ShoppingCartItem, CustomerAccount

def seed_all():
    """Seed the database with test data from mock_data.json"""
    print("🌱 Seeding database with test data...")

    json_path = os.path.join(os.path.dirname(__file__), "../mock_data.json")

    with open(json_path, "r") as file:
        data = json.load(file)

    try:
        # Seed categories
        for cat in data["categories"]:
            db.session.add(Category(id=cat["id"], name=cat["name"]))

        # Seed users
        for user in data["users"]:
            db.session.add(
                User(
                    username=user["username"],
                    email=user["email"],
                    role=user["role"],
                    is_active=user["is_active"],
                    password_hash=generate_password_hash(user["password"]),
                )
            )

        # Seed customers
        for cust in data["customers"]:
            db.session.add(Customer(id=cust["id"], name=cust["name"], email=cust["email"], phone=cust["phone"]))

        # Seed products
        for prod in data["products"]:
            db.session.add(
                Product(
                    id=prod["id"],
                    name=prod["name"],
                    price=prod["price"],
                    stock_quantity=prod["stock_quantity"],
                    category_id=prod["category_id"],
                )
            )

        # Seed orders
        for order in data["orders"]:
            db.session.add(
                Order(
                    id=order["id"],
                    customer_id=order["customer_id"],
                    total_price=order["total_price"],
                )
            )

        # Seed order items
        for item in data["order_items"]:
            db.session.add(
                OrderItem(
                    id=item["id"],
                    order_id=item["order_id"],
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    price_at_order=item["price_at_order"],
                    subtotal=item["subtotal"],
                )
            )

        # Seed shopping carts
        for cart in data["shopping_carts"]:
            db.session.add(ShoppingCart(id=cart["id"], customer_id=cart["customer_id"]))

        # Seed shopping cart items
        for sci in data["shopping_cart_items"]:
            db.session.add(
                ShoppingCartItem(
                    id=sci["id"],
                    cart_id=sci["cart_id"],
                    product_id=sci["product_id"],
                    quantity=sci["quantity"],
                    price=sci["price"],
                    subtotal=sci["subtotal"],
                )
            )

        # Seed customer accounts
        for ca in data["customer_accounts"]:
            db.session.add(
                CustomerAccount(
                    id=ca["id"],
                    username=ca["username"],
                    password_hash=ca["password_hash"],
                    customer_id=ca["customer_id"],
                )
            )

        db.session.commit()
        print("✅ Database seeding complete.")

    except IntegrityError as e:
        db.session.rollback()
        print(f"⚠️ Seeding failed: {e}")

if __name__ == "__main__":
    from app import create_app
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        seed_all()
