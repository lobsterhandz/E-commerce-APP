import React from 'react';
import StockManagement from '../components/StockManagement';

/**
 * StockManagementPage Component
 * A page that renders the StockManagement component.
 */
const StockManagementPage = () => {
  return (
    <div className="container mt-4">
      <h1>Stock Management</h1>
      <StockManagement />
    </div>
  );
};

export default StockManagementPage;
