import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { formatINR } from '../utils/format';

const Checkout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const orderData = location.state?.orderData;
  const chargeMode = orderData?.charge_mode || (orderData?.payment_mode === 'sandbox' ? 'sandbox' : 'test');
  const sandbox = chargeMode === 'sandbox';
  const missingGateway = Boolean(
    orderData && !sandbox && (!orderData.razorpay_key_id || !orderData.razorpay_order_id)
  );
  const [error, setError] = useState(
    missingGateway ? 'This order is missing Razorpay checkout details.' : ''
  );
  const [busy, setBusy] = useState(false);
  const [gatewayReady, setGatewayReady] = useState(Boolean(sandbox));

  useEffect(() => {
    if (!orderData) {
      navigate('/payment', { replace: true });
      return undefined;
    }
    if (sandbox) {
      return undefined;
    }
    if (!orderData.razorpay_key_id || !orderData.razorpay_order_id) {
      return undefined;
    }
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    script.onload = () => setGatewayReady(true);
    script.onerror = () => setError('Razorpay checkout could not be loaded.');
    document.body.appendChild(script);
    return () => {
      if (document.body.contains(script)) document.body.removeChild(script);
    };
  }, [orderData, navigate, sandbox]);

  const finishFailure = async (reason) => {
    await api.post('/payments/failure/', {
      transaction_id: orderData.transaction.id,
      reason,
    });
    navigate(`/payment-failure/${orderData.transaction.id}`);
  };

  const recordSandbox = async (outcome) => {
    setBusy(true);
    setError('');
    try {
      if (outcome === 'cancel') {
        await finishFailure('Checkout was cancelled.');
        return;
      }
      const { data } = await api.post('/payments/sandbox/complete/', {
        transaction_id: orderData.transaction.id,
        outcome,
      });
      const path = data.transaction.status === 'SUCCESS' ? 'payment-success' : 'payment-failure';
      navigate(`/${path}/${data.transaction.id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Could not record the sandbox payment');
      setBusy(false);
    }
  };

  const openRazorpay = () => {
    if (!window.Razorpay) {
      setError('Razorpay is not ready yet.');
      return;
    }
    const options = {
      key: orderData.razorpay_key_id,
      amount: orderData.amount_in_paise,
      currency: 'INR',
      name: 'PayGate',
      description: orderData.description,
      order_id: orderData.razorpay_order_id,
      prefill: {
        name: orderData.user_name || '',
        email: orderData.user_email || '',
      },
      theme: { color: '#0e6b56' },
      handler: async (response) => {
        try {
          await api.post('/payments/verify/', {
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          });
          navigate(`/payment-success/${orderData.transaction.id}`);
        } catch {
          navigate(`/payment-failure/${orderData.transaction.id}`);
        }
      },
      modal: {
        ondismiss: () => {
          finishFailure('Checkout was cancelled.');
        },
      },
    };
    const checkout = new window.Razorpay(options);
    checkout.on('payment.failed', () => {
      finishFailure('The card was declined.');
    });
    checkout.open();
  };

  if (!orderData) return null;

  return (
    <section className="page">
      <div className="container narrow">
        <p className="eyebrow">
          {chargeMode === 'live' && 'Live Razorpay checkout'}
          {chargeMode === 'test' && 'Razorpay test checkout'}
          {chargeMode === 'sandbox' && 'Sandbox checkout'}
        </p>
        <h1>{formatINR(orderData.amount)}</h1>
        <p className="lede">{orderData.description}</p>
        {error && <div className="alert alert-error" role="alert">{error}</div>}

        <div className="panel">
          <dl className="meta">
            <div><dt>Order</dt><dd>{orderData.transaction.order_id}</dd></div>
            <div>
              <dt>Provider</dt>
              <dd>{chargeMode === 'live' ? 'Razorpay live' : chargeMode === 'test' ? 'Razorpay test' : 'Sandbox'}</dd>
            </div>
          </dl>

          {sandbox ? (
            <div className="choice-grid">
              <button className="btn btn-primary" disabled={busy} onClick={() => recordSandbox('success')}>
                Mark as paid
              </button>
              <button className="btn btn-outline" disabled={busy} onClick={() => recordSandbox('failed')}>
                Decline the card
              </button>
              <button className="btn btn-ghost" disabled={busy} onClick={() => recordSandbox('cancel')}>
                Cancel checkout
              </button>
            </div>
          ) : (
            <button className="btn btn-primary btn-block" disabled={!gatewayReady || busy} onClick={openRazorpay}>
              {gatewayReady ? `Pay ${formatINR(orderData.amount)}` : 'Loading Razorpay…'}
            </button>
          )}
          <p className="hint center">
            {chargeMode === 'sandbox' && 'These buttons call the same verification path a real Razorpay signature uses.'}
            {chargeMode === 'test' && 'Test card 4111 1111 1111 1111, any future expiry, any CVV. PayGate accepts it only if the signature matches.'}
            {chargeMode === 'live' && 'This can charge a real card. PayGate accepts the payment only if the Razorpay signature matches.'}
          </p>
        </div>
      </div>
    </section>
  );
};

export default Checkout;
