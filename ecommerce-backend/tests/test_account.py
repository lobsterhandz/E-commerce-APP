# tests/test_account.py
import unittest
from app import app, db
from app.models import Customer, CustomerAccount

class CustomerAccountTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the test client and create the database tables
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()
        
        # Add a test customer to associate accounts with
        self.customer = Customer(name="Test Customer", email="testcustomer@example.com", phone_number="+1234567890")
        with app.app_context():
            db.session.add(self.customer)
            db.session.commit()

    def tearDown(self):
        # Clean up and drop the tables after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_customer_account(self):
        # Test creating a new customer account
        response = self.app.post('/customer_account', json={
            'username': 'testuser',
            'password': 'testpassword',
            'customer_id': self.customer.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Customer account created successfully', response.data)

    def test_create_customer_account_missing_fields(self):
        # Test missing required fields during account creation
        response = self.app.post('/customer_account', json={
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing required fields', response.data)

    def test_create_customer_account_nonexistent_customer(self):
        # Test creating a customer account with a nonexistent customer ID
        response = self.app.post('/customer_account', json={
            'username': 'testuser',
            'password': 'testpassword',
            'customer_id': 999  # Nonexistent customer ID
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Customer not found', response.data)

    def test_read_customer_account(self):
        # Add a customer account for the test
        account = CustomerAccount(username="testuser", password="testpassword", customer_id=self.customer.id)
        with app.app_context():
            db.session.add(account)
            db.session.commit()
        
        # Test reading the customer account
        response = self.app.get(f'/customer_account/{account.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data)

    def test_update_customer_account(self):
        # Add a customer account for the test
        account = CustomerAccount(username="testuser", password="testpassword", customer_id=self.customer.id)
        with app.app_context():
            db.session.add(account)
            db.session.commit()
        
        # Test updating the customer account
        response = self.app.put(f'/customer_account/{account.id}', json={
            'username': 'updateduser'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Customer account updated successfully', response.data)

    def test_delete_customer_account(self):
        # Add a customer account for the test
        account = CustomerAccount(username="testuser", password="testpassword", customer_id=self.customer.id)
        with app.app_context():
            db.session.add(account)
            db.session.commit()
        
        # Test deleting the customer account
        response = self.app.delete(f'/customer_account/{account.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Customer account deleted successfully', response.data)

    def test_delete_nonexistent_customer_account(self):
        # Test deleting a customer account that does not exist
        response = self.app.delete('/customer_account/999')  # Nonexistent account ID
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Customer account not found', response.data)

if __name__ == '__main__':
    unittest.main()