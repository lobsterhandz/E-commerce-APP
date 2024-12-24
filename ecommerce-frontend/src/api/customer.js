import axiosInstance from './axios';

/**
 * API function to create a customer.
 * @param {Object} data - Customer data to create.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const createCustomer = async (data) => {
  try {
    const response = await axiosInstance.post('/customers/customer', data);
    return response.data;
  } catch (error) {
    handleError(error, 'Error creating customer');
  }
};

/**
 * API function to fetch customers.
 * Fetch all customers if no ID is provided, or fetch a specific customer by ID.
 * @param {String} [id] - Customer ID (optional).
 * @returns {Object|Array} Response data.
 * @throws {String} Error message.
 */
export const getCustomers = async (id = '') => {
  try {
    const endpoint = id ? `/customers/customer/${id}` : '/customers/customers';
    const response = await axiosInstance.get(endpoint);
    return response.data;
  } catch (error) {
    handleError(error, 'Error fetching customers');
  }
};

/**
 * API function to update a customer by ID.
 * @param {String} id - Customer ID.
 * @param {Object} data - Data to update the customer.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const updateCustomer = async (id, data) => {
  try {
    const response = await axiosInstance.put(`/customers/customer/${id}`, data);
    return response.data;
  } catch (error) {
    handleError(error, 'Error updating customer');
  }
};

/**
 * API function to delete a customer by ID.
 * @param {String} id - Customer ID.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const deleteCustomer = async (id) => {
  try {
    const response = await axiosInstance.delete(`/customers/customer/${id}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Error deleting customer');
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
