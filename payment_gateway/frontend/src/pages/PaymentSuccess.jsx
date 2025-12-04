import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/axios';

const PaymentSuccess = () => {
  const { transactionId } = useParams();
  const [transaction, setTransaction] = useState(null);

  useEffect(() => {
    const fetchTransaction = async () => {
      try {
        const response = await api.get(`/payments/transactions/${transactionId}/`);
        setTransaction(response.data);
      } catch (error) {
        // Handle error silently
      }
    };
    fetchTransaction();
  }, [transactionId]);

  if (!transaction) return <div>Loading...</div>;

  return (
    <section className="auth-section">
      <div className="container" style={{ maxWidth: '600px', textAlign: 'center' }}>
        <div className="auth-card">
          <div style={{ fontSize: '80px', marginBottom: '20px' }}>✅</div>
          <h1>Payment Successful!</h1>
          <p>Your payment has been processed successfully.</p>

          <div style={{ margin: '30px 0', background: '#f8f9fa', padding: '20px', borderRadius: '8px', textAlign: 'left' }}>
            <h3 style={{ marginBottom: '15px' }}>Transaction Details</h3>
            <table style={{ width: '100%' }}>
              <tbody>
                <tr>
                  <td style={{ padding: '8px', color: '#666' }}>Order ID:</td>
                  <td style={{ padding: '8px' }}><strong>{transaction.order_id}</strong></td>
                </tr>
                <tr>
                  <td style={{ padding: '8px', color: '#666' }}>Amount:</td>
                  <td style={{ padding: '8px' }}><strong>₹{transaction.amount}</strong></td>
                </tr>
                <tr>
                  <td style={{ padding: '8px', color: '#666' }}>Payment ID:</td>
                  <td style={{ padding: '8px' }}><strong>{transaction.razorpay_payment_id}</strong></td>
                </tr>
                <tr>
                  <td style={{ padding: '8px', color: '#666' }}>Status:</td>
                  <td style={{ padding: '8px' }}>
                    <span style={{ background: '#28a745', color: 'white', padding: '5px 10px', borderRadius: '4px', fontSize: '12px' }}>
                      {transaction.status}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td style={{ padding: '8px', color: '#666' }}>Date:</td>
                  <td style={{ padding: '8px' }}>{new Date(transaction.created_at).toLocaleString()}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: '30px' }}>
            <Link to="/transactions" className="btn btn-primary">View All Transactions</Link>
            <Link to="/dashboard" className="btn btn-outline" style={{ marginLeft: '10px' }}>Back to Dashboard</Link>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PaymentSuccess;
