# E-commerce Management System - BackEnd

## Project Overview
This project is a simple e-commerce management system developed using Flask. It provides RESTful API endpoints for managing customers, customer accounts, products, and orders. The system allows users to perform CRUD (Create, Read, Update, Delete) operations across different entities, ensuring an interactive and efficient experience.

The project includes a modular code structure, robust error handling, and unit tests for reliability. Flask-SQLAlchemy is used as the ORM (Object Relational Mapper) and Flask-Migrate for managing database migrations. Additionally, it features JWT-based authentication, caching for optimized performance, request rate limiting, and schema validation using Marshmallow.

The project leverages Flask for the API, PostgreSQL for the database, and a robust CI/CD pipeline using GitHub Actions and Render for continuous integration and deployment. It emphasizes automated testing, smooth deployment, and comprehensive documentation to facilitate efficient collaboration and project management.

## Key Features
- **JWT Authentication**: Secure user login and role-based access control using JSON Web Tokens.
- **Caching**: Optimized performance for frequently accessed endpoints using Flask-Caching.
- **Rate Limiting**: API usage is controlled using Flask-Limiter to prevent abuse.
- **Marshmallow Schemas**: Data validation and serialization for API requests and responses.
- **Dynamic Shopping Cart**: A fully interactive shopping cart system that supports adding, updating, removing items, and seamless checkout functionality.
- **CI/CD Workflow**: Automates build, test, and deployment processes with GitHub Actions and Render.

- **Swagger Documentation**: Interactive API documentation accessible via Swagger UI: https://e-commerce-flask-232f.onrender.com/docs/
- **GitHub Actions integration with Render**: safe and fast and continuous deployment
- **Modular Design**: Can easilly port this app businesss or existing database.
## Project Structure
```
# File Structure for `ecommerce-backend`

ecommerce-backend/
|-- __pycache__/
|-- migrations/
|-- models/
|   |-- __pycache__/
|   |-- __init__.py
|   |-- category.py
|   |-- customer_account.py
|   |-- customer.py
|   |-- order_item.py
|   |-- order.py
|   |-- product.py
|   |-- shopping_cart_item.py
|   |-- shopping_cart.py
|   |-- user.py
|-- routes/
|   |-- __pycache__/
|   |-- __init__.py
|   |-- category_bp.py
|   |-- customer_account_bp.py
|   |-- customer_bp.py
|   |-- order_bp.py
|   |-- order_item_bp.py
|   |-- product_bp.py
|   |-- shopping_cart_bp.py
|   |-- shopping_cart_item_bp.py
|   |-- user_bp.py
|-- schemas/
|   |-- __pycache__/
|   |-- __init__.py
|   |-- category_schema.py
|   |-- customer_account_schema.py
|   |-- customer_schema.py
|   |-- order_item_schema.py
|   |-- order_schema.py
|   |-- product_schema.py
|   |-- shopping_cart_item_schema.py
|   |-- shopping_cart_schema.py
|   |-- user_schema.py
|-- services/
|   |-- customer_account_service.py
|   |-- customer_service.py
|   |-- order_item_service.py
|   |-- order_service.py
|   |-- product_service.py
|   |-- shopping_cart_item_service.py
|   |-- shopping_cart_service.py
|   |-- user_service.py
|-- tests/
|   |-- __pycache__/
|   |-- __init__.py
|   |-- test_endpoints.py
|   |-- mock_data.py
|   |-- README.md
|   |-- conftest.py
|-- utils/
|   |-- __pycache__/
|   |-- __init__.py
|   |-- caching.py
|   |-- limiter.py
|   |-- utils.py
|   |-- validation.py
|-- venv/
|-- .env
|-- mock_data.json
|-- app.py
|-- config.py
|-- menu.py
|-- README.md
|-- requirements.txt
```

## API Endpoints

### Authentication
- **Login**: `POST /users/login` (JWT token-based authentication)
- **Register**: `POST /users/register`

### User Management
- **List Users**: `GET /users`
- **Get User by ID**: `GET /users/<int:user_id>`
- **Update User**: `PUT /users/<int:user_id>`
- **Delete User**: `DELETE /users/<int:user_id>`

### Customer Management
- **Create Customer**: `POST /customers`
- **Read Customer**: `GET /customers/<int:customer_id>`
- **Update Customer**: `PUT /customers/<int:customer_id>`
- **Delete Customer**: `DELETE /customers/<int:customer_id>`

### Customer Account Management
- **Create Customer Account**: `POST /customer_accounts`
- **Read Customer Account**: `GET /customer_accounts/<int:account_id>`
- **Update Customer Account**: `PUT /customer_accounts/<int:account_id>`
- **Delete Customer Account**: `DELETE /customer_accounts/<int:account_id>`

### Product Management
- **Create Product**: `POST /products`
- **Read Product**: `GET /products/<int:product_id>`
- **Update Product**: `PUT /products/<int:product_id>`
- **Delete Product**: `DELETE /products/<int:product_id>`
- **List Products**: `GET /products`

### Order Management
- **Create Order**: `POST /orders`
- **Read Order**: `GET /orders/<int:order_id>`
- **Update Order**: `PUT /orders/<int:order_id>`
- **Delete Order**: `DELETE /orders/<int:order_id>`

### Shopping Cart
- **Get Cart**: `GET /shopping_cart`
- **Add Item to Cart**: `POST /shopping_cart`
- **Remove Item from Cart**: `DELETE /shopping_cart/<int:product_id>`
- **Checkout Cart**: `POST /shopping_cart/checkout`

### Shopping Cart Items
- **Get Cart Items**: `GET /shopping_cart_items/<int:cart_id>/items`
- **Add Item to Cart**: `POST /shopping_cart_items/<int:cart_id>/items`
- **Update Item in Cart**: `PUT /shopping_cart_items/<int:cart_id>/items/<int:item_id>`
- **Remove Item from Cart**: `DELETE /shopping_cart_items/<int:cart_id>/items/<int:item_id>`

## Key Technologies and Features

### JSON Web Tokens (JWT)
- Used for secure user authentication and role-based access control.
- Provides a stateless mechanism for verifying users with roles such as `super_admin`, `admin`, and `user`.

### Flask-Caching
- Implements caching for frequently accessed endpoints, significantly improving performance.
- Query strings are utilized for cache keys, ensuring endpoint flexibility.

### Flask-Limiter
- Prevents API abuse by limiting the number of requests per user for specific endpoints.
- Configurable rate limits such as `5 per minute` or `10 per second`.

### Marshmallow
- Handles data validation and serialization for request bodies and responses.
- Ensures all API inputs adhere to the required schema.

### Dynamic Shopping Cart
- Fully dynamic shopping cart system allowing users to:
  - Add items (with quantity and subtotal calculations).
  - Update item quantities in real-time.
  - Remove items.
  - Checkout with the total price calculation.

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- MySQL (Optional for database setup)

### Installation Steps
1. **Clone the Repository**:
   ```sh
   git clone https://github.com/your-username/ecommerce-management-system.git
   cd ecommerce-management-system
   ```

2. **Create and Activate a Virtual Environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure the Database**:
   - The application supports both MySQL and SQLite databases.
   - **SQLite (Default)**: No further setup is needed if you are okay using SQLite.
   - **MySQL**:
     - To use MySQL, set up the following environment variable in your terminal:
     ```sh
     export DATABASE_URL=mysql+pymysql://username:password@localhost/ecommerce_db
     ```
     Replace `username`, `password`, and `ecommerce_db` with your MySQL credentials.

5. **Set Up the Database**:
   ```sh
   flask db init
   flask db migrate -m "Initial migration for the database."
   flask db upgrade
   ```

6. **Run the Application**:
   ```sh
   python app.py
   ```

7. **Run Command-Line Menu Interface**:
   To interact with the API through a menu-driven command line, open a new terminal window and run:
   ```sh
   python menu.py
   ```

## Testing the Application

Unit tests are included to validate the functionality of each route. To run the tests, use the following command:
```sh
python -m unittest discover -s tests -p "test_*.py"
```

The tests cover:
- Customer CRUD operations (`test_customer.py`)
- Customer Account operations (`test_customer_account.py`)
- Product management (`test_product.py`)
- Order management (`test_order.py`)

## Contribution Guidelines
- Contributions are welcome! Please fork the repository and create a pull request.
- Before submitting a pull request, ensure all tests are passing and your code follows best practices.

## License
This project is licensed under the MIT License.

## Contact
For any issues or inquiries, please contact [josemurillo82@gmail.com].

## Notes & improvements
Version: v6.12.0- stable
- added local db(sqlite) for testing enviorments to avoid accidental change/loss to prodution data.
- Use simple cache(local) if Redis not setup.
- can select config class (test,development, production) from your enviorment variable.
- Github Actions will run conftest and test_enpoints before a succesfull push (ci-cd) 
