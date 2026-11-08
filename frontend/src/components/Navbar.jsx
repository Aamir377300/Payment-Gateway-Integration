import { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    setShowDropdown(false);
    navigate('/');
  };

  const initial = (user?.first_name || user?.email || 'U')[0].toUpperCase();

  return (
    <nav className="navbar">
      <div className="container nav-inner">
        <Link to={user ? '/dashboard' : '/'} className="brand">
          <span className="brand-mark">P</span>
          <span>PayGate</span>
        </Link>
        <div className="nav-links">
          {user ? (
            <>
              <NavLink to="/dashboard" className="nav-link">Dashboard</NavLink>
              <NavLink to="/payment" className="nav-link">New payment</NavLink>
              <NavLink to="/transactions" className="nav-link">History</NavLink>
              <div className="user-menu" ref={dropdownRef}>
                <button
                  className="user-avatar"
                  onClick={() => setShowDropdown((open) => !open)}
                  aria-label="Account menu"
                  aria-expanded={showDropdown}
                >
                  {initial}
                </button>
                {showDropdown && (
                  <div className="dropdown-menu">
                    <div className="dropdown-header">
                      <strong>{user.first_name || 'Merchant'}</strong>
                      <span>{user.email}</span>
                    </div>
                    <button className="dropdown-item" onClick={handleLogout}>Log out</button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">Log in</Link>
              <Link to="/signup" className="btn btn-primary">Create account</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
