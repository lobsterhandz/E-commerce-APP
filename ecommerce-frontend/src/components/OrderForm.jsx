import React, { useState, useEffect } from 'react';
import { Form, Button, Container, Row, Col, Alert, Table } from 'react-bootstrap';
import { createOrder, getOrder, updateOrder, deleteOrder } from '../api/order';

const OrderForm = () => {
  const [order, setOrder] = useState({ customerId: '', products: [], date: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [orders, setOrders] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [orderId, setOrderId] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await getOrder(''); // Fetch all orders if the backend supports it
      setOrders(response);
    } catch (err) {
      setError('Failed to fetch orders');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setOrder({ ...order, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editMode) {
        await updateOrder(orderId, order);
        setSuccess('Order updated successfully!');
      } else {
        await createOrder(order);
        setSuccess('Order created successfully!');
      }
      setError('');
      setOrder({ customerId: '', products: [], date: '' });
      setEditMode(false);
      setOrderId(null);
      fetchOrders();
    } catch (err) {
      setError(err);
      setSuccess('');
    }
  };

  const handleEdit = (order) => {
    setOrder({ customerId: order.customerId, products: order.products, date: order.date });
    setEditMode(true);
    setOrderId(order.id);
    setSuccess('');
    setError('');
  };

  const handleDelete = async (id) => {
    try {
      await deleteOrder(id);
      setSuccess('Order deleted successfully!');
      setError('');
      fetchOrders();
    } catch (err) {
      setError('Failed to delete order');
      setSuccess('');
    }
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={6}>
          <h2 className="text-center">{editMode ? 'Edit Order' : 'Create Order'}</h2>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="customerId">
              <Form.Label>Customer ID</Form.Label>
              <Form.Control
                type="text"
                name="customerId"
                value={order.customerId}
                onChange={handleChange}
                placeholder="Enter customer ID"
                required
              />
            </Form.Group>
            <Form.Group controlId="products" className="mt-3">
              <Form.Label>Products (comma-separated)</Form.Label>
              <Form.Control
                type="text"
                name="products"
                value={order.products.join(', ')}
                onChange={(e) =>
                  setOrder({ ...order, products: e.target.value.split(',').map((p) => p.trim()) })
                }
                placeholder="Enter product IDs"
                required
              />
            </Form.Group>
            <Form.Group controlId="date" className="mt-3">
              <Form.Label>Order Date</Form.Label>
              <Form.Control
                type="date"
                name="date"
                value={order.date}
                onChange={handleChange}
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
          <h3 className="text-center">Order List</h3>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Products</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((ord) => (
                <tr key={ord.id}>
                  <td>{ord.customerId}</td>
                  <td>{ord.products.join(', ')}</td>
                  <td>{ord.date}</td>
                  <td>
                    <Button
                      variant="warning"
                      className="me-2"
                      onClick={() => handleEdit(ord)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="danger"
                      onClick={() => handleDelete(ord.id)}
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

export default OrderForm;
