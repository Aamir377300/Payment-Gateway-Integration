import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/axios';
import StatusBadge from '../components/StatusBadge';
import { formatDate, formatINR } from '../utils/format';

const EVENT_LABELS = {
  ORDER_CREATED: 'Order created',
  PAYMENT_SUCCESS: 'Payment verified',
  PAYMENT_FAILED: 'Payment failed',
  SIGNATURE_VERIFIED: 'Signature matched',
  SIGNATURE_FAILED: 'Signature rejected',
  WEBHOOK_RECEIVED: 'Webhook received',
  REFUND: 'Refunded',
};

const TransactionDetail = () => {
  const { transactionId } = useParams();
  const [transaction, setTransaction] = useState(null);
  const [error, setError] = useState('');
  const [refunding, setRefunding] = useState(false);
  const [confirmRefund, setConfirmRefund] = useState(false);

  const load = async () => {
    const response = await api.get(`/payments/transactions/${transactionId}/`);
    setTransaction(response.data);
  };

  useEffect(() => {
    let ignore = false;
    api.get(`/payments/transactions/${transactionId}/`)
      .then((response) => {
        if (!ignore) setTransaction(response.data);
      })
      .catch(() => {
        if (!ignore) setError('This payment could not be found.');
      });
    return () => {
      ignore = true;
    };
  }, [transactionId]);

  const refund = async () => {
    setConfirmRefund(false);
    setRefunding(true);
    setError('');
    try {
      await api.post(`/payments/transactions/${transactionId}/refund/`);
      await load();
    } catch (err) {
      setError(err.response?.data?.error || 'Refund failed');
    } finally {
      setRefunding(false);
    }
  };

  if (error && !transaction) {
    return (
      <section className="page">
        <div className="container narrow">
          <div className="alert alert-error">{error}</div>
          <Link to="/transactions">Back to history</Link>
        </div>
      </section>
    );
  }

  if (!transaction) {
    return <section className="page"><div className="container"><p className="empty">Loading receipt…</p></div></section>;
  }

  return (
    <section className="page">
      <div className="container narrow">
        <Link to="/transactions" className="back-link">History</Link>
        <div className="receipt panel">
          <div className="receipt-top">
            <div>
              <p className="eyebrow">Receipt</p>
              <h1>{transaction.description || 'Payment'}</h1>
            </div>
            <StatusBadge status={transaction.status} />
          </div>
          <p className="amount">{formatINR(transaction.amount)}</p>
          {transaction.failure_reason && <p className="reason">{transaction.failure_reason}</p>}
          {error && <div className="alert alert-error">{error}</div>}
          <dl className="meta">
            <div><dt>Order</dt><dd>{transaction.order_id}</dd></div>
            <div><dt>Provider reference</dt><dd>{transaction.razorpay_order_id || '—'}</dd></div>
            <div><dt>Payment id</dt><dd>{transaction.razorpay_payment_id || '—'}</dd></div>
            <div><dt>Provider</dt><dd>{transaction.provider}</dd></div>
            <div><dt>Created</dt><dd>{formatDate(transaction.created_at)}</dd></div>
            <div><dt>Updated</dt><dd>{formatDate(transaction.updated_at)}</dd></div>
          </dl>
          <h2>Activity</h2>
          <ol className="timeline">
            {(transaction.activity || []).map((event, index) => (
              <li key={`${event.event_type}-${index}`}>
                <strong>{EVENT_LABELS[event.event_type] || event.event_type}</strong>
                <span>{event.message}</span>
                <time>{formatDate(event.created_at)}</time>
              </li>
            ))}
          </ol>
          <div className="button-row">
            <button type="button" className="btn btn-outline" onClick={() => window.print()}>Print</button>
            {transaction.status === 'SUCCESS' && !confirmRefund && (
              <button type="button" className="btn btn-danger" disabled={refunding} onClick={() => setConfirmRefund(true)}>
                {refunding ? 'Refunding…' : 'Refund payment'}
              </button>
            )}
            {confirmRefund && (
              <>
                <button type="button" className="btn btn-danger" disabled={refunding} onClick={refund}>
                  {refunding ? 'Refunding…' : 'Confirm refund'}
                </button>
                <button type="button" className="btn btn-ghost" disabled={refunding} onClick={() => setConfirmRefund(false)}>
                  Keep payment
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default TransactionDetail;
