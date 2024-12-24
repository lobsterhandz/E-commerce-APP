import React, { useState, useEffect } from 'react';
import { Form, Button, Container, Row, Col, Alert, Table } from 'react-bootstrap';
import {
  createCustomer,
  getCustomers,
  updateCustomer,
  deleteCustomer,
} from '../api/customer';

const CustomerForm = () => {
  const [customer, setCustomer] = useState({ name: '', email: '', phone_number: '' });
  const [customers, setCustomers] = useState([]);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [customerId, setCustomerId] = useState(null);

  // Fetch customers on component load
  useEffect(() => {
    fetchCustomers();
  }, []);

  // Fetch customers from API
  const fetchCustomers = async () => {
    try {
      const data = await getCustomers();
      setCustomers(data);
    } catch (err) {
      setError('Failed to fetch customers');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCustomer((prev) => ({
      ...prev,
      [name]: value, // Dynamically update the correct field
    }));
  };
  

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editMode) {
        await updateCustomer(customerId, customer);
        setSuccess('Customer updated successfully!');
      } else {
        await createCustomer(customer);
        setSuccess('Customer added successfully!');
      }
      resetForm();
      fetchCustomers();
    } catch (err) {
      setError(err);
    }
  };

  // Reset form state
  const resetForm = () => {
    setCustomer({ name: '', email: '', phone_number: '' });
    setEditMode(false);
    setCustomerId(null);
    setSuccess('');
    setError('');
  };

  // Handle edit action
  const handleEdit = (cust) => {
    setCustomer(cust);
    setEditMode(true);
    setCustomerId(cust.id);
    setSuccess('');
    setError('');
  };

  // Handle delete action
  const handleDelete = async (id) => {
    try {
      await deleteCustomer(id);
      setSuccess('Customer deleted successfully!');
      fetchCustomers();
    } catch (err) {
      setError(err);
    }
  };

  return (
    <Container className="mt-5">
      {/* Form Section */}
      <Row className="justify-content-center">
        <Col md={6}>
          <h2>{editMode ? 'Edit Customer' : 'Add Customer'}</h2>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="name">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={customer.name}
                onChange={handleChange}
                placeholder="Enter customer's name"
                required
              />
            </Form.Group>
            <Form.Group controlId="email" className="mt-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                name="email"
                value={customer.email}
                onChange={handleChange}
                placeholder="Enter customer's email"
                required
              />
            </Form.Group>
            <Form.Group controlId="phone" className="mt-3">
              <Form.Label>Phone</Form.Label>
              <Form.Control
                type="text"
                name="phone_number"
                value={customer.phone_number}
                onChange={handleChange}
                placeholder="Enter customer's phone"
                required
              />
            </Form.Group>
            <Button type="submit" className="mt-4 w-100">
              {editMode ? 'Update' : 'Submit'}
            </Button>
          </Form>
        </Col>
      </Row>

      {/* Customer List Section */}
      <Row className="mt-5">
        <Col>
          <h3>Customer List</h3>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((cust) => (
                <tr key={cust.id}>
                  <td>{cust.name}</td>
                  <td>{cust.email}</td>
                  <td>{cust.phone}</td>
                  <td>
                    <Button variant="warning" onClick={() => handleEdit(cust)}>
                      Edit
                    </Button>{' '}
                    <Button variant="danger" onClick={() => handleDelete(cust.id)}>
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

export default CustomerForm;
