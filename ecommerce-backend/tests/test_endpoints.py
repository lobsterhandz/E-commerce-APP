import json
import pytest


@pytest.fixture(scope="module")
def auth_tokens(client):
    """Authenticate and return JWT tokens for both admin and customer."""
    admin_login = client.post("/users/login", json={"username": "admin", "password": "adminpassword"})
    customer_login = client.post("/users/login", json={"username": "customer1", "password": "customerpassword"})

    assert admin_login.status_code == 200, "Admin login failed"
    assert customer_login.status_code == 200, "Customer login failed"

    admin_token = json.loads(admin_login.data)["token"]
    customer_token = json.loads(customer_login.data)["token"]

    return {"admin": f"Bearer {admin_token}", "customer": f"Bearer {customer_token}"}


def test_get_products(client):
    """Test retrieving product list (public endpoint)."""
    response = client.get("/products")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert "products" in data
    assert isinstance(data["products"], list)


def test_create_product(client, auth_tokens):
    """Test creating a product (Admin only)."""
    headers = {"Authorization": auth_tokens["admin"]}
    response = client.post("/products", json={
        "name": "New Product",
        "price": 99.99,
        "stock_quantity": 50,
        "category_id": 1
    }, headers=headers)

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["name"] == "New Product"

def test_update_product(client, auth_tokens):
    """Test updating a product (Admin only)."""
    headers = {"Authorization": auth_tokens["admin"]}
    
    # First create a product
    response = client.post("/products", json={
        "name": "Update Test Product",
        "price": 50.00,
        "stock_quantity": 10,
        "category_id": 1
    }, headers=headers)
    
    assert response.status_code == 201
    product_id = json.loads(response.data)["id"]

    # Update the product
    response = client.put(f"/products/{product_id}", json={
        "name": "Updated Product Name",
        "price": 59.99,
        "stock_quantity": 15
    }, headers=headers)

    assert response.status_code == 200
    updated_product = json.loads(response.data)
    assert updated_product["name"] == "Updated Product Name"
    assert updated_product["price"] == 59.99

def test_customer_cannot_create_product(client, auth_tokens):
    """Test that a customer cannot create a product."""
    headers = {"Authorization": auth_tokens["customer"]}
    response = client.post("/products", json={
        "name": "Unauthorized Product",
        "price": 49.99,
        "stock_quantity": 20,
        "category_id": 1
    }, headers=headers)

    assert response.status_code == 403  # Forbidden

def test_delete_product(client, auth_tokens):
    """Test deleting a product (Admin only)."""
    headers = {"Authorization": auth_tokens["admin"]}
    
    # First create a product
    response = client.post("/products", json={
        "name": "Delete Test Product",
        "price": 25.99,
        "stock_quantity": 5,
        "category_id": 1
    }, headers=headers)
    
    assert response.status_code == 201
    product_id = json.loads(response.data)["id"]

    # Delete the product
    response = client.delete(f"/products/{product_id}", headers=headers)
    assert response.status_code == 200
    assert json.loads(response.data)["message"] == "Product deleted successfully"

    # Verify it's deleted
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404  # Product no longer exists


def test_customer_cannot_delete_product(client, auth_tokens):
    """Ensure customers cannot delete products."""
    headers = {"Authorization": auth_tokens["customer"]}

    response = client.delete(f"/products/1", headers=headers)
    assert response.status_code == 403  # Forbidden

def test_admin_can_list_users(client, auth_tokens):
    """Test admin can view user list."""
    headers = {"Authorization": auth_tokens["admin"]}
    response = client.get("/users", headers=headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_customer_cannot_list_users(client, auth_tokens):
    """Test that a customer cannot list users."""
    headers = {"Authorization": auth_tokens["customer"]}
    response = client.get("/users", headers=headers)

    assert response.status_code == 403  # Forbidden


def test_create_order(client, auth_tokens):
    """Test creating an order (Customer only)."""
    headers = {"Authorization": auth_tokens["customer"]}
    response = client.post("/orders", json={
        "customer_id": 1,
        "total_price": 199.99,
        "items": [{"product_id": 1, "quantity": 2, "price_at_order": 99.99}]
    }, headers=headers)

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["customer_id"] == 1


def test_admin_cannot_create_order(client, auth_tokens):
    """Test that an admin cannot create an order."""
    headers = {"Authorization": auth_tokens["admin"]}
    response = client.post("/orders", json={
        "customer_id": 1,
        "total_price": 99.99,
        "items": [{"product_id": 2, "quantity": 1, "price_at_order": 99.99}]
    }, headers=headers)

    assert response.status_code == 403  # Forbidden


def test_checkout_cart(client, auth_tokens):
    """Test checkout process for a customer."""
    headers = {"Authorization": auth_tokens["customer"]}
    response = client.post("/shopping_cart/checkout", headers=headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
