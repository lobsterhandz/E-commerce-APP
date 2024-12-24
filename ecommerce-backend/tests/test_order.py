# tests/test_order.py
import unittest
from app import app, db
from app.models import Customer, Product, Order, OrderItem
from datetime import datetime

class OrderTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the test client and create the database tables
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()
            # Create a customer for order association
            self.customer = Customer(name="Test Customer", email="testcustomer@example.com", phone_number="+1234567890")
            db.session.add(self.customer)
            # Create a product to add to orders
            self.product = Product(name="Test Product", price=10.0, stock_level=100)
            db.session.add(self.product)
            db.session.commit()

    def tearDown(self):
        # Clean up and drop the tables after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_order(self):
        # Test creating a new order
        response = self.app.post('/order', json={
            'customer_id': self.customer.id,
            'order_items': [
                {
                    'product_id': self.product.id,
                    'quantity': 2
                }
            ]
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Order created successfully', response.data)

    def test_create_order_insufficient_stock(self):
        # Test creating an order with a quantity greater than available stock
        response = self.app.post('/order', json={
            'customer_id': self.customer.id,
            'order_items': [
                {
                    'product_id': self.product.id,
                    'quantity': 200  # Insufficient stock
                }
            ]
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Insufficient stock', response.data)

    def test_read_order(self):
        # Add an order for the test
        order = Order(order_date=datetime.utcnow(), customer_id=self.customer.id)
        with app.app_context():
            db.session.add(order)
            db.session.flush()
            order_item = OrderItem(order_id=order.id, product_id=self.product.id, quantity=2)
            db.session.add(order_item)
            db.session.commit()
        
        # Test reading the order details
        response = self.app.get(f'/order/{order.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product', response.data)

    def test_update_order(self):
        # Add an order for the test
        order = Order(order_date=datetime.utcnow(), customer_id=self.customer.id)
        with app.app_context():
            db.session.add(order)
            db.session.flush()
            order_item = OrderItem(order_id=order.id, product_id=self.product.id, quantity=2)
            db.session.add(order_item)
            db.session.commit()
        
        # Test updating the order
        response = self.app.put(f'/order/{order.id}', json={
            'order_items': [
                {
                    'product_id': self.product.id,
                    'quantity': 1
                }
            ]
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Order updated successfully', response.data)

    def test_delete_order(self):
        # Add an order for the test
        order = Order(order_date=datetime.utcnow(), customer_id=self.customer.id)
        with app.app_context():
            db.session.add(order)
            db.session.flush()
            order_item = OrderItem(order_id=order.id, product_id=self.product.id, quantity=2)
            db.session.add(order_item)
            db.session.commit()
        
        # Test deleting the order
        response = self.app.delete(f'/order/{order.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Order deleted successfully', response.data)

    def test_delete_nonexistent_order(self):
        # Test deleting an order that does not exist
        response = self.app.delete('/order/999')  # Nonexistent order ID
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Order not found', response.data)

if __name__ == '__main__':
    unittest.main()