import React, { useState, useEffect } from 'react';
import { Form, Button, Container, Row, Col, Alert, Table } from 'react-bootstrap';
import { createCustomerAccount, getCustomerAccount, updateCustomerAccount, deleteCustomerAccount } from '../api/customerAccount';

const CustomerAccountForm = () => {
  const [account, setAccount] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [accounts, setAccounts] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [accountId, setAccountId] = useState(null);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await getCustomerAccount(''); // Fetch all accounts
      setAccounts(response);
    } catch (err) {
      setError('Failed to fetch accounts');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setAccount({ ...account, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editMode) {
        await updateCustomerAccount(accountId, account);
        setSuccess('Account updated successfully!');
      } else {
        await createCustomerAccount(account);
        setSuccess('Account created successfully!');
      }
      setError('');
      setAccount({ username: '', password: '' });
      setEditMode(false);
      setAccountId(null);
      fetchAccounts();
    } catch (err) {
      setError(err);
      setSuccess('');
    }
  };

  const handleEdit = (account) => {
    setAccount({ username: account.username, password: '' }); // Password reset for security
    setEditMode(true);
    setAccountId(account.id);
    setSuccess('');
    setError('');
  };

  const handleDelete = async (id) => {
    try {
      await deleteCustomerAccount(id);
      setSuccess('Account deleted successfully!');
      setError('');
      fetchAccounts();
    } catch (err) {
      setError('Failed to delete account');
      setSuccess('');
    }
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={6}>
          <h2 className="text-center">{editMode ? 'Edit Account' : 'Create Account'}</h2>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="username">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                name="username"
                value={account.username}
                onChange={handleChange}
                placeholder="Enter username"
                required
              />
            </Form.Group>
            <Form.Group controlId="password" className="mt-3">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                name="password"
                value={account.password}
                onChange={handleChange}
                placeholder="Enter password"
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
          <h3 className="text-center">Customer Accounts</h3>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Username</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {accounts.map((acc) => (
                <tr key={acc.id}>
                  <td>{acc.username}</td>
                  <td>
                    <Button
                      variant="warning"
                      className="me-2"
                      onClick={() => handleEdit(acc)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="danger"
                      onClick={() => handleDelete(acc.id)}
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

export default CustomerAccountForm;
