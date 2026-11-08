import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import StatusBadge from '../components/StatusBadge';
import { formatDate, formatINR } from '../utils/format';

const Dashboard = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let ignore = false;
    const load = async () => {
      try {
        const [summaryResponse, historyResponse] = await Promise.all([
          api.get('/payments/summary/'),
          api.get('/payments/transactions/'),
        ]);
        if (ignore) return;
        setSummary(summaryResponse.data);
        setRecent(historyResponse.data.results.slice(0, 5));
      } catch {
        if (!ignore) setError('Could not load the dashboard.');
      } finally {
        if (!ignore) setLoading(false);
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, []);

  return (
    <section className="page">
      <div className="container">
        <div className="page-header">
          <div>
            <p className="eyebrow">Merchant desk</p>
            <h1>Hello, {user?.first_name || 'there'}</h1>
            <p className="lede">Collected payments, open checkouts, and the latest activity on your account.</p>
          </div>
          <Link to="/payment" className="btn btn-primary">New payment</Link>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="stat-grid">
          <article className="stat-card">
            <p>Collected</p>
            <strong>{loading ? '—' : formatINR(summary?.collected_amount)}</strong>
            <span>{summary?.successful_count || 0} paid</span>
          </article>
          <article className="stat-card">
            <p>Pending</p>
            <strong>{loading ? '—' : summary?.pending_count || 0}</strong>
            <span>Waiting on checkout</span>
          </article>
          <article className="stat-card">
            <p>Failed</p>
            <strong>{loading ? '—' : summary?.failed_count || 0}</strong>
            <span>Declined or cancelled</span>
          </article>
          <article className="stat-card">
            <p>Refunded</p>
            <strong>{loading ? '—' : formatINR(summary?.refunded_amount)}</strong>
            <span>{summary?.refunded_count || 0} returned</span>
          </article>
        </div>

        <div className="panel">
          <div className="panel-head">
            <h2>Recent payments</h2>
            <Link to="/transactions">View history</Link>
          </div>
          {loading ? (
            <p className="empty">Loading payments…</p>
          ) : recent.length === 0 ? (
            <div className="empty">
              <p>No payments yet.</p>
              <Link to="/payment" className="btn btn-primary">Take the first payment</Link>
            </div>
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>When</th>
                  </tr>
                </thead>
                <tbody>
                  {recent.map((transaction) => (
                    <tr key={transaction.id}>
                      <td>
                        <Link to={`/transactions/${transaction.id}`}>{transaction.description}</Link>
                        <small>{transaction.order_id}</small>
                      </td>
                      <td>{formatINR(transaction.amount)}</td>
                      <td><StatusBadge status={transaction.status} /></td>
                      <td>{formatDate(transaction.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Dashboard;
