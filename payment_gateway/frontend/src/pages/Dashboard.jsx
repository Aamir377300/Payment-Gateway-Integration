import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    total: 0,
    successful: 0,
    successAmount: 0,
    pending: 0,
    failed: 0
  });
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/payments/transactions/');
      const transactions = response.data;
      
      const total = transactions.length;
      const successful = transactions.filter(t => t.status === 'SUCCESS').length;
      const pending = transactions.filter(t => t.status === 'PENDING').length;
      const failed = transactions.filter(t => t.status === 'FAILED').length;
      const successAmount = transactions
        .filter(t => t.status === 'SUCCESS')
        .reduce((sum, t) => sum + parseFloat(t.amount), 0);
      
      setStats({
        total,
        successful,
        successAmount,
        pending,
        failed
      });
      
      setRecentTransactions(transactions.slice(0, 5));
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

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

  return (
    <section className="dashboard-section">
      <div className="container">
        <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Welcome, {user?.first_name || user?.username}!</h1>
            <p>Manage your payments and transactions</p>
          </div>
          <Link to="/payment" className="btn btn-primary btn-lg">
            💳 Make a Payment
          </Link>
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <path d="M16 8L22 14L16 20L10 14L16 8Z" fill="white" />
              </svg>
            </div>
            <h3>Total Transactions</h3>
            <p className="card-value">{loading ? '...' : stats.total}</p>
            <p className="card-label">
              {stats.total === 0 ? 'No transactions yet' : `${stats.successful} successful, ${stats.failed} failed`}
            </p>
          </div>

          <div className="dashboard-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <path d="M10 16L14 20L22 12" stroke="white" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>
            <h3>Successful Payments</h3>
            <p className="card-value">
              {loading ? '...' : `₹${stats.successAmount.toFixed(2)}`}
            </p>
            <p className="card-label">
              {stats.successful === 0 ? 'No successful payments' : `${stats.successful} successful transactions`}
            </p>
          </div>

          <div className="dashboard-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="6" stroke="white" strokeWidth="2" />
              </svg>
            </div>
            <h3>Pending</h3>
            <p className="card-value">{loading ? '...' : stats.pending}</p>
            <p className="card-label">
              {stats.pending === 0 ? 'No pending payments' : 'Awaiting confirmation'}
            </p>
          </div>
        </div>

        <div className="content-card">
          <h2>Recent Transactions</h2>
          {loading ? (
            <div className="empty-state">
              <p>Loading...</p>
            </div>
          ) : recentTransactions.length > 0 ? (
            <>
              <div style={{ overflowX: 'auto' }}>
                <table className="transaction-table">
                  <thead>
                    <tr>
                      <th>Order ID</th>
                      <th>Amount</th>
                      <th>Description</th>
                      <th>Status</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentTransactions.map((transaction) => (
                      <tr key={transaction.id}>
                        <td>{transaction.order_id}</td>
                        <td>₹{transaction.amount}</td>
                        <td>{transaction.description || 'N/A'}</td>
                        <td>{getStatusBadge(transaction.status)}</td>
                        <td>{new Date(transaction.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div style={{ marginTop: '20px', textAlign: 'center', display: 'flex', gap: '10px', justifyContent: 'center' }}>
                <Link to="/transactions" className="btn btn-outline">View All Transactions</Link>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <circle cx="32" cy="32" r="30" stroke="#e5e7eb" strokeWidth="2" />
                <path d="M32 20V32L40 40" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <p>No transactions yet</p>
              <Link to="/payment" className="btn btn-primary">Make a Payment</Link>
              <Link to="/transactions" className="btn btn-outline" style={{ marginLeft: '10px' }}>View History</Link>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Dashboard;
