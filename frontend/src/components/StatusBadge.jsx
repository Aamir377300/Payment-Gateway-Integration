const LABELS = {
  SUCCESS: 'Paid',
  FAILED: 'Failed',
  PENDING: 'Pending',
  REFUNDED: 'Refunded',
};

const StatusBadge = ({ status }) => {
  const key = (status || 'pending').toLowerCase();
  return <span className={`badge badge-${key}`}>{LABELS[status] || status}</span>;
};

export default StatusBadge;
