import React, { useState } from 'react';
import { Form, Button, Alert } from 'react-bootstrap';
import { createProduct } from '../api/product';

/**
 * CreateNewProductForm Component
 * Allows creating a new product by submitting product details to the backend.
 *
 * Props:
 * - onProductCreated: Callback function triggered after a successful product creation.
 */
const CreateNewProductForm = ({ onProductCreated }) => {
  const [product, setProduct] = useState({ name: '', price: '', stock_level: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setProduct({ ...product, [name]: value });
  };

  // Validate form inputs
  const validateForm = () => {
    if (!product.name || !product.price || product.stock_level === '') {
      setError('All fields are required.');
      return false;
    }

    if (isNaN(product.price) || product.price <= 0) {
      setError('Price must be a positive number.');
      return false;
    }

    if (isNaN(product.stock_level) || product.stock_level < 0) {
      setError('Stock level must be a non-negative number.');
      return false;
    }

    setError('');
    return true;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      await createProduct(product);
      setSuccess('Product created successfully!');
      setProduct({ name: '', price: '', stock_level: '' }); // Reset form fields
      onProductCreated(product); // Notify parent component
    } catch (err) {
      setError('Failed to create product.');
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <Form.Group controlId="name">
        <Form.Label>Name</Form.Label>
        <Form.Control
          type="text"
          name="name"
          value={product.name}
          onChange={handleChange}
          placeholder="Enter product name"
          required
        />
      </Form.Group>

      <Form.Group controlId="price" className="mt-3">
        <Form.Label>Price</Form.Label>
        <Form.Control
          type="number"
          name="price"
          value={product.price}
          onChange={handleChange}
          placeholder="Enter product price"
          required
        />
      </Form.Group>

      <Form.Group controlId="stock_level" className="mt-3">
        <Form.Label>Stock Level</Form.Label>
        <Form.Control
          type="number"
          name="stock_level"
          value={product.stock_level}
          onChange={handleChange}
          placeholder="Enter stock level"
          required
        />
      </Form.Group>

      <Button className="mt-4" variant="primary" type="submit">
        Create Product
      </Button>
    </Form>
  );
};

export default CreateNewProductForm;
