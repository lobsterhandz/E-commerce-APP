import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx'; // Main App Component
import 'bootstrap/dist/css/bootstrap.min.css'; // Bootstrap CSS for styling
import './index.css'; // Custom CSS styles (if needed)

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
