import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/axios';

const PaymentForm = () => {
  const [formData, setFormData] = useState({ amount: '', description: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await api.post('/payments/create-order/', formData);
      navigate('/checkout', { state: { orderData: response.data } });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create order');
    }
  };

  return (
    <section className="auth-section">
      <div className="container" style={{ maxWidth: '600px' }}>
        <div className="auth-card">
          <div className="auth-header">
            <h1>💳 Make a Payment</h1>
            <p>Enter payment details below</p>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="amount">Amount (₹)</label>
              <input
                type="number"
                className="form-control"
                id="amount"
                step="0.01"
                min="1"
                placeholder="Enter amount"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                required
              />
              <span className="form-hint">Minimum amount: ₹1</span>
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                className="form-control"
                id="description"
                rows="3"
                placeholder="What is this payment for?"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              ></textarea>
            </div>

            <button type="submit" className="btn btn-primary btn-block">
              Proceed to Payment
            </button>
          </form>

          <div className="auth-footer">
            <Link to="/dashboard" className="link">← Back to Dashboard</Link>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PaymentForm;
