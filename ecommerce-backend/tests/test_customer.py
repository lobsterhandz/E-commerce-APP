# tests/test_customer.py
import unittest
from app import app, db
from app.models import Customer

class CustomerTestCase(unittest.TestCase):
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

    def test_create_customer(self):
        # Test creating a new customer
        response = self.app.post('/customer', json={
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'phone_number': '+1234567890'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Customer created successfully', response.data)

    def test_create_customer_missing_fields(self):
        # Test missing required fields during customer creation
        response = self.app.post('/customer', json={
            'name': 'John Doe'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing required fields', response.data)

    def test_create_customer_invalid_email(self):
        # Test creating a customer with an invalid email address
        response = self.app.post('/customer', json={
            'name': 'John Doe',
            'email': 'invalid-email',
            'phone_number': '+1234567890'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid email format', response.data)

    def test_read_customer(self):
        # Add a customer for the test
        customer = Customer(name='Jane Doe', email='janedoe@example.com', phone_number='+1234567890')
        with app.app_context():
            db.session.add(customer)
            db.session.commit()

        # Test reading the customer details
        response = self.app.get(f'/customer/{customer.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jane Doe', response.data)

    def test_update_customer(self):
        # Add a customer for the test
        customer = Customer(name='Jane Doe', email='janedoe@example.com', phone_number='+1234567890')
        with app.app_context():
            db.session.add(customer)
            db.session.commit()

        # Test updating the customer details
        response = self.app.put(f'/customer/{customer.id}', json={
            'name': 'Jane Smith'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Customer updated successfully', response.data)

    def test_delete_customer(self):
        # Add a customer for the test
        customer = Customer(name='Jane Doe', email='janedoe@example.com', phone_number='+1234567890')
        with app.app_context():
            db.session.add(customer)
            db.session.commit()

        # Test deleting the customer
        response = self.app.delete(f'/customer/{customer.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Customer deleted successfully', response.data)

    def test_delete_nonexistent_customer(self):
        # Test deleting a customer that does not exist
        response = self.app.delete('/customer/999')  # Nonexistent customer ID
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Customer not found', response.data)

if __name__ == '__main__':
    unittest.main()