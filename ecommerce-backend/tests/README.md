# Tests for Factory Management System

This folder contains all test scripts and supporting files for the Factory Management System. These tests validate the functionality and reliability of the system, covering both unit and integration scenarios using the `unittest` framework.

---

## Folder Structure

tests/
│── auth/               # Tests related to authentication, roles, and token validation
│   ├── test_login.py
│   ├── test_register.py
│   ├── test_refresh_token.py
│   ├── test_role_based_access.py
│── integration/        # High-level tests that combine multiple routes or behaviors
│   ├── test_checkout_process.py
│   ├── test_order_lifecycle.py
│   ├── test_payment_flow.py
│── unit/               # Isolated tests for each feature, focusing on business logic
│   ├── test_category.py
│   ├── test_product.py
│   ├── test_user.py
│── mocks/              # Test doubles (mock data and fake API responses)
│   ├── mock_data.py
│   ├── fake_tiktok_api.py
│── utils/              # Shared helper functions for setting up tests
│   ├── test_setup.py
│   ├── jwt_helper.py
│── test_config.py      # Special test config settings
│── conftest.py         # Pytest setup (if using Pytest)
│── run_tests.py        # Unified test runner script


## Purpose

The `tests` folder serves the following purposes:

### Validate Functionality
Ensure that API endpoints work as expected, covering normal operations and edge cases.

### Prevent Regressions
Automatically verify that new changes do not break existing functionality.

### Isolate Components
Use mocking to test individual components independently of the database.

### Support Integration Testing
Seed mock data dynamically to validate the full flow of application features.

---

## Key Files

### `mock_data.json`

- A centralized JSON file containing mock data for users, employees, products, customers, orders, and production records.
- Provides consistent test data for all test cases.

### `mock_data.py`

- Contains helper functions to load and preprocess data from `mock_data.json`.
- Includes `seed_test_data()` to clear existing data and populate the database dynamically with mock data.

---

## Setup

Before running the tests, follow these steps:

### Install Dependencies
Ensure all required libraries are installed:
```bash
pip install -r requirements.txt
```

### Set Up the Database
Create and configure the testing database in `TestingConfig` (e.g., SQLite or MySQL).

### Seed Test Data
Test data is seeded dynamically via `seed_test_data()` from `mock_data.py`. This function clears existing data and populates the database with mock data from `mock_data.json`.

---

## Running Tests

### Run All Tests
Run all tests in the `tests` folder:
```bash
python -m unittest discover tests
```

### Run a Specific Test File
Run an individual test file:
```bash
python -m unittest tests/test_customer.py
```

---

## Writing Tests

### Basic Structure of a Test File

#### Import Modules and Classes
```python
import unittest
from unittest.mock import patch
from app import app
```

#### Set Up Test Client and Mock Data
```python
class TestExample(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mock token
```

#### Write Test Methods for Each Scenario
```python
@patch("services.example_service.ExampleService.get_example")
def test_get_example(self, mock_get_example):
    mock_get_example.return_value = {"id": 1, "name": "Example"}
    response = self.client.get("/example", headers=self.headers)
    self.assertEqual(response.status_code, 200)
    self.assertIn("Example", response.get_data(as_text=True))
```

#### Tear Down Resources
```python
def tearDown(self):
    pass
```

---

## Token for Testing

- Passwords for mock users in `mock_data.py` can be used to generate JWT tokens for testing.

---

## Contributing

1. Add new test files for additional features or endpoints.
2. Use `mock_data.json` for consistent data across all tests.
3. Run all tests before submitting changes to ensure nothing breaks.

---

This README ensures that new contributors or team members can easily understand and work with the `tests` folder. Let me know if you'd like to add anything else!

