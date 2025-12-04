import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api/axios';

const Checkout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const orderData = location.state?.orderData;
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!orderData) {
      navigate('/payment');
      return;
    }

    if (!orderData.razorpay_key_id || !orderData.razorpay_order_id || !orderData.amount_in_paise) {
      setError('Invalid order data');
      setIsLoading(false);
      return;
    }
    // razorpay window pop up 
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    script.onload = () => setIsLoading(false);
    script.onerror = () => {
      setError('Failed to load payment gateway');
      setIsLoading(false);
    };
    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [orderData, navigate]);

  const handlePayment = () => {
    if (!window.Razorpay) {
      setError('Razorpay not loaded');
      return;
    }

    const amount = parseInt(orderData.amount_in_paise);
    if (isNaN(amount) || amount <= 0) {
      setError('Invalid amount');
      return;
    }

    const options = {
      key: orderData.razorpay_key_id,
      amount: amount,
      currency: 'INR',
      name: 'PayGate',
      description: orderData.description || 'Payment',
      order_id: orderData.razorpay_order_id,
      handler: async (response) => {
        try {
          await api.post('/payments/verify/', {
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          });
          navigate(`/payment-success/${orderData.transaction.id}`);
        } catch (error) {
          navigate(`/payment-failure/${orderData.transaction.id}`);
        }
      },
      prefill: {
        name: orderData.user_name || '',
        email: orderData.user_email || '',
        contact: orderData.user_contact || '',
      },
      method: { upi: true, card: true, netbanking: true, wallet: true },
      theme: { color: '#667eea' },
      modal: { ondismiss: () => navigate(`/payment-failure/${orderData.transaction.id}`) }
    };

    try {
      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', (response) => {
        setError(response.error?.description || 'Payment failed');
      });
      rzp.open();
    } catch (error) {
      setError('Failed to open payment');
    }
  };

  if (!orderData) return null;

  if (error) {
    return (
      <section className="auth-section">
        <div className="container" style={{ maxWidth: '600px', textAlign: 'center' }}>
          <div className="auth-card">
            <div style={{ fontSize: '80px', marginBottom: '20px' }}>⚠️</div>
            <h1>Payment Issue</h1>
            <div className="alert alert-error" style={{ marginBottom: '30px' }}>
              {error}
            </div>
            <button onClick={() => setError('')} className="btn btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="auth-section">
      <div className="container" style={{ maxWidth: '600px' }}>
        <div className="auth-card">
          <div className="auth-header">
            <h1>🔒 Secure Checkout</h1>
            <p>Complete your payment securely</p>
          </div>

          <div style={{ margin: '30px 0', background: '#f8f9fa', padding: '20px', borderRadius: '8px' }}>
            <h3 style={{ marginBottom: '15px' }}>Payment Details</h3>
            <table style={{ width: '100%' }}>
              <tbody>
                <tr>
                  <td style={{ padding: '8px', color: '#666' }}>Order ID:</td>
                  <td style={{ padding: '8px' }}><strong>{orderData.transaction.order_id}</strong></td>
                </tr>
                <tr>
                  <td style={{ padding: '8px', color: '#666' }}>Description:</td>
                  <td style={{ padding: '8px' }}>{orderData.description || 'Payment'}</td>
                </tr>
                <tr>
                  <td style={{ padding: '8px', color: '#666' }}>Amount:</td>
                  <td style={{ padding: '8px', fontSize: '24px', color: '#667eea' }}>
                    <strong>₹{orderData.amount}</strong>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <button
            onClick={handlePayment}
            className="btn btn-primary btn-block"
            disabled={isLoading}
            style={{ 
              padding: '15px',
              fontSize: '18px',
              fontWeight: 'bold'
            }}
          >
            {isLoading ? 'Loading Payment Gateway...' : `Pay ₹${orderData.amount}`}
          </button>

          <div style={{ 
            marginTop: '20px', 
            padding: '15px', 
            background: '#e7f3ff', 
            borderRadius: '8px',
            fontSize: '14px',
            textAlign: 'center'
          }}>
            <p style={{ margin: 0, color: '#666' }}>
              🔐 Secured by Razorpay • All payment methods accepted
            </p>
          </div>

          <div className="auth-footer" style={{ marginTop: '20px' }}>
            <button 
              onClick={() => navigate('/payment')} 
              className="link"
              style={{ background: 'none', border: 'none', cursor: 'pointer' }}
            >
              ← Back to Payment Form
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Checkout;
