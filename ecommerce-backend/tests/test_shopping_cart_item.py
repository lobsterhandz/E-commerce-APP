import unittest
from app import create_app
from models import db, ShoppingCartItem, ShoppingCart, Product, User
from services.shopping_cart_service import ShoppingCartService
from flask import Flask


class TestShoppingCartItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        # Seed initial data
        cls.seed_data()

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    @classmethod
    def seed_data(cls):
        """Seed initial data for testing."""
        user = User(username="test_user", password="test_password")
        user.set_password("test_password")
        db.session.add(user)

        product = Product(name="Test Product", price=10.99, stock=100)
        db.session.add(product)

        cart = ShoppingCart(user_id=1)
        db.session.add(cart)

        cart_item = ShoppingCartItem(cart_id=1, product_id=1, quantity=2, subtotal=21.98)
        db.session.add(cart_item)

        db.session.commit()

    def setUp(self):
        """Set up for individual tests."""
        self.service = ShoppingCartService()

    def tearDown(self):
        """Rollback changes after each test."""
        db.session.rollback()

    # ------------------------------------
    # Model Layer Tests
    # ------------------------------------
    def test_create_shopping_cart_item(self):
        """Test creating a shopping cart item."""
        cart_item = ShoppingCartItem(cart_id=1, product_id=1, quantity=3, subtotal=32.97)
        db.session.add(cart_item)
        db.session.commit()

        self.assertEqual(cart_item.cart_id, 1)
        self.assertEqual(cart_item.quantity, 3)
        self.assertEqual(cart_item.subtotal, 32.97)

    def test_update_shopping_cart_item(self):
        """Test updating a shopping cart item's quantity."""
        cart_item = ShoppingCartItem.query.first()
        cart_item.update_quantity(5)

        self.assertEqual(cart_item.quantity, 5)
        self.assertEqual(cart_item.subtotal, 54.95)

    def test_delete_shopping_cart_item(self):
        """Test deleting a shopping cart item."""
        cart_item = ShoppingCartItem.query.first()
        cart_item.delete_item()

        self.assertIsNone(ShoppingCartItem.query.get(cart_item.id))

    # ------------------------------------
    # Service Layer Tests
    # ------------------------------------
    def test_add_item_to_cart(self):
        """Test adding an item to the shopping cart via service."""
        item = self.service.add_item_to_cart(customer_id=1, product_id=1, quantity=2)
        self.assertEqual(item.quantity, 4)  # Existing quantity is 2; adding 2 more
        self.assertEqual(item.subtotal, 43.96)

    def test_remove_item_from_cart(self):
        """Test removing an item from the shopping cart via service."""
        self.service.remove_item_from_cart(customer_id=1, product_id=1)
        cart_item = ShoppingCartItem.query.filter_by(cart_id=1, product_id=1).first()
        self.assertIsNone(cart_item)

    def test_clear_cart(self):
        """Test clearing the shopping cart via service."""
        self.service.clear_cart(customer_id=1)
        cart_items = ShoppingCartItem.query.filter_by(cart_id=1).all()
        self.assertEqual(len(cart_items), 0)

    def test_checkout_cart(self):
        """Test the checkout process."""
        summary = self.service.checkout_cart(customer_id=1)

        self.assertEqual(summary["customer_id"], 1)
        self.assertEqual(summary["total_price"], 21.98)
        self.assertEqual(len(summary["items"]), 1)

    # ------------------------------------
    # Route Layer Tests
    # ------------------------------------
    def test_get_shopping_cart_items(self):
        """Test fetching shopping cart items via route."""
        response = self.client.get("/shopping_cart_items/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json)

    def test_add_shopping_cart_item_route(self):
        """Test adding a shopping cart item via route."""
        data = {"cart_id": 1, "product_id": 1, "quantity": 3, "subtotal": 32.97}
        response = self.client.post("/shopping_cart_items/", json=data)
        self.assertEqual(response.status_code, 201)

        cart_item = ShoppingCartItem.query.filter_by(cart_id=1, product_id=1).first()
        self.assertEqual(cart_item.quantity, 5)  # Existing quantity + 3

    def test_delete_shopping_cart_item_route(self):
        """Test deleting a shopping cart item via route."""
        response = self.client.delete("/shopping_cart_items/1")
        self.assertEqual(response.status_code, 204)

        cart_item = ShoppingCartItem.query.get(1)
        self.assertIsNone(cart_item)
    # ------------------------------------
    # Schema Validation Tests
    # ------------------------------------
    def test_schema_serialization(self):
        """Test serialization of ShoppingCartItem."""
        cart_item = ShoppingCartItem.query.first()
        schema = ShoppingCartItemSchema()
        serialized = schema.dump(cart_item)
        self.assertIn("cart_id", serialized)
        self.assertIn("product_id", serialized)
        self.assertIn("quantity", serialized)
        self.assertIn("subtotal", serialized)

    def test_schema_deserialization_valid(self):
        """Test deserialization of valid ShoppingCartItem data."""
        data = {"cart_id": 1, "product_id": 1, "quantity": 4}
        schema = ShoppingCartItemSchema()
        deserialized = schema.load(data)
        self.assertEqual(deserialized["cart_id"], 1)
        self.assertEqual(deserialized["product_id"], 1)
        self.assertEqual(deserialized["quantity"], 4)

    def test_schema_deserialization_invalid_quantity(self):
        """Test deserialization with an invalid quantity (less than 1)."""
        data = {"cart_id": 1, "product_id": 1, "quantity": 0}
        schema = ShoppingCartItemSchema()
        with self.assertRaises(Exception) as context:
            schema.load(data)
        self.assertIn("Quantity must be at least 1.", str(context.exception))

    def test_schema_deserialization_missing_fields(self):
        """Test deserialization with missing required fields."""
        data = {"product_id": 1, "quantity": 4}  # Missing `cart_id`
        schema = ShoppingCartItemSchema()
        with self.assertRaises(Exception) as context:
            schema.load(data)
        self.assertIn("Cart ID is required.", str(context.exception))
class TestShoppingCartItemRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a test Flask application."""
        cls.app = Flask(__name__)
        cls.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        cls.app.config["TESTING"] = True
        cls.app.config["JWT_SECRET_KEY"] = "test_jwt_secret"
        db.init_app(cls.app)

        with cls.app.app_context():
            db.create_all()
            # Seed data
            product = Product(id=1, name="Test Product", price=10.0)
            db.session.add(product)
            db.session.commit()

        cls.client = cls.app.test_client()
        cls.app.register_blueprint(shopping_cart_item_bp, url_prefix="/shopping_cart_items")

    @classmethod
    def tearDownClass(cls):
        """Tear down the test database."""
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_cart_items(self):
        """Test fetching all items in a cart."""
        with self.app.app_context():
            # Add a test item
            item = ShoppingCartItem(cart_id=1, product_id=1, quantity=2, subtotal=20.0)
            db.session.add(item)
            db.session.commit()

        response = self.client.get("/shopping_cart_items/1/items")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_add_item_to_cart(self):
        """Test adding an item to a shopping cart."""
        data = {"product_id": 1, "quantity": 3}
        response = self.client.post("/shopping_cart_items/1/items", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["quantity"], 3)

    def test_update_cart_item(self):
        """Test updating an item's quantity in a shopping cart."""
        with self.app.app_context():
            # Add a test item
            item = ShoppingCartItem(cart_id=1, product_id=1, quantity=2, subtotal=20.0)
            db.session.add(item)
            db.session.commit()

        data = {"quantity": 5}
        response = self.client.put("/shopping_cart_items/1/items/1", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["quantity"], 5)

    def test_remove_cart_item(self):
        """Test removing an item from a shopping cart."""
        with self.app.app_context():
            # Add a test item
            item = ShoppingCartItem(cart_id=1, product_id=1, quantity=2, subtotal=20.0)
            db.session.add(item)
            db.session.commit()

        response = self.client.delete("/shopping_cart_items/1/items/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Item removed successfully.")

if __name__ == "__main__":
    unittest.main()
