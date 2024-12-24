import React, { useState, useEffect } from 'react';
import { Table, Button, Container, Alert, Form, Row, Col } from 'react-bootstrap';
import { createOrder, getOrder, updateOrder, deleteOrder } from '../api/order';
import { getCustomers } from '../api/customer';
import { getProducts } from '../api/product';

const OrderPage = () => {
  const [orders, setOrders] = useState([]);
  const [order, setOrder] = useState({ customer_id: '', order_items: [] });
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [orderId, setOrderId] = useState(null);

  useEffect(() => {
    fetchOrders();
    fetchCustomers();
    fetchProducts();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await getOrder();
      setOrders(response);
    } catch (err) {
      setError('Failed to fetch orders');
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await getCustomers();
      setCustomers(response);
    } catch (err) {
      setError('Failed to fetch customers');
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await getProducts();
      setProducts(response);
    } catch (err) {
      setError('Failed to fetch products');
    }
  };

  const handleAddItem = () => {
    setOrder((prev) => ({
      ...prev,
      order_items: [...prev.order_items, { product_id: '', quantity: 1 }],
    }));
  };

  const handleItemChange = (index, field, value) => {
    const updatedItems = [...order.order_items];
    updatedItems[index][field] = value;
    setOrder((prev) => ({ ...prev, order_items: updatedItems }));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setOrder((prev) => ({ ...prev, [name]: value }));
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
      resetForm();
      fetchOrders();
    } catch (err) {
      setError(err || 'Failed to save order');
    }
  };

  const resetForm = () => {
    setOrder({ customer_id: '', order_items: [] });
    setEditMode(false);
    setOrderId(null);
    setError('');
    setSuccess('');
  };

  const handleEdit = (ord) => {
    setOrder({
      customer_id: ord.customer_id,
      order_items: ord.order_items.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
      })),
    });
    setEditMode(true);
    setOrderId(ord.order_id);
  };

  const handleDelete = async (id) => {
    try {
      await deleteOrder(id);
      setSuccess('Order deleted successfully!');
      fetchOrders();
    } catch (err) {
      setError('Failed to delete order');
    }
  };

  return (
    <Container className="mt-5">
      <Row>
        <Col>
          <h2 className="text-center">{editMode ? 'Edit Order' : 'Add Order'}</h2>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="customer_id">
              <Form.Label>Customer</Form.Label>
              <Form.Control
                as="select"
                name="customer_id"
                value={order.customer_id}
                onChange={handleChange}
                required
              >
                <option value="">Select Customer</option>
                {customers.map((cust) => (
                  <option key={cust.id} value={cust.id}>
                    {cust.name}
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
            <h4 className="mt-4">Order Items</h4>
            {order.order_items.map((item, index) => (
              <div key={`${item.product_id}-${index}`} className="d-flex align-items-center mb-3">
                <Form.Control
                  as="select"
                  value={item.product_id}
                  onChange={(e) => handleItemChange(index, 'product_id', e.target.value)}
                  className="me-2"
                  required
                >
                  <option value="">Select Product</option>
                  {products.map((prod) => (
                    <option key={prod.id} value={prod.id}>
                      {prod.name}
                    </option>
                  ))}
                </Form.Control>
                <Form.Control
                  type="number"
                  value={item.quantity}
                  onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                  className="me-2"
                  placeholder="Quantity"
                  min="1"
                  required
                />
                <Button
                  variant="danger"
                  onClick={() =>
                    setOrder((prev) => ({
                      ...prev,
                      order_items: prev.order_items.filter((_, i) => i !== index),
                    }))
                  }
                >
                  Remove
                </Button>
              </div>
            ))}
            <Button variant="secondary" onClick={handleAddItem} className="mb-3">
              Add Item
            </Button>
            <Button type="submit" className="w-100">
              {editMode ? 'Update Order' : 'Submit Order'}
            </Button>
          </Form>
        </Col>
      </Row>
      <Row className="mt-5">
        <Col>
          <h3>Order List</h3>
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Order Items</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((ord) => (
                <tr key={ord.order_id}>
                  <td>{ord.customer_name}</td>
                  <td>
                    {ord.order_items.map((item, index) => (
                      <div key={`${item.product_id}-${index}`}>
                        Product ID: {item.product_id}, Quantity: {item.quantity}
                      </div>
                    ))}
                  </td>
                  <td>
                    <Button variant="warning" onClick={() => handleEdit(ord)}>
                      Edit
                    </Button>{' '}
                    <Button variant="danger" onClick={() => handleDelete(ord.order_id)}>
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

export default OrderPage;

