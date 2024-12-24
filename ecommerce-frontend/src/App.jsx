import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import Header from './components/Header';
import AppRoutes from './routes/index';

/**
 * App Component
 * Main application entry point that sets up routing and renders the header.
 */
const App = () => {
  return (
    <Router>
      <div className="d-flex flex-column min-vh-100">
        <Header />
        <main className="container d-flex justify-content-center flex-grow-1">
          <div className="w-100">
            <AppRoutes />
          </div>
        </main>
      </div>
    </Router>
  );
};

export default App;
