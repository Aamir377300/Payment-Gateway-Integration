import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import StatusBadge from '../components/StatusBadge';
import { formatDate, formatINR } from '../utils/format';

const STATUSES = [
  { value: '', label: 'All statuses' },
  { value: 'SUCCESS', label: 'Paid' },
  { value: 'PENDING', label: 'Pending' },
  { value: 'FAILED', label: 'Failed' },
  { value: 'REFUNDED', label: 'Refunded' },
];

const TransactionHistory = () => {
  const [status, setStatus] = useState('');
  const [query, setQuery] = useState('');
  const [appliedQuery, setAppliedQuery] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let ignore = false;
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await api.get('/payments/transactions/', {
          params: { status, q: appliedQuery, page },
        });
        if (!ignore) setData(response.data);
      } catch {
        if (!ignore) setError('Could not load payments.');
      } finally {
        if (!ignore) setLoading(false);
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, [status, appliedQuery, page]);

  const exportCsv = async () => {
    const response = await api.get('/payments/transactions/export/', {
      params: { status, q: appliedQuery },
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'paygate-transactions.csv';
    link.click();
    window.URL.revokeObjectURL(url);
  };

  const results = data?.results || [];

  return (
    <section className="page">
      <div className="container">
        <div className="page-header">
          <div>
            <p className="eyebrow">Ledger</p>
            <h1>Payment history</h1>
          </div>
          <button type="button" className="btn btn-outline" onClick={exportCsv}>Export CSV</button>
        </div>

        <form
          className="toolbar"
          onSubmit={(event) => {
            event.preventDefault();
            setPage(1);
            setAppliedQuery(query.trim());
          }}
        >
          <input
            className="form-control"
            placeholder="Search description, order, or payment id"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <select
            className="form-control"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              setPage(1);
            }}
          >
            {STATUSES.map((item) => (
              <option key={item.value} value={item.value}>{item.label}</option>
            ))}
          </select>
          <button type="submit" className="btn btn-primary">Search</button>
        </form>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="panel">
          {loading ? (
            <p className="empty">Loading payments…</p>
          ) : results.length === 0 ? (
            <div className="empty">
              <p>No payments match this view.</p>
              <Link to="/payment" className="btn btn-primary">New payment</Link>
            </div>
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Payment id</th>
                    <th>When</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((transaction) => (
                    <tr key={transaction.id}>
                      <td>
                        <Link to={`/transactions/${transaction.id}`}>{transaction.description || 'Payment'}</Link>
                        <small>{transaction.order_id}</small>
                      </td>
                      <td>{formatINR(transaction.amount)}</td>
                      <td><StatusBadge status={transaction.status} /></td>
                      <td><code>{transaction.razorpay_payment_id || '—'}</code></td>
                      <td>{formatDate(transaction.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {data && data.num_pages > 1 && (
            <div className="pager">
              <button type="button" className="btn btn-ghost" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                Previous
              </button>
              <span>Page {data.page} of {data.num_pages}</span>
              <button type="button" className="btn btn-ghost" disabled={page >= data.num_pages} onClick={() => setPage(page + 1)}>
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default TransactionHistory;
