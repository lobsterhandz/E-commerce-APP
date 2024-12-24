import React from 'react';
import { Button, Container, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <Container className="d-flex flex-column justify-content-start align-items-center vh-100 py-4 text-center">
      <Row className="w-100">
        <Col>
          <h1>Welcome to the E-Commerce App</h1>
          <p>
            Manage your business operations seamlessly with tools for handling customers, products, and orders.
          </p>
          <div className="mt-4">
            <Link to="/customers">
              <Button variant="primary" className="m-2">
                Manage Customers
              </Button>
            </Link>
            <Link to="/products">
              <Button variant="success" className="m-2">
                Manage Products
              </Button>
            </Link>
            <Link to="/orders">
              <Button variant="info" className="m-2">
                Manage Orders
              </Button>
            </Link>
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default HomePage;
