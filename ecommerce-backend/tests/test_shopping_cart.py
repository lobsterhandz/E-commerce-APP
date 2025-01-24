import unittest
from unittest.mock import patch
from app import create_app
from models import db
from services.shopping_cart_service import ShoppingCartService


class TestShoppingCart(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mocked token for authentication

    @patch("services.shopping_cart_service.ShoppingCartService.get_cart_by_customer")
    def test_get_cart_success(self, mock_get_cart_by_customer):
        """Test fetching the shopping cart successfully."""
        mock_get_cart_by_customer.return_value = {
            "id": 1,
            "customer_id": 1,
            "items": [
                {"product_id": 1, "quantity": 2, "subtotal": 39.98},
                {"product_id": 2, "quantity": 1, "subtotal": 19.99},
            ]
        }
        response = self.client.get("/api/shopping_cart", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.get_json())

    @patch("services.shopping_cart_service.ShoppingCartService.clear_cart")
    def test_clear_cart_success(self, mock_clear_cart):
        """Test clearing the shopping cart successfully."""
        mock_clear_cart.return_value = True
        response = self.client.delete("/api/shopping_cart", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cart cleared successfully", response.get_data(as_text=True))

    @patch("services.shopping_cart_service.ShoppingCartService.checkout_cart")
    def test_checkout_cart_success(self, mock_checkout_cart):
        """Test checking out the shopping cart successfully."""
        mock_checkout_cart.return_value = {
            "customer_id": 1,
            "items": [
                {"product_id": 1, "quantity": 2, "subtotal": 39.98},
                {"product_id": 2, "quantity": 1, "subtotal": 19.99},
            ],
            "total_price": 59.97
        }
        response = self.client.post("/api/shopping_cart/checkout", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_price", response.get_json())

    @patch("services.shopping_cart_service.ShoppingCartService.get_cart_by_customer")
    def test_get_cart_empty(self, mock_get_cart_by_customer):
        """Test fetching the shopping cart when it is empty."""
        mock_get_cart_by_customer.return_value = {"id": 1, "customer_id": 1, "items": []}
        response = self.client.get("/api/shopping_cart", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json().get("items")), 0)

    @patch("services.shopping_cart_service.ShoppingCartService.checkout_cart")
    def test_checkout_cart_empty(self, mock_checkout_cart):
        """Test checking out an empty shopping cart."""
        mock_checkout_cart.side_effect = ValueError("Cart is empty. Cannot proceed to checkout.")
        response = self.client.post("/api/shopping_cart/checkout", headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cart is empty", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
