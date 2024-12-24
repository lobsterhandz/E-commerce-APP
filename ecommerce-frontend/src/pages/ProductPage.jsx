import React, { useState, useEffect } from 'react';
import { Table, Button, Container, Alert, Form, Row, Col } from 'react-bootstrap';
import {
  createProduct,
  getProducts,
  updateProduct,
  deleteProduct,
} from '../api/product';

const ProductPage = () => {
  const [products, setProducts] = useState([]);
  const [product, setProduct] = useState({ name: '', price: '', stock_level: '' });
  const [editMode, setEditMode] = useState(false);
  const [productId, setProductId] = useState(null);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProduct((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editMode) {
        await updateProduct(productId, product);
        setSuccess('Product updated successfully!');
      } else {
        await createProduct(product);
        setSuccess('Product added successfully!');
      }
      resetForm();
      fetchProducts();
    } catch (err) {
      setError(err || 'Failed to save product');
    }
  };

  const resetForm = () => {
    setProduct({ name: '', price: '', stock_level: '' });
    setEditMode(false);
    setProductId(null);
    setSuccess('');
    setError('');
  };

  const handleEdit = (product) => {
    setProduct({ name: product.name, price: product.price, stock_level: product.stock_level });
    setEditMode(true);
    setProductId(product.id);
  };

  const handleDelete = async (id) => {
    try {
      await deleteProduct(id);
      setSuccess('Product deleted successfully!');
      fetchProducts();
    } catch (err) {
      setError('Failed to delete product');
    }
  };

  return (
    <Container className="mt-5">
      <Row>
        <Col>
          <h2 className="text-center">{editMode ? 'Edit Product' : 'Add Product'}</h2>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          <Form onSubmit={handleSubmit}>
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
            <Button type="submit" className="mt-4 w-100">
              {editMode ? 'Update Product' : 'Add Product'}
            </Button>
          </Form>
        </Col>
      </Row>
      <Row className="mt-5">
        <Col>
          <h3>Product List</h3>
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>Name</th>
                <th>Price</th>
                <th>Stock Level</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((prod) => (
                <tr key={prod.id}>
                  <td>{prod.name}</td>
                  <td>{prod.price}</td>
                  <td>{prod.stock_level}</td>
                  <td>
                    <Button variant="warning" onClick={() => handleEdit(prod)}>
                      Edit
                    </Button>{' '}
                    <Button variant="danger" onClick={() => handleDelete(prod.id)}>
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Col>
      </Row>
    </Container>
  );
};

export default ProductPage;
