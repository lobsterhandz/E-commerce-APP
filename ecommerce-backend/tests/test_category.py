import unittest
from unittest.mock import patch
from app import create_app
from models import db
from services.category_service import CategoryService


class TestCategoryEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mocked token for authentication

    @patch("services.category_service.CategoryService.get_all_categories")
    def test_get_all_categories_success(self, mock_get_all_categories):
        """Test fetching all categories successfully."""
        # Mock return value
        mock_get_all_categories.return_value = [
            {"id": 1, "name": "Electronics"},
            {"id": 2, "name": "Clothing"},
        ]
        # Perform GET request
        response = self.client.get("/categories", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("Electronics", response.get_data(as_text=True))

    @patch("services.category_service.CategoryService.get_all_categories")
    def test_get_all_categories_empty(self, mock_get_all_categories):
        """Test fetching all categories when the list is empty."""
        mock_get_all_categories.return_value = []
        response = self.client.get("/categories", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)  # Expecting an empty list

    @patch("services.category_service.CategoryService.get_category_by_id")
    def test_get_category_success(self, mock_get_category_by_id):
        """Test fetching a category by ID successfully."""
        # Mock return value
        mock_get_category_by_id.return_value = {"id": 1, "name": "Electronics"}
        # Perform GET request
        response = self.client.get("/categories/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Electronics", response.get_data(as_text=True))

    @patch("services.category_service.CategoryService.get_category_by_id")
    def test_get_category_not_found(self, mock_get_category_by_id):
        """Test fetching a category when the category does not exist."""
        # Mock side effect to simulate not found
        mock_get_category_by_id.side_effect = ValueError("Category not found.")
        # Perform GET request
        response = self.client.get("/categories/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Category not found", response.get_data(as_text=True))

    @patch("services.category_service.CategoryService.create_category")
    def test_create_category_success(self, mock_create_category):
        """Test creating a new category successfully."""
        # Mock return value
        mock_create_category.return_value = {"id": 3, "name": "Toys"}
        # Perform POST request
        response = self.client.post(
            "/categories",
            json={"name": "Toys"},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertIn("Toys", response.get_data(as_text=True))

    @patch("services.category_service.CategoryService.create_category")
    def test_create_category_invalid_data(self, mock_create_category):
        """Test creating a category with invalid data."""
        # Mock side effect to simulate validation error
        mock_create_category.side_effect = ValueError("Invalid category data.")
        # Perform POST request
        response = self.client.post(
            "/categories",
            json={"name": ""},  # Invalid data
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid category data", response.get_data(as_text=True))

    @patch("services.category_service.CategoryService.update_category")
    def test_update_category_success(self, mock_update_category):
        """Test updating a category successfully."""
        # Mock return value
        mock_update_category.return_value = {"id": 1, "name": "Electronics & Gadgets"}
        # Perform PUT request
        response = self.client.put(
            "/categories/1",
            json={"name": "Electronics & Gadgets"},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Electronics & Gadgets", response.get_data(as_text=True))

    @patch("services.category_service.CategoryService.update_category")
    def test_update_category_not_found(self, mock_update_category):
        """Test updating a category when the category does not exist."""
        # Mock side effect to simulate not found
        mock_update_category.side_effect = ValueError("Category not found.")
        # Perform PUT request
        response = self.client.put(
            "/categories/999",
            json={"name": "Nonexistent Category"},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Category not found", response.get_data(as_text=True))

    @patch("services.category_service.CategoryService.delete_category")
    def test_delete_category_success(self, mock_delete_category):
        """Test deleting a category successfully."""
        # Mock return value
        mock_delete_category.return_value = True
        # Perform DELETE request
        response = self.client.delete("/categories/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Category deleted successfully", response.get_data(as_text=True))

    @patch("services.category_service.CategoryService.delete_category")
    def test_delete_category_not_found(self, mock_delete_category):
        """Test deleting a category when the category does not exist."""
        # Mock side effect to simulate not found
        mock_delete_category.side_effect = ValueError("Category not found.")
        # Perform DELETE request
        response = self.client.delete("/categories/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Category not found", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
