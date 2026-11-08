import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Landing = () => {
  const { user, config } = useAuth();
  const start = user ? '/dashboard' : '/signup';

  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <p className="eyebrow">Payment desk · Django + React</p>
            <h1>Take a payment, verify it, and keep the receipt.</h1>
            <p className="lede">
              PayGate is a small merchant app: accounts, checkout, signed payment confirmation,
              a searchable ledger, and refunds. Sandbox mode lets you walk the whole flow
              without a live Razorpay account.
            </p>
            <div className="hero-actions">
              <Link to={start} className="btn btn-primary btn-lg">
                {user ? 'Open dashboard' : 'Create an account'}
              </Link>
              <Link to={user ? '/transactions' : '/login'} className="btn btn-outline btn-lg">
                {user ? 'View history' : 'Try the demo'}
              </Link>
            </div>
          </div>
          <div className="ledger-preview" aria-hidden="true">
            <div className="ledger-top">
              <span>Today</span>
              <strong>₹3,798.00</strong>
            </div>
            <ul>
              <li><span>Brand identity retainer</span><em>Paid</em></li>
              <li><span>Workshop seat</span><em>Paid</em></li>
              <li><span>Domain renewal</span><em className="muted">Refunded</em></li>
              <li><span>Print run deposit</span><em className="wait">Pending</em></li>
            </ul>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-head">
            <h2>What a reviewer can click through</h2>
            <p>Three screens, one payment lifecycle.</p>
          </div>
          <div className="steps">
            <article>
              <span>01</span>
              <h3>Open a checkout</h3>
              <p>Enter an amount and what it is for. PayGate creates an order that belongs only to that merchant.</p>
            </article>
            <article>
              <span>02</span>
              <h3>Confirm the result</h3>
              <p>Sandbox records paid, declined, or cancelled. With Razorpay keys, the same screen opens the real test checkout and checks the signature.</p>
            </article>
            <article>
              <span>03</span>
              <h3>Read the ledger</h3>
              <p>Filter history, export a CSV, open a receipt, and refund a successful payment. Every change is written to an audit log.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="section section-alt" id="how">
        <div className="container feature-grid">
          <article className="feature">
            <h3>Signed, not trusted</h3>
            <p>A payment is marked paid only after the HMAC signature matches. A bad signature fails the order instead of accepting it.</p>
          </article>
          <article className="feature">
            <h3>Your rows only</h3>
            <p>History, receipts, and refunds are scoped to the logged-in user. Another account cannot complete or read your order.</p>
          </article>
          <article className="feature">
            <h3>Sandbox or Razorpay</h3>
            <p>
              {config?.charge_mode === 'live'
                ? 'Live Razorpay keys are set. A successful checkout charges a real card.'
                : config?.charge_mode === 'test'
                  ? 'Razorpay test keys are set. The checkout is real, and the card is not charged. Swap in live keys when you want real money to move.'
                  : 'No keys yet, so checkout is simulated. Add your Razorpay key id and secret to the server env and this same screen opens Razorpay.'}
            </p>
          </article>
          <article className="feature">
            <h3>A record you can audit</h3>
            <p>Orders, failures, signature checks, webhooks, and refunds land in a payment log an admin can inspect.</p>
          </article>
        </div>
      </section>
    </>
  );
};

export default Landing;
