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
  const [submitting, setSubmitting] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const update = (key) => (event) => setFormData({ ...formData, [key]: event.target.value });

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await signup(formData);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Could not create the account');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="auth-layout">
      <div className="auth-card">
        <p className="eyebrow">New merchant</p>
        <h1>Create an account</h1>
        <p className="lede">You will get your own ledger. Payments you create stay on this account.</p>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <form onSubmit={handleSubmit} className="stack">
          <div className="split">
            <label className="field">
              First name
              <input className="form-control" value={formData.first_name} onChange={update('first_name')} required autoFocus />
            </label>
            <label className="field">
              Last name
              <input className="form-control" value={formData.last_name} onChange={update('last_name')} required />
            </label>
          </div>
          <label className="field">
            Email
            <input type="email" className="form-control" value={formData.email} onChange={update('email')} required />
          </label>
          <label className="field">
            Password
            <input type="password" className="form-control" minLength={8} value={formData.password1} onChange={update('password1')} required />
            <span className="hint">At least 8 characters, and not a common password.</span>
          </label>
          <label className="field">
            Confirm password
            <input type="password" className="form-control" minLength={8} value={formData.password2} onChange={update('password2')} required />
          </label>
          <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? 'Creating…' : 'Create account'}
          </button>
        </form>
        <p className="auth-switch">Already registered? <Link to="/login">Log in</Link></p>
      </div>
      <aside className="auth-aside">
        <h2>What you can do next</h2>
        <ul>
          <li>Create a checkout in sandbox or Razorpay test mode</li>
          <li>Watch a payment move from pending to paid, failed, or refunded</li>
          <li>Export the ledger and open a printable receipt</li>
        </ul>
      </aside>
    </section>
  );
};

export default Signup;
