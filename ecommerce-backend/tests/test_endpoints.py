import pytest

@pytest.fixture
def auth_tokens(client):
    """
    Fixture to authenticate as both an admin and a customer.
    Returns a dictionary of JWT tokens for testing.
    """
    # Authenticate as admin
    admin_resp = client.post("/users/login", json={
        "username": "admin",
        "password": "adminpassword"
    })
    # Authenticate as customer
    customer_resp = client.post("/users/login", json={
        "username": "customer1",
        "password": "customerpassword"
    })

    # Ensure both logins succeed
    assert admin_resp.status_code == 200, "Admin login failed"
    assert customer_resp.status_code == 200, "Customer login failed"

    # Use .get_json() to parse response payloads and extract access_token
    admin_data = admin_resp.get_json()
    customer_data = customer_resp.get_json()

    return {
        "admin": f"Bearer {admin_data['access_token']}",
        "customer": f"Bearer {customer_data['access_token']}"
    }

def test_get_products(client, auth_tokens):
    """
    Test fetching the products list using an admin token.
    """
    headers = {"Authorization": auth_tokens["admin"]}
    response = client.get("/products", headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    data = response.get_json()
    assert "products" in data, "Response does not contain 'products' key"
    assert isinstance(data["products"], list), "'products' is not a list"

def test_create_product(client, auth_tokens):
    """
    Test product creation (Admin only).
    """
    headers = {"Authorization": auth_tokens["admin"]}
    payload = {
        "name": "New Product",
        "price": 99.99,
        "stock_quantity": 50,
        "category_id": 1
    }
    response = client.post("/products", json=payload, headers=headers)
    assert response.status_code == 201, f"Expected 201 but got {response.status_code}"
    data = response.get_json()
    assert data["name"] == "New Product", "Product name does not match"

def test_update_product(client, auth_tokens):
    """
    Test updating a product (Admin only).
    """
    headers = {"Authorization": auth_tokens["admin"]}
    # Create a product to update
    create_payload = {
        "name": "Temp Product",
        "price": 50.00,
        "stock_quantity": 10,
        "category_id": 1
    }
    create_resp = client.post("/products", json=create_payload, headers=headers)
    assert create_resp.status_code == 201, "Failed to create product for update test"
    product_id = create_resp.get_json()["id"]

    # Update the product
    update_payload = {
        "name": "Updated Product",
        "price": 59.99,
        "stock_quantity": 15
    }
    update_resp = client.put(f"/products/{product_id}", json=update_payload, headers=headers)
    assert update_resp.status_code == 200, f"Expected 200 but got {update_resp.status_code}"
    updated_product = update_resp.get_json()
    assert updated_product["name"] == "Updated Product", "Product name was not updated"
    assert updated_product["price"] == 59.99, "Product price was not updated"

def test_customer_cannot_create_product(client, auth_tokens):
    """
    Ensure that a customer cannot create a product.
    """
    headers = {"Authorization": auth_tokens["customer"]}
    payload = {"name": "Unauthorized", "price": 49.99, "stock_quantity": 20, "category_id": 1}
    response = client.post("/products", json=payload, headers=headers)
    assert response.status_code == 403, "Customer should not be allowed to create a product"

def test_delete_product(client, auth_tokens):
    """
    Test product deletion (Admin only).
    """
    headers = {"Authorization": auth_tokens["admin"]}
    # Create a product to delete
    payload = {
        "name": "Delete Me",
        "price": 25.99,
        "stock_quantity": 5,
        "category_id": 1
    }
    create_resp = client.post("/products", json=payload, headers=headers)
    product_id = create_resp.get_json()["id"]

    # Delete the product
    delete_resp = client.delete(f"/products/{product_id}", headers=headers)
    assert delete_resp.status_code == 200, f"Expected 200 but got {delete_resp.status_code}"
    delete_msg = delete_resp.get_json()["message"]
    assert delete_msg == "Product deleted successfully", "Deletion message mismatch"

    # Verify the product is deleted
    get_resp = client.get(f"/products/{product_id}", headers=headers)
    assert get_resp.status_code == 404, "Product still exists after deletion"

def test_customer_cannot_delete_product(client, auth_tokens):
    """Ensure customers cannot delete products."""
    headers = {"Authorization": auth_tokens["customer"]}

    # ✅ Dynamically create a product for this test to avoid missing product errors
    create_resp = client.post("/products", json={"name": "CannotDelete", "price": 30.00, "stock_quantity": 10, "category_id": 1}, headers=auth_tokens["admin"])
    product_id = create_resp.get_json()["id"]

    response = client.delete(f"/products/{product_id}", headers=headers)
    assert response.status_code == 403  # ✅ Customers should not be able to delete products

def test_admin_can_list_users(client, auth_tokens):
    """
    Test that admins can list users.
    """
    headers = {"Authorization": auth_tokens["admin"]}
    response = client.get("/users", headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    data = response.get_json()
    assert isinstance(data, list), "Users endpoint did not return a list"

def test_customer_cannot_list_users(client, auth_tokens):
    """
    Test that customers cannot list users.
    """
    headers = {"Authorization": auth_tokens["customer"]}
    response = client.get("/users", headers=headers)
    assert response.status_code == 403, "Customer should not be allowed to list users"

def test_create_order(client, auth_tokens):
    """
    Test that a customer can create an order.
    """
    headers = {"Authorization": auth_tokens["customer"]}
    payload = {
        "customer_id": 1,
        "total_price": 99.99,
        "items": [{"product_id": 1, "quantity": 2, "price_at_order": 49.99}]
    }
    response = client.post("/orders", json=payload, headers=headers)
    assert response.status_code == 201, f"Expected 201 but got {response.status_code}"

def test_admin_cannot_create_order(client, auth_tokens):
    """
    Ensure that admins cannot create orders.
    Your API must reject order creation for non-customer roles.
    """
    headers = {"Authorization": auth_tokens["admin"]}
    payload = {
        "customer_id": 1,
        "total_price": 99.99,
        "items": [{"product_id": 2, "quantity": 1, "price_at_order": 99.99}]
    }
    response = client.post("/orders", json=payload, headers=headers)
    assert response.status_code == 403, "Admin should not be allowed to create an order"

def test_checkout_cart(client, auth_tokens):
    """
    Test the shopping cart checkout process for a customer.
    """
    headers = {"Authorization": auth_tokens["customer"]}
    response = client.post("/shopping_cart/checkout", headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    data = response.get_json()
    assert "message" in data, "Checkout response missing 'message' key"
