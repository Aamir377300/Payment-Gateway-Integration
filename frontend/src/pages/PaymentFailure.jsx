import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/axios';
import StatusBadge from '../components/StatusBadge';
import { formatINR } from '../utils/format';

const PaymentFailure = () => {
  const { transactionId } = useParams();
  const [transaction, setTransaction] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get(`/payments/transactions/${transactionId}/`);
        let current = response.data;
        if (current.status === 'PENDING') {
          const failed = await api.post('/payments/failure/', { transaction_id: transactionId });
          current = failed.data.transaction;
        }
        setTransaction(current);
      } catch {
        setError('This payment could not be loaded.');
      }
    };
    load();
  }, [transactionId]);

  return (
    <section className="page">
      <div className="container narrow">
        <p className="eyebrow">Checkout closed</p>
        <h1>Not paid</h1>
        {error && <div className="alert alert-error">{error}</div>}
        {!transaction && !error && <p className="empty">Updating the payment…</p>}
        {transaction && (
          <div className="panel">
            <StatusBadge status={transaction.status} />
            <p className="amount">{formatINR(transaction.amount)}</p>
            <p>{transaction.failure_reason || 'The payment was not completed.'}</p>
            <dl className="meta">
              <div><dt>Order</dt><dd>{transaction.order_id}</dd></div>
              <div><dt>For</dt><dd>{transaction.description}</dd></div>
            </dl>
            <div className="button-row">
              <Link to="/payment" className="btn btn-primary">Try another payment</Link>
              <Link to={`/transactions/${transaction.id}`} className="btn btn-outline">View record</Link>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default PaymentFailure;
