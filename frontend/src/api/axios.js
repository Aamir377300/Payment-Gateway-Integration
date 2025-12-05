import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  withCredentials: true,
  headers: { 
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Store CSRF token in memory as fallback
let csrfTokenCache = null;

const getCSRFToken = () => {
  // First try to get from cookie
  const cookies = document.cookie.split(';');
  const csrfCookie = cookies.find(c => c.trim().startsWith('csrftoken='));
  const cookieToken = csrfCookie ? csrfCookie.split('=')[1] : null;
  
  // Return cookie token if available, otherwise use cached token
  return cookieToken || csrfTokenCache;
};

// Fetch CSRF token on app initialization
let csrfInitialized = false;
export const initializeCSRF = async () => {
  if (!csrfInitialized) {
    try {
      console.log('Fetching CSRF token...');
      const response = await api.get('/csrf/');
      
      // Store token from response body as fallback
      if (response.data?.csrfToken) {
        csrfTokenCache = response.data.csrfToken;
        console.log('CSRF token cached from response');
      }
      
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
    const status = error.response?.status;
    const url = error.config?.url;
    
    // Don't log 401/403 on /auth/user/ as errors (expected for unauthenticated users)
    if ((status === 401 || status === 403) && url?.includes('/auth/user/')) {
      console.log(`User not authenticated (${status})`);
    } else {
      console.error('API Error:', status, error.response?.data || error.message);
    }
    
    // If 403 and CSRF error, try to refetch CSRF token
    if (status === 403 && 
        error.response?.data?.detail?.includes('CSRF') && 
        !url?.includes('/csrf/') && 
        !error.config._retry) {
      error.config._retry = true;
      try {
        console.log('CSRF token missing or invalid. Fetching new token...');
        const csrfResponse = await api.get('/csrf/');
        
        // Cache token from response body
        if (csrfResponse.data?.csrfToken) {
          csrfTokenCache = csrfResponse.data.csrfToken;
          console.log('CSRF token cached from response');
        }
        
        // Wait a bit for cookie to be set
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Get token (will use cookie or cache)
        const token = getCSRFToken();
        
        if (token) {
          error.config.headers['X-CSRFToken'] = token;
          console.log('Retrying request with new CSRF token');
          return api.request(error.config);
        } else {
          console.error('Failed to obtain CSRF token');
        }
      } catch (retryError) {
        console.error('Failed to retry with new CSRF token:', retryError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
