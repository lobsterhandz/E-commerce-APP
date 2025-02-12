import json
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_mock_data():
    data = {
        "categories": [
            {"id": 1, "name": "Electronics"},
            {"id": 2, "name": "Home Appliances"},
            {"id": 3, "name": "Books"},
            {"id": 4, "name": "Clothing"},
            {"id": 5, "name": "Sports Equipment"}
        ],
        "users": [
            {"username": "admin", "password": "adminpassword", "role": "admin", "is_active": True, "email": "admin@example.com"},
            {"username": "customer1", "password": "customerpassword", "role": "user", "is_active": True, "email": "customer1@example.com"},
            {"username": "customer2", "password": "customerpassword", "role": "user", "is_active": True, "email": "customer2@example.com"}
        ],
        "customers": [
            {"id": 1, "name": "John Doe", "email": "johndoe@example.com", "phone": "123-456-7890"},
            {"id": 2, "name": "Jane Smith", "email": "janesmith@example.com", "phone": "987-654-3210"},
            {"id": 3, "name": fake.name(), "email": fake.email(), "phone": fake.phone_number()}
        ],
        "products": [
            {"id": 1, "name": fake.word() + " Smartphone", "price": round(fake.random_number(digits=3), 2), "stock_quantity": fake.random_int(min=1, max=100), "category_id": 1},
            {"id": 2, "name": fake.word() + " Laptop", "price": round(fake.random_number(digits=4), 2), "stock_quantity": fake.random_int(min=1, max=50), "category_id": 1},
            {"id": 3, "name": fake.word() + " Washing Machine", "price": round(fake.random_number(digits=3), 2), "stock_quantity": fake.random_int(min=1, max=20), "category_id": 2},
            {"id": 4, "name": fake.word() + " Novel Book", "price": round(fake.random_number(digits=2), 2), "stock_quantity": fake.random_int(min=1, max=100), "category_id": 3},
            {"id": 5, "name": fake.word() + " Tennis Racket", "price": round(fake.random_number(digits=3), 2), "stock_quantity": fake.random_int(min=1, max=15), "category_id": 5}
        ],
        "orders": [
        {
            "id": 1,
            "customer_id": 1,
            "total_price": 789.98,
            "created_at": (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "items": [
                {"order_id": 1, "product_id": 1, "quantity": 1, "price_at_order": 699.99, "subtotal": 699.99},
                {"order_id": 1, "product_id": 3, "quantity": 1, "price_at_order": 89.99, "subtotal": 89.99}
            ]
        },
        {
            "id": 2,
            "customer_id": 2,
            "total_price": 14.99,
            "created_at": (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            "items": [
                {"order_id": 2, "product_id": 4, "quantity": 1, "price_at_order": 14.99, "subtotal": 14.99}
            ]
        }
    ],
        "order_items": [
            {
                "id": 1,
                "order_id": 1,
                "product_id": 1,
                "quantity": fake.random_int(min=1, max=5),
                "price_at_order": 699.99,
                "subtotal": 699.99
            },
            {
                "id": 2,
                "order_id": 1,
                "product_id": 3,
                "quantity": fake.random_int(min=1, max=5),
                "price_at_order": 89.99,
                "subtotal": 89.99
            },
            {
                "id": 3,
                "order_id": 2,
                "product_id": 4,
                "quantity": fake.random_int(min=1, max=5),
                "price_at_order": 14.99,
                "subtotal": 14.99
            }
        ],
        "shopping_carts": [
            {
                "id": 1,
                "customer_id": 1,
                "created_at": (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                "deleted_at": None,
                "items": [
                    {
                        "cart_id": 1,
                        "product_id": 1,
                        "quantity": fake.random_int(min=1, max=5),
                        "price": 699.99,
                        "subtotal": 699.99
                    },
                    {
                        "cart_id": 1,
                        "product_id": 4,
                        "quantity": fake.random_int(min=1, max=5),
                        "price": 14.99,
                        "subtotal": 29.98
                    }
                ]
            },
            {
                "id": 2,
                "customer_id": 2,
                "created_at": (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                "deleted_at": None,
                "items": [
                    {
                        "cart_id": 2,
                        "product_id": 2,
                        "quantity": fake.random_int(min=1, max=5),
                        "price": 1299.99,
                        "subtotal": 1299.99
                    }
                ]
            }
        ],
    "shopping_cart_items": [
        {
            "id": 1,
            "cart_id": 1,
            "product_id": 1,
            "quantity": fake.random_int(min=1, max=5),
            "price": 699.99,
            "subtotal": 699.99,
            "created_at": (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            "id": 2,
            "cart_id": 1,
            "product_id": 4,
            "quantity": fake.random_int(min=1, max=5),
            "price": 14.99,
            "subtotal": 29.98,
            "created_at": (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            "id": 3,
            "cart_id": 2,
            "product_id": 2,
            "quantity": fake.random_int(min=1, max=5),
            "price": 1299.99,
            "subtotal": 1299.99,
            "created_at": (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        }
    ],
        "customer_accounts": [
            {
                "id": 1,
                "username": "customer_account_1",
                "password_hash": fake.sha256(),
                "customer_id": 1
            },
            {
                "id": 2,
                "username": "customer_account_2",
                "password_hash": fake.sha256(),
                "customer_id": 2
            }
        ]
    }

    return data
if __name__ == "__main__":
    mock_data = generate_mock_data()
    print(json.dumps(mock_data, indent=4)) 
    with open("mock_data.json", "w") as file:
        json.dump(mock_data, file, indent=4)
    print("Mock data saved to mock_data.json")
