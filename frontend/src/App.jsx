import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import PaymentForm from './pages/PaymentForm';
import Checkout from './pages/Checkout';
import PaymentSuccess from './pages/PaymentSuccess';
import PaymentFailure from './pages/PaymentFailure';
import TransactionHistory from './pages/TransactionHistory';
import TransactionDetail from './pages/TransactionDetail';

const LoadingScreen = () => <div className="loading-screen">Opening your desk…</div>;

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <LoadingScreen />;
  return user ? children : <Navigate to="/login" />;
};

const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <LoadingScreen />;
  return !user ? children : <Navigate to="/dashboard" />;
};

function ModeBanner() {
  const { config } = useAuth();
  const mode = config?.charge_mode;
  if (!mode || mode === 'misconfigured') return null;

  if (mode === 'live') {
    return (
      <div className="sandbox-banner live">
        Live Razorpay. A successful checkout charges a real card.
      </div>
    );
  }

  if (mode === 'test') {
    return (
      <div className="sandbox-banner">
        Razorpay test mode. Use card 4111 1111 1111 1111. Replace the keys with your live keys to charge a real card.
      </div>
    );
  }

  return (
    <div className="sandbox-banner">
      Practice mode. To take a real payment, add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in payment_gateway/.env and restart. No code changes.
    </div>
  );
}

function AppContent() {
  return (
    <Router>
      <Navbar />
      <ModeBanner />
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/signup" element={<PublicRoute><Signup /></PublicRoute>} />
          <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/payment" element={<PrivateRoute><PaymentForm /></PrivateRoute>} />
          <Route path="/checkout" element={<PrivateRoute><Checkout /></PrivateRoute>} />
          <Route path="/payment-success/:transactionId" element={<PrivateRoute><PaymentSuccess /></PrivateRoute>} />
          <Route path="/payment-failure/:transactionId" element={<PrivateRoute><PaymentFailure /></PrivateRoute>} />
          <Route path="/transactions" element={<PrivateRoute><TransactionHistory /></PrivateRoute>} />
          <Route path="/transactions/:transactionId" element={<PrivateRoute><TransactionDetail /></PrivateRoute>} />
        </Routes>
      </main>
      <Footer />
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
