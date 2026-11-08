import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { login, config } = useAuth();
  const navigate = useNavigate();
  const demo = config?.demo_login;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(formData.email, formData.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="auth-layout">
      <div className="auth-card">
        <p className="eyebrow">Merchant login</p>
        <h1>Welcome back</h1>
        <p className="lede">Use your account, or the seeded demo merchant if you have run the demo setup.</p>

        {error && <div className="alert alert-error" role="alert">{error}</div>}

        {demo && (
          <div className="demo-card">
            <div>
              <strong>Demo merchant</strong>
              <p>{demo.email}</p>
              <p>{demo.password}</p>
            </div>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => setFormData({ email: demo.email, password: demo.password })}
            >
              Fill demo login
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="stack">
          <label className="field">
            Email
            <input
              type="email"
              className="form-control"
              value={formData.email}
              onChange={(event) => setFormData({ ...formData, email: event.target.value })}
              required
              autoFocus
            />
          </label>
          <label className="field">
            Password
            <input
              type="password"
              className="form-control"
              value={formData.password}
              onChange={(event) => setFormData({ ...formData, password: event.target.value })}
              required
            />
          </label>
          <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? 'Signing in…' : 'Log in'}
          </button>
        </form>
        <p className="auth-switch">No account yet? <Link to="/signup">Create one</Link></p>
      </div>
      <aside className="auth-aside">
        <h2>A desk, not a marketing page.</h2>
        <p>Log in, take a sandbox payment, then open the receipt. That is the project.</p>
      </aside>
    </section>
  );
};

export default Login;
