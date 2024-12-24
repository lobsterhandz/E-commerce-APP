import React from 'react';
import { Routes, Route } from 'react-router-dom';
import CustomerPage from '../pages/CustomerPage';
import ProductPage from '../pages/ProductPage';
import OrderPage from '../pages/OrderPage';
import StockManagementPage from '../pages/StockManagementPage';
import NotFoundPage from '../pages/NotFoundPage';
import HomePage from "../pages/HomePage"; 

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} /> {/* Default home page */}
      <Route path="/customers" element={<CustomerPage />} />
      <Route path="/products" element={<ProductPage />} />
      <Route path="/orders" element={<OrderPage />} />
      <Route path="/stock-management" element={<StockManagementPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRoutes;
