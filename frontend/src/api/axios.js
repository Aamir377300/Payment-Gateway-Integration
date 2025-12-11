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

let csrfInitialized = false;
export const initializeCSRF = async () => {
  if (!csrfInitialized) {
    try {
      await api.get('/csrf/');
      csrfInitialized = true;
    } catch (error) {
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
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    return Promise.reject(error);
  }
);

export default api;
