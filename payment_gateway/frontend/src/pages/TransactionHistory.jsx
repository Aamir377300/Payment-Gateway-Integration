import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';

const TransactionHistory = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await api.get('/payments/transactions/');
        setTransactions(response.data);
      } catch (error) {
        // Handle error silently
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, []);

  const getStatusBadge = (status) => {
    if (status === 'SUCCESS') {
      return <span className="badge badge-success">✓ Success</span>;
    } else if (status === 'FAILED') {
      return <span className="badge badge-danger">✗ Failed</span>;
    } else if (status === 'PENDING') {
      return <span className="badge badge-warning">⏳ Pending</span>;
    }
    return <span className="badge">{status}</span>;
  };

  if (loading) return <div>Loading...</div>;

  return (
    <section className="history-section">
      <div className="container">
        <h1>📊 Transaction History</h1>

        {transactions.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="transaction-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Amount</th>
                  <th>Description</th>
                  <th>Status</th>
                  <th>Payment ID</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td>{transaction.order_id}</td>
                    <td>₹{transaction.amount}</td>
                    <td>{transaction.description || 'N/A'}</td>
                    <td>{getStatusBadge(transaction.status)}</td>
                    <td>
                      {transaction.razorpay_payment_id ? (
                        <code>{transaction.razorpay_payment_id}</code>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>{new Date(transaction.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <p>📭 No transactions yet</p>
            <Link to="/payment" className="btn btn-primary">Make Your First Payment</Link>
          </div>
        )}

        <div style={{ marginTop: '30px', textAlign: 'center' }}>
          <Link to="/dashboard" className="btn btn-outline">← Back to Dashboard</Link>
        </div>
      </div>
    </section>
  );
};

export default TransactionHistory;
