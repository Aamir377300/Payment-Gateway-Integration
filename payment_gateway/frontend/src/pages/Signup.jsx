import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Signup = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password1: '',
    password2: '',
  });
  const [error, setError] = useState('');
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await signup(formData);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Signup failed');
    }
  };

  return (
    <section className="auth-section">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Create Account</h1>
            <p>Start accepting payments in minutes</p>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">First Name</label>
                <input
                  type="text"
                  id="first_name"
                  className="form-control"
                  placeholder="John"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  required
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label htmlFor="last_name">Last Name</label>
                <input
                  type="text"
                  id="last_name"
                  className="form-control"
                  placeholder="Doe"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                className="form-control"
                placeholder="john@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password1">Password</label>
              <input
                type="password"
                id="password1"
                className="form-control"
                placeholder="Create a password"
                value={formData.password1}
                onChange={(e) => setFormData({ ...formData, password1: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password2">Confirm Password</label>
              <input
                type="password"
                id="password2"
                className="form-control"
                placeholder="Re-enter your password"
                value={formData.password2}
                onChange={(e) => setFormData({ ...formData, password2: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input type="checkbox" name="terms" required />
                <span>I agree to the <a href="#" className="link">Terms of Service</a> and <a href="#" className="link">Privacy Policy</a></span>
              </label>
            </div>

            <button type="submit" className="btn btn-primary btn-block">
              Create Account
            </button>
          </form>

          <div className="auth-footer">
            <p>Already have an account? <Link to="/login" className="link">Login</Link></p>
          </div>
        </div>

        <div className="auth-visual">
          <div className="visual-content">
            <h2>Why Choose PayGate?</h2>
            <p>Everything you need to manage payments efficiently and securely.</p>
            <div className="visual-features">
              <div className="visual-feature">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M9 12L11 14L15 10" stroke="#667eea" strokeWidth="2" strokeLinecap="round" />
                  <circle cx="12" cy="12" r="9" stroke="#667eea" strokeWidth="2" />
                </svg>
                <span>Easy integration with Razorpay</span>
              </div>
              <div className="visual-feature">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M9 12L11 14L15 10" stroke="#667eea" strokeWidth="2" strokeLinecap="round" />
                  <circle cx="12" cy="12" r="9" stroke="#667eea" strokeWidth="2" />
                </svg>
                <span>Complete transaction history</span>
              </div>
              <div className="visual-feature">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M9 12L11 14L15 10" stroke="#667eea" strokeWidth="2" strokeLinecap="round" />
                  <circle cx="12" cy="12" r="9" stroke="#667eea" strokeWidth="2" />
                </svg>
                <span>Webhook verification</span>
              </div>
              <div className="visual-feature">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M9 12L11 14L15 10" stroke="#667eea" strokeWidth="2" strokeLinecap="round" />
                  <circle cx="12" cy="12" r="9" stroke="#667eea" strokeWidth="2" />
                </svg>
                <span>Admin monitoring tools</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Signup;
