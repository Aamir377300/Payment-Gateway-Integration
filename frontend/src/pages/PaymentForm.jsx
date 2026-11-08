import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

const PRESETS = ['499', '1299', '2499'];

const PaymentForm = () => {
  const [formData, setFormData] = useState({ amount: '1299', description: '' });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { config } = useAuth();
  const navigate = useNavigate();
  const chargeMode = config?.charge_mode || 'sandbox';

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const response = await api.post('/payments/create-order/', formData);
      navigate('/checkout', { state: { orderData: response.data } });
    } catch (err) {
      setError(err.response?.data?.error || 'Could not open checkout');
      setSubmitting(false);
    }
  };

  return (
    <section className="page">
      <div className="container narrow">
        <p className="eyebrow">Checkout</p>
        <h1>New payment</h1>
        <p className="lede">
          {chargeMode === 'live' && 'This opens Razorpay and can charge a real card. The payment is saved only after the signature matches.'}
          {chargeMode === 'test' && 'This opens Razorpay test checkout. Use a test card. Nothing real is charged, and the same screen is used when you switch to live keys.'}
          {chargeMode === 'sandbox' && 'This is practice checkout. Paid, declined, and cancelled are recorded here. Add your Razorpay keys to use the real checkout on this same screen.'}
        </p>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <form onSubmit={handleSubmit} className="panel stack">
          <label className="field">
            Amount (INR)
            <div className="presets">
              {PRESETS.map((amount) => (
                <button
                  type="button"
                  key={amount}
                  className={formData.amount === amount ? 'chip active' : 'chip'}
                  onClick={() => setFormData({ ...formData, amount })}
                >
                  ₹{amount}
                </button>
              ))}
            </div>
            <input
              type="number"
              className="form-control"
              min="1"
              max="100000"
              step="0.01"
              value={formData.amount}
              onChange={(event) => setFormData({ ...formData, amount: event.target.value })}
              required
            />
            <span className="hint">From ₹1 to ₹1,00,000. Two decimal places.</span>
          </label>
          <label className="field">
            What is this for?
            <input
              className="form-control"
              maxLength={200}
              placeholder="Workshop seat, invoice 104, print deposit"
              value={formData.description}
              onChange={(event) => setFormData({ ...formData, description: event.target.value })}
              required
            />
          </label>
          <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? 'Creating order…' : 'Continue to checkout'}
          </button>
          <Link to="/dashboard" className="back-link">Back to dashboard</Link>
        </form>
      </div>
    </section>
  );
};

export default PaymentForm;
