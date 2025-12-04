import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' }
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
      await api.get('/csrf/');
      csrfInitialized = true;
    } catch (error) {
      console.error('Failed to fetch CSRF token:', error);
    }
  }
};

api.interceptors.request.use(async config => {
  // Ensure CSRF token is fetched before first request
  if (!csrfInitialized) {
    await initializeCSRF();
  }
  
  const token = getCSRFToken();
  if (token) config.headers['X-CSRFToken'] = token;
  return config;
});

export default api;
