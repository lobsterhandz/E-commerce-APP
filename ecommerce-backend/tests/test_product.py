# tests/test_product.py
import unittest
from app import app, db
from app.models import Product

class ProductTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the test client and create the database tables
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up and drop the tables after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_product(self):
        # Test creating a new product
        response = self.app.post('/product', json={
            'name': 'Test Product',
            'price': 20.0,
            'stock_level': 50
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Product created successfully', response.data)

    def test_create_product_missing_fields(self):
        # Test creating a product with missing required fields
        response = self.app.post('/product', json={
            'name': 'Test Product'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing required fields', response.data)

    def test_create_product_negative_price(self):
        # Test creating a product with a negative price
        response = self.app.post('/product', json={
            'name': 'Test Product',
            'price': -10.0,
            'stock_level': 50
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Price must be positive', response.data)

    def test_read_product(self):
        # Add a product for the test
        product = Product(name='Test Product', price=20.0, stock_level=50)
        with app.app_context():
            db.session.add(product)
            db.session.commit()

        # Test reading the product details
        response = self.app.get(f'/product/{product.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product', response.data)

    def test_update_product(self):
        # Add a product for the test
        product = Product(name='Test Product', price=20.0, stock_level=50)
        with app.app_context():
            db.session.add(product)
            db.session.commit()

        # Test updating the product details
        response = self.app.put(f'/product/{product.id}', json={
            'price': 25.0,
            'stock_level': 100
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product updated successfully', response.data)

    def test_delete_product(self):
        # Add a product for the test
        product = Product(name='Test Product', price=20.0, stock_level=50)
        with app.app_context():
            db.session.add(product)
            db.session.commit()

        # Test deleting the product
        response = self.app.delete(f'/product/{product.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product deleted successfully', response.data)

    def test_delete_nonexistent_product(self):
        # Test deleting a product that does not exist
        response = self.app.delete('/product/999')  # Nonexistent product ID
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Product not found', response.data)

if __name__ == '__main__':
    unittest.main()
