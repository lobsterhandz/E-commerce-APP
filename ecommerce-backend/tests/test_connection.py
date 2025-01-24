import unittest
from app import create_app
from models import db

class TestDatabaseConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def test_database_connection(self):
        """Test if the database connection is successful."""
        with self.app.app_context():
            result = db.session.execute("SELECT 1").scalar()
            self.assertEqual(result, 1)

if __name__ == "__main__":
    unittest.main()
