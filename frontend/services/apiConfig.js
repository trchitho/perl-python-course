// API Configuration
export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api';

// Helper function to get auth headers
export function getAuthHeaders(token) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// Helper function to get token from localStorage
export function getToken() {
  return localStorage.getItem('token');
}

// Helper function for API calls with error handling
export async function apiCall(url, options = {}) {
  const token = getToken();
  const headers = getAuthHeaders(token);
  
  const config = {
    ...options,
    headers: {
      ...headers,
      ...(options.headers || {}),
    },
  };

  try {
    const response = await fetch(`${API_BASE}${url}`, config);
    
    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    }
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || data.message || `HTTP error! status: ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// Helper for GET requests
export async function apiGet(url) {
  return apiCall(url, { method: 'GET' });
}

// Helper for POST requests
export async function apiPost(url, body) {
  return apiCall(url, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

// Helper for PUT requests
export async function apiPut(url, body) {
  return apiCall(url, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

// Helper for PATCH requests
export async function apiPatch(url, body) {
  return apiCall(url, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
}

// Helper for DELETE requests
export async function apiDelete(url) {
  return apiCall(url, { method: 'DELETE' });
}

