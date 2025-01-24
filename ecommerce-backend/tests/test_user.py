import os
import unittest
from flask import json
from unittest.mock import patch
from app import create_app, db
from models import User
from utils.utils import encode_token
from werkzeug.security import generate_password_hash


class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up test variables."""
        self.app = create_app("testing")  # Use the testing configuration
        self.client = self.app.test_client()
        self.headers = {}
        self.test_user_data = {
            "username": "testuser",
            "password": "testpassword",
            "email": "Test@test.com",
            "role": "user"
        }

        with self.app.app_context():
            db.create_all()
            self.seed_test_data()

    def tearDown(self):
        """Clean up the database after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def seed_test_data(self):
        """Seed the database with a test user and generate a token."""
        user = User(
            username=self.test_user_data["username"],
            email="testuser@example.com",
            role=self.test_user_data["role"],
            password_hash=generate_password_hash("password123")
        )
        user.set_password(self.test_user_data["password"])  # Hash the password
        db.session.add(user)
        db.session.commit()

        # Generate token for the test user
        token = encode_token(user.id, user.role)
        self.headers = {"Authorization": f"Bearer {token}"}

    @patch("utils.utils.jwt_required", lambda f: f)  # Mock JWT validation
    @patch("utils.utils.role_required", lambda role: lambda f: f)  # Mock role validation
    def test_get_user_success(self):
        """Test fetching a user by ID successfully."""
        response = self.client.get(
            "/1",  # Adjusted to match the new route structure
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.json)
        self.assertEqual(response.json["username"], self.test_user_data["username"])

    @patch("utils.utils.jwt_required", lambda f: f)  # Mock JWT validation
    @patch("utils.utils.role_required", lambda role: lambda f: f)  # Mock role validation
    def test_get_user_not_found(self):
        """Test fetching a user by ID when the user does not exist."""
        response = self.client.get(
            "/999",  # Nonexistent user ID
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "User not found.")

    @patch("utils.utils.jwt_required", lambda f: f)  # Mock JWT validation
    @patch("utils.utils.role_required", lambda role: lambda f: f)  # Mock role validation
    def test_delete_user_success(self):
        """Test deleting a user successfully."""
        response = self.client.delete(
            "/1",  # Adjusted to match the new route structure
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "User deleted successfully.")

    @patch("utils.utils.jwt_required", lambda f: f)  # Mock JWT validation
    @patch("utils.utils.role_required", lambda role: lambda f: f)  # Mock role validation
    def test_delete_user_not_found(self):
        """Test deleting a user that does not exist."""
        response = self.client.delete(
            "/999",  # Nonexistent user ID
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "User not found.")


if __name__ == "__main__":
    unittest.main()
