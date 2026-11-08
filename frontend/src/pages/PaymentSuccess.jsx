import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/axios';
import StatusBadge from '../components/StatusBadge';
import { formatDate, formatINR } from '../utils/format';

const PaymentSuccess = () => {
  const { transactionId } = useParams();
  const [transaction, setTransaction] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get(`/payments/transactions/${transactionId}/`)
      .then((response) => setTransaction(response.data))
      .catch(() => setError('This receipt could not be loaded.'));
  }, [transactionId]);

  return (
    <section className="page">
      <div className="container narrow">
        <p className="eyebrow">Payment recorded</p>
        <h1>Paid</h1>
        {error && <div className="alert alert-error">{error}</div>}
        {!transaction && !error && <p className="empty">Loading receipt…</p>}
        {transaction && (
          <div className="panel">
            <StatusBadge status={transaction.status} />
            <p className="amount">{formatINR(transaction.amount)}</p>
            <p>{transaction.description}</p>
            <dl className="meta">
              <div><dt>Order</dt><dd>{transaction.order_id}</dd></div>
              <div><dt>Payment</dt><dd>{transaction.razorpay_payment_id || '—'}</dd></div>
              <div><dt>When</dt><dd>{formatDate(transaction.created_at)}</dd></div>
            </dl>
            <div className="button-row">
              <Link to={`/transactions/${transaction.id}`} className="btn btn-primary">Open receipt</Link>
              <Link to="/transactions" className="btn btn-outline">History</Link>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default PaymentSuccess;
