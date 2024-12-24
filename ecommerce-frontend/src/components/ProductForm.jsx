import React, { useState, useEffect } from 'react';
import { Form, Button, Container, Row, Col, Alert, Table } from 'react-bootstrap';
import { createProduct, getProduct, updateProduct, deleteProduct } from '../api/product';

const ProductForm = () => {
  const [product, setProduct] = useState({ name: '', price: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [products, setProducts] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [productId, setProductId] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await getProduct(''); // Fetch all products if the backend supports it
      setProducts(response);
    } catch (err) {
      setError('Failed to fetch products');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProduct({ ...product, [name]: value });
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
      setError('');
      setProduct({ name: '', price: '' });
      setEditMode(false);
      setProductId(null);
      fetchProducts();
    } catch (err) {
      setError(err);
      setSuccess('');
    }
  };

  const handleEdit = (product) => {
    setProduct({ name: product.name, price: product.price });
    setEditMode(true);
    setProductId(product.id);
    setSuccess('');
    setError('');
  };

  const handleDelete = async (id) => {
    try {
      await deleteProduct(id);
      setSuccess('Product deleted successfully!');
      setError('');
      fetchProducts();
    } catch (err) {
      setError('Failed to delete product');
      setSuccess('');
    }
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={6}>
          <h2 className="text-center">{editMode ? 'Edit Product' : 'Add Product'}</h2>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="name">
              <Form.Label>Product Name</Form.Label>
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
            <Button variant="primary" type="submit" className="mt-4 w-100">
              {editMode ? 'Update' : 'Submit'}
            </Button>
          </Form>
        </Col>
      </Row>
      <Row className="mt-5">
        <Col>
          <h3 className="text-center">Product List</h3>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Name</th>
                <th>Price</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((prod) => (
                <tr key={prod.id}>
                  <td>{prod.name}</td>
                  <td>{prod.price}</td>
                  <td>
                    <Button
                      variant="warning"
                      className="me-2"
                      onClick={() => handleEdit(prod)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="danger"
                      onClick={() => handleDelete(prod.id)}
                    >
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

export default ProductForm;
