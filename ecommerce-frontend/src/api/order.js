import axiosInstance from './axios';

/**
 * API function to create an order.
 * @param {Object} data - Order data to create.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const createOrder = async (data) => {
  try {
    const response = await axiosInstance.post('/orders/order', data);
    return response.data;
  } catch (error) {
    handleError(error, 'Error creating order');
  }
};

/**
 * API function to fetch orders.
 * Fetch all orders if no ID is provided, or fetch a specific order by ID.
 * @param {String} [id] - Order ID (optional).
 * @returns {Object|Array} Response data.
 * @throws {String} Error message.
 */
export const getOrder = async (id = '') => {
    const endpoint = id ? `/orders/order/${id}` : '/orders/orders'; // Ensure correct URL
    try {
        const response = await axiosInstance.get(endpoint);
        return response.data;
    } catch (error) {
        handleError(error, 'Error fetching order(s)');
    }
};

/**
 * API function to update an order by ID.
 * @param {String} id - Order ID.
 * @param {Object} data - Data to update the order.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const updateOrder = async (id, data) => {
  try {
    const response = await axiosInstance.put(`/orders/order/${id}`, data);
    return response.data;
  } catch (error) {
    handleError(error, 'Error updating order');
  }
};

/**
 * API function to delete an order by ID.
 * @param {String} id - Order ID.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const deleteOrder = async (id) => {
  try {
    const response = await axiosInstance.delete(`/orders/order/${id}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Error deleting order');
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
