import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  withCredentials: true,
  headers: { 
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

const getCSRFToken = () => {
  const cookies = document.cookie.split(';');
  const csrfCookie = cookies.find(c => c.trim().startsWith('csrftoken='));
  return csrfCookie ? csrfCookie.split('=')[1] : null;
};

// Fetch CSRF token on app initialization
let csrfInitialized = false;
export const initializeCSRF = async () => {
  if (!csrfInitialized) {
    try {
      console.log('Fetching CSRF token...');
      await api.get('/csrf/');
      csrfInitialized = true;
      console.log('CSRF token fetched successfully');
    } catch (error) {
      console.error('Failed to fetch CSRF token:', error);
      throw error;
    }
  }
};

api.interceptors.request.use(
  config => {
    const token = getCSRFToken();
    if (token) {
      config.headers['X-CSRFToken'] = token;
    }
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  response => {
    console.log(`API Response: ${response.config.url} - ${response.status}`);
    return response;
  },
  async error => {
    console.error('API Error:', error.response?.status, error.response?.data || error.message);
    
    // If 403 and CSRF token issue, try to refetch CSRF token
    if (error.response?.status === 403 && !error.config._retry) {
      error.config._retry = true;
      try {
        await api.get('/csrf/');
        const token = getCSRFToken();
        if (token) {
          error.config.headers['X-CSRFToken'] = token;
          return api.request(error.config);
        }
      } catch (retryError) {
        console.error('Failed to retry with new CSRF token:', retryError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
