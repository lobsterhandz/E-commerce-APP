import axiosInstance from './axios';

/**
 * API function to create a customer account.
 * @param {Object} data - Customer account data to create.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const createCustomerAccount = async (data) => {
  try {
    const response = await axiosInstance.post('/customer_accounts/customer_account', data);
    return response.data;
  } catch (error) {
    handleError(error, 'Error creating customer account');
  }
};

/**
 * API function to fetch customer accounts.
 * Fetch all accounts if no ID is provided, or fetch a specific account by ID.
 * @param {String} [id] - Account ID (optional).
 * @returns {Object|Array} Response data.
 * @throws {String} Error message.
 */
export const getCustomerAccount = async (id = '') => {
  try {
    const endpoint = id ? `/customer_accounts/customer_account/${id}` : '/customer_accounts/customer_accounts';
    const response = await axiosInstance.get(endpoint);
    return response.data;
  } catch (error) {
    handleError(error, 'Error fetching customer account(s)');
  }
};

/**
 * API function to update a customer account by ID.
 * @param {String} id - Account ID.
 * @param {Object} data - Data to update the customer account.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const updateCustomerAccount = async (id, data) => {
  try {
    const response = await axiosInstance.put(`/customer_accounts/customer_account/${id}`, data);
    return response.data;
  } catch (error) {
    handleError(error, 'Error updating customer account');
  }
};

/**
 * API function to delete a customer account by ID.
 * @param {String} id - Account ID.
 * @returns {Object} Response data.
 * @throws {String} Error message.
 */
export const deleteCustomerAccount = async (id) => {
  try {
    const response = await axiosInstance.delete(`/customer_accounts/customer_account/${id}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Error deleting customer account');
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
