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
      // User is not authenticated, which is fine
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    console.log('🔐 AuthContext: Logging in user...');
    const { data } = await api.post('/auth/login/', { email, password });
    console.log('✅ AuthContext: Login response received, setting user:', data.user.username);
    setUser(data.user);
    console.log('✅ AuthContext: User state updated');
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
