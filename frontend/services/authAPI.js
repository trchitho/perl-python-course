import { apiPost } from './apiConfig.js';

export async function login(email, password) {
  try {
    return await apiPost('/auth/login', { email, password });
  } catch (error) {
    throw new Error(error.message || 'Login failed. Please check your credentials.');
  }
}

export async function register(data) {
  try {
    return await apiPost('/auth/register', data);
  } catch (error) {
    throw new Error(error.message || 'Registration failed. Please try again.');
  }
}
