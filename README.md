# E-commerce Management System

## Project Overview
This project is a robust E-commerce Management System developed with a Flask backend and a React frontend. The system provides CRUD (Create, Read, Update, Delete) operations for managing customers, customer accounts, products, and orders. It integrates a MySQL database (or SQLite as default) and uses Axios for front-end API calls.

---

## Backend API Structure

### **API Endpoints**
#### Customer Management
- **Create Customer**: `POST /customer`
- **Read Customer**: `GET /customer/<id>`
- **Update Customer**: `PUT /customer/<id>`
- **Delete Customer**: `DELETE /customer/<id>`

#### Customer Account Management
- **Create Account**: `POST /customer_account`
- **Read Account**: `GET /customer_account/<id>`
- **Update Account**: `PUT /customer_account/<id>`
- **Delete Account**: `DELETE /customer_account/<id>`

#### Product Management
- **Create Product**: `POST /product`
- **Read Product**: `GET /product/<id>`
- **Update Product**: `PUT /product/<id>`
- **Delete Product**: `DELETE /product/<id>`
- **List Products**: `GET /products`

#### Order Management
- **Create Order**: `POST /order`
- **Read Order**: `GET /order/<id>`
- **Update Order**: `PUT /order/<id>`
- **Delete Order**: `DELETE /order/<id>`

---

## Frontend Components

### **Main Front-End Entry Point**
- **File**: `src/main.jsx`
- **Purpose**: Renders the root component and initializes React Router for navigation.
- **Key Imports**:
  - `App.jsx` for routing.
  - Bootstrap and custom styles.

### **App Component**
- **File**: `src/App.jsx`
- **Purpose**: Centralized routing for the application.
- **Routes**:
  - `/customers`: Customer management.
  - `/accounts`: Customer account management.
  - `/products`: Product management.
  - `/orders`: Order management.

### **Customer Components**
- **File**: `src/components/CustomerForm.jsx`
- **Purpose**: Manage customer records with create, read, update, and delete operations.
- **API Integration**: Uses `src/api/customer.js` for backend requests.

### **Customer Account Components**
- **File**: `src/components/CustomerAccountForm.jsx`
- **Purpose**: Handle customer account management, including username and password updates.
- **API Integration**: Uses `src/api/customerAccount.js`.

### **Product Components**
- **File**: `src/components/ProductForm.jsx`
- **Purpose**: Enable product creation, listing, editing, and deletion.
- **API Integration**: Uses `src/api/product.js`.

### **Order Components**
- **File**: `src/components/OrderForm.jsx`
- **Purpose**: Manage customer orders, including product selection and order status updates.
- **API Integration**: Uses `src/api/order.js`.

### **Shared Axios Instance**
- **File**: `src/api/axios.js`
- **Purpose**: Centralizes API configuration and base URL setup for Axios requests.

---

## Frontend-Backend Integration

### Axios Configuration
**File**: `src/api/axios.js`
```javascript
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosInstance;
```

### API Modules
#### **Customer API** (`src/api/customer.js`)
- Functions:
  - `createCustomer(data)`
  - `getCustomer(id)`
  - `updateCustomer(id, data)`
  - `deleteCustomer(id)`

#### **Customer Account API** (`src/api/customerAccount.js`)
- Functions:
  - `createCustomerAccount(data)`
  - `getCustomerAccount(id)`
  - `updateCustomerAccount(id, data)`
  - `deleteCustomerAccount(id)`

#### **Product API** (`src/api/product.js`)
- Functions:
  - `createProduct(data)`
  - `getProduct(id)`
  - `updateProduct(id, data)`
  - `deleteProduct(id)`

#### **Order API** (`src/api/order.js`)
- Functions:
  - `createOrder(data)`
  - `getOrder(id)`
  - `updateOrder(id, data)`
  - `deleteOrder(id)`

---

## Running the Application

### Backend
1. Start the Flask server:
   ```bash
   python app.py
   ```

### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd ecommerce-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Access the application in your browser:
   ```
   http://localhost:5173
   ```

---

## Testing the Application

### Backend Testing
- Use **Postman** or **curl** to test API endpoints.
- Example:
  ```bash
  curl -X GET http://127.0.0.1:5000/customers
  ```

### Frontend Testing
- Navigate to each route (e.g., `/customers`, `/accounts`, `/products`, `/orders`).
- Test create, read, update, and delete operations.
- Verify data updates in the backend using Postman or database queries.

---

## Contribution Guidelines
- Fork the repository and create a pull request for contributions.
- Ensure all tests pass before submitting.

---

## License
This project is licensed under the MIT License.

