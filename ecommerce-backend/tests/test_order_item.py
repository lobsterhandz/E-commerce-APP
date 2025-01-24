import unittest
from unittest.mock import patch
from app import create_app
from models import db
from services.order_item_service import OrderItemService


class TestOrderItemEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mocked token for authentication

    @patch("services.order_item_service.OrderItemService.get_items_by_order_id")
    def test_get_order_items_success(self, mock_get_items_by_order_id):
        """Test fetching all items for an order successfully."""
        mock_get_items_by_order_id.return_value = [
            {"id": 1, "order_id": 1, "product_id": 101, "quantity": 2, "subtotal": 39.98},
            {"id": 2, "order_id": 1, "product_id": 102, "quantity": 1, "subtotal": 19.99},
        ]
        response = self.client.get("/api/orders/1/items", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("subtotal", response.get_data(as_text=True))

    @patch("services.order_item_service.OrderItemService.get_items_by_order_id")
    def test_get_order_items_not_found(self, mock_get_items_by_order_id):
        """Test fetching items for a non-existent order."""
        mock_get_items_by_order_id.side_effect = ValueError("Order not found.")
        response = self.client.get("/api/orders/999/items", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Order not found", response.get_data(as_text=True))

    @patch("services.order_item_service.OrderItemService.add_item_to_order")
    def test_add_order_item_success(self, mock_add_item_to_order):
        """Test adding an item to an order successfully."""
        mock_add_item_to_order.return_value = {
            "id": 3,
            "order_id": 1,
            "product_id": 103,
            "quantity": 1,
            "subtotal": 29.99,
        }
        response = self.client.post(
            "/api/orders/1/items",
            json={"product_id": 103, "quantity": 1},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("product_id", response.get_json())

    @patch("services.order_item_service.OrderItemService.add_item_to_order")
    def test_add_order_item_invalid_data(self, mock_add_item_to_order):
        """Test adding an item with invalid data."""
        mock_add_item_to_order.side_effect = ValueError("Invalid item data.")
        response = self.client.post(
            "/api/orders/1/items",
            json={"product_id": 103, "quantity": -1},  # Invalid quantity
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid item data", response.get_data(as_text=True))

    @patch("services.order_item_service.OrderItemService.update_item_quantity")
    def test_update_order_item_success(self, mock_update_item_quantity):
        """Test updating an item's quantity in an order successfully."""
        mock_update_item_quantity.return_value = {
            "id": 1,
            "order_id": 1,
            "product_id": 101,
            "quantity": 3,
            "subtotal": 59.97,
        }
        response = self.client.put(
            "/api/orders/1/items/1",
            json={"quantity": 3},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("quantity", response.get_json())

    @patch("services.order_item_service.OrderItemService.remove_item_from_order")
    def test_remove_order_item_success(self, mock_remove_item_from_order):
        """Test removing an item from an order successfully."""
        mock_remove_item_from_order.return_value = True
        response = self.client.delete("/api/orders/1/items/1", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Item removed successfully", response.get_data(as_text=True))

    @patch("services.order_item_service.OrderItemService.remove_item_from_order")
    def test_remove_order_item_not_found(self, mock_remove_item_from_order):
        """Test removing an item that does not exist in an order."""
        mock_remove_item_from_order.side_effect = ValueError("Item not found in order.")
        response = self.client.delete("/api/orders/1/items/999", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Item not found in order", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
