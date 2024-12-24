# E-commerce Management System

## Project Overview
This project is a simple e-commerce management system developed using Flask. It provides RESTful API endpoints for managing customers, customer accounts, products, and orders. The system allows users to perform CRUD (Create, Read, Update, Delete) operations across different entities, ensuring an interactive and efficient experience.

The project includes a modular code structure, robust error handling, and unit tests for reliability. Flask-SQLAlchemy is used as the ORM (Object Relational Mapper) and Flask-Migrate for managing database migrations.

## Project Structure
```
ecommerce-management-system/
|
├── app/                      
│   ├── __init__.py           # Initializes Flask app and connects Blueprints
│   ├── database.py           # Database setup
│   ├── models.py             # SQLAlchemy models
│   ├── validation.py         # Validation functions
│   ├── routes/
│   │   ├── __init__.py       # Imports all routes
│   │   ├── customer_routes.py
│   │   ├── customer_account_routes.py
│   │   ├── product_routes.py
│   │   └── order_routes.py
├── migrations/               # Database migrations
├── tests/                    # Test files
│   ├── test_customer.py      # Tests for customer endpoints
│   ├── test_account.py       # Tests for customer account endpoints
│   ├── test_product.py       # Tests for product endpoints
│   ├── test_order.py         # Tests for order endpoints
├── .gitignore                # Git ignore file
├── config.py                 # Configuration settings (development, testing)
├── menu.py                   # User interactive interface to manage CRUD operations
├── app.py                    # Main entry point to run the Flask server
├── README.md                 # Documentation for the project
└── requirements.txt          # Python dependencies
```

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

## API Endpoints and Examples

### Customer Management
- **Create Customer**: `POST /customer`
- **Read Customer**: `GET /customer/<id>`
- **Update Customer**: `PUT /customer/<id>`
- **Delete Customer**: `DELETE /customer/<id>`

### Customer Account Management
- **Create Customer Account**: `POST /customer_account`
- **Read Customer Account**: `GET /customer_account/<id>`
- **Update Customer Account**: `PUT /customer_account/<id>`
- **Delete Customer Account**: `DELETE /customer_account/<id>`

### Product Management
- **Create Product**: `POST /product`
- **Read Product**: `GET /product/<id>`
- **Update Product**: `PUT /product/<id>`
- **Delete Product**: `DELETE /product/<id>`
- **List Products**: `GET /products`

### Order Management
- **Create Order**: `POST /order`
- **Read Order**: `GET /order/<id>`
- **Update Order**: `PUT /order/<id>`
- **Delete Order**: `DELETE /order/<id>`

## Testing the Application

Unit tests are included to validate the functionality of each route. To run the tests, use the following command:
```sh
pytest
```
The tests cover:
- Customer CRUD operations (`test_customer.py`)
- Customer Account operations (`test_account.py`)
- Product management (`test_product.py`)
- Order management (`test_order.py`)

## Technology Stack
- **Backend**: Python, Flask
- **Database**: MySQL (optional), SQLite (default for local development)
- **ORM**: SQLAlchemy
- **Testing**: unittest, pytest

## Contribution Guidelines
- Contributions are welcome! Please fork the repository and create a pull request.
- Before submitting a pull request, ensure all tests are passing and your code follows best practices.

## License
This project is licensed under the MIT License.

## Contact
For any issues or inquiries, please contact [your-email@example.com].

