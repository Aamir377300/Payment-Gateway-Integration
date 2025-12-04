import { Link } from 'react-router-dom';

const Landing = () => {
  return (
    <>
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1 className="hero-title">
                Accept Payments
                <span className="gradient-text">Securely & Easily</span>
              </h1>
              <p className="hero-description">
                A simple payment gateway built with Django and Razorpay. Get started in minutes and start accepting payments from your customers.
              </p>
              <div className="hero-buttons">
                <Link to="/signup" className="btn btn-primary btn-lg">Get Started Free</Link>
                <a href="#features" className="btn btn-outline btn-lg">Learn More</a>
              </div>
              <div className="hero-stats">
                <div className="stat">
                  <span className="stat-number">99.9%</span>
                  <span className="stat-label">Uptime</span>
                </div>
                <div className="stat">
                  <span className="stat-number">100%</span>
                  <span className="stat-label">Secure</span>
                </div>
                <div className="stat">
                  <span className="stat-number">24/7</span>
                  <span className="stat-label">Support</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="features">
        <div className="container">
          <div className="section-header">
            <h2>Why use PayGate?</h2>
            <p>Simple tools to help you accept payments</p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                  <rect width="40" height="40" rx="10" fill="#667eea" opacity="0.1" />
                  <path d="M20 12L26 18L20 24L14 18L20 12Z" stroke="#667eea" strokeWidth="2" />
                </svg>
              </div>
              <h3>Secure Transactions</h3>
              <p>Your payments are protected with encryption and webhook verification to keep everything safe</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                  <rect width="40" height="40" rx="10" fill="#f093fb" opacity="0.1" />
                  <circle cx="20" cy="20" r="6" stroke="#f093fb" strokeWidth="2" />
                </svg>
              </div>
              <h3>Real-time Updates</h3>
              <p>Get instant notifications when payments come through so you're always in the loop</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                  <rect width="40" height="40" rx="10" fill="#4facfe" opacity="0.1" />
                  <rect x="14" y="14" width="12" height="12" stroke="#4facfe" strokeWidth="2" />
                </svg>
              </div>
              <h3>Transaction History</h3>
              <p>View all your past payments in one place with detailed records you can search through</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                  <rect width="40" height="40" rx="10" fill="#43e97b" opacity="0.1" />
                  <path d="M15 20L18 23L25 16" stroke="#43e97b" strokeWidth="2" />
                </svg>
              </div>
              <h3>Easy to Set Up</h3>
              <p>Get up and running quickly with straightforward setup and clear documentation</p>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to start?</h2>
            <p>Create your account and start accepting payments today</p>
            <Link to="/signup" className="btn btn-primary btn-lg">Get Started</Link>
          </div>
        </div>
      </section>
    </>
  );
};

export default Landing;
