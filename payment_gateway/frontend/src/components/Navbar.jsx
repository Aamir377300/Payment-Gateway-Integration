import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const getInitial = () => {
    if (user?.first_name) return user.first_name[0].toUpperCase();
    if (user?.username) return user.username[0].toUpperCase();
    return 'U';
  };

  return (
    <nav className="navbar">
      <div className="container">
        <div className="nav-brand">
          <Link to="/">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="url(#gradient)" />
              <path d="M16 8L22 14L16 20L10 14L16 8Z" fill="white" />
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32">
                  <stop offset="0%" stopColor="#667eea" />
                  <stop offset="100%" stopColor="#764ba2" />
                </linearGradient>
              </defs>
            </svg>
            <span>PayGate</span>
          </Link>
        </div>
        <div className="nav-links">
          {user ? (
            <div className="user-menu" ref={dropdownRef}>
              <button className="user-avatar" onClick={() => setShowDropdown(!showDropdown)}>
                <span className="avatar-text">{getInitial()}</span>
              </button>
              <div className={`dropdown-menu ${showDropdown ? 'show' : ''}`}>
                <div className="dropdown-header">
                  <div className="dropdown-user-info">
                    <strong>{user.first_name || user.email}</strong>
                    <span>{user.email}</span>
                  </div>
                </div>
                <div className="dropdown-divider"></div>
                <Link to="/dashboard" className="dropdown-item" onClick={() => setShowDropdown(false)}>
                  Dashboard
                </Link>
                <Link to="/transactions" className="dropdown-item" onClick={() => setShowDropdown(false)}>
                  Transactions
                </Link>
                <div className="dropdown-divider"></div>
                <button className="dropdown-item logout" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            </div>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline">Login</Link>
              <Link to="/signup" className="btn btn-primary">Sign Up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
