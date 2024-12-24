import axiosInstance from './axios';

/**
 * API function to create a product.
 * @param {Object} data - Product data to create.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const createProduct = async (data) => {
  try {
    const response = await axiosInstance.post('/products/product', data);
    return response.data;
  } catch (error) {
    handleError(error, 'Error creating product');
  }
};

/**
 * API function to fetch products.
 * Fetch all products if no ID is provided, or fetch a specific product by ID.
 * @param {String} [id] - Product ID (optional).
 * @returns {Object|Array} Response data.
 * @throws {String} Error message.
 */
export const getProducts = async (id = '') => {
  try {
    const endpoint = id ? `/products/product/${id}` : '/products/products';
    const response = await axiosInstance.get(endpoint);
    return response.data;
  } catch (error) {
    handleError(error, 'Error fetching product(s)');
  }
};

/**
 * API function to update a product by ID.
 * @param {String} id - Product ID.
 * @param {Object} data - Data to update the product.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const updateProduct = async (id, data) => {
  try {
    const response = await axiosInstance.put(`/products/product/${id}`, data);
    return response.data;
  } catch (error) {
    handleError(error, 'Error updating product');
  }
};

/**
 * API function to delete a product by ID.
 * @param {String} id - Product ID.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const deleteProduct = async (id) => {
  try {
    const response = await axiosInstance.delete(`/products/product/${id}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Error deleting product');
  }
};

/**
 * Utility function to handle API errors.
 * Logs the error and throws a formatted error message.
 * @param {Object} error - Axios error object.
 * @param {String} defaultMessage - Default error message to throw.
 * @throws {String} Formatted error message.
 */
const handleError = (error, defaultMessage) => {
  console.error(error);
  const errorMessage = error.response?.data?.error || defaultMessage;
  throw errorMessage;
};
