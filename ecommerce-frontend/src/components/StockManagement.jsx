import React, { useState, useEffect } from 'react';
import { Table, Button, Form, Container, Alert } from 'react-bootstrap';
import { getProducts, updateProduct } from '../api/product';

const StockManagementPage = () => {
  const [products, setProducts] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await getProducts();
      setProducts(response);
    } catch (err) {
      setError('Failed to fetch products');
    }
  };

  const handleStockChange = async (id, stockLevel) => {
    try {
      await updateProduct(id, { stock_level: stockLevel });
      setSuccess('Stock updated successfully!');
      setError('');
      fetchProducts();
    } catch (err) {
      setError('Failed to update stock. Please try again.');
      setSuccess('');
    }
  };

  return (
    <Container className="mt-5">
      <h2 className="text-center">Stock Management</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}
      <Table striped bordered hover responsive className="mt-4">
        <thead>
          <tr>
            <th>Product Name</th>
            <th>Stock Level</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.id}>
              <td>{product.name}</td>
              <td>
                <Form.Control
                  type="number"
                  value={product.stock_level}
                  onChange={(e) =>
                    handleStockChange(product.id, parseInt(e.target.value))
                  }
                  min="0"
                />
              </td>
              <td>
                <Button
                  variant="success"
                  onClick={() =>
                    handleStockChange(product.id, product.stock_level)
                  }
                >
                  Update
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
};

export default StockManagementPage;
