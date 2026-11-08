import { createContext, useState, useEffect, useContext } from 'react';
import api, { initializeCSRF } from '../api/axios';

const AuthContext = createContext();

// Hook and provider live together so pages can call useAuth() without a second module.
// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    const initApp = async () => {
      try {
        await initializeCSRF();
        const [configResult, userResult] = await Promise.allSettled([
          api.get('/config/'),
          api.get('/auth/user/'),
        ]);
        if (ignore) return;
        if (configResult.status === 'fulfilled') {
          setConfig(configResult.value.data);
        }
        setUser(userResult.status === 'fulfilled' ? userResult.value.data : null);
      } catch {
        if (!ignore) setUser(null);
      } finally {
        if (!ignore) setLoading(false);
      }
    };
    initApp();
    return () => {
      ignore = true;
    };
  }, []);

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
    <AuthContext.Provider value={{ user, config, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
