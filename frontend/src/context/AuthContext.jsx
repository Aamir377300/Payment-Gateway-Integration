import { createContext, useState, useEffect, useContext } from 'react';
import api, { initializeCSRF } from '../api/axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initApp();
  }, []);

  const initApp = async () => {
    try {
      // First, initialize CSRF token
      await initializeCSRF();
      // Then check if user is authenticated
      await checkAuth();
    } catch (error) {
      console.error('App initialization error:', error);
      setUser(null);
      setLoading(false);
    }
  };

  const checkAuth = async () => {
    try {
      const { data } = await api.get('/auth/user/');
      setUser(data);
    } catch (error) {
      // 401/403 means user is not authenticated - this is expected
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.log('User not authenticated (expected for first visit)');
      } else {
        console.error('Unexpected auth check error:', error);
      }
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login/', { email, password });
    setUser(data.user);
    return data;
  };

  const signup = async (userData) => {
    const { data } = await api.post('/auth/signup/', userData);
    return data;
  };

  const logout = async () => {
    await api.post('/auth/logout/');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};
