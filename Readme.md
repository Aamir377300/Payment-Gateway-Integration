# PayGate - Payment Gateway Integration

A full-stack payment gateway application built with Django REST Framework and React, integrated with Razorpay for secure payment processing.

## Screenshot's
<div style="display: flex; justify-content: center; gap: 12px;">
  <img src="photos/Dashboard.png" alt="Dashboard" width="460">
  <img src="photos/checkout.png" alt="Checkout" width="460">
</div>



## Live Demo

- **Frontend:** https://payment-gateway-integration-zeta.vercel.app
- **Backend API:** https://payment-gateway-integration-371z.onrender.com
- **Admin Panel:** https://payment-gateway-integration-371z.onrender.com/admin

## Features

- User authentication (signup, login, logout)
- Secure payment processing with Razorpay
- Transaction history and tracking
- Real-time payment status updates
- Admin dashboard for managing users and transactions
- Payment logs for audit trails
- Responsive design for all devices

## Tech Stack

### Backend

- Django 6.0
- Django REST Framework
- PostgreSQL (Render)
- Razorpay Payment Gateway
- Gunicorn + Whitenoise

### Frontend

- React 18
- Vite
- Axios
- React Router
- CSS3

## API Endpoints

### Authentication Endpoints

| Method | Endpoint              | Description                               | Auth Required |
| ------ | --------------------- | ----------------------------------------- | ------------- |
| GET    | `/api/csrf/`        | Initialize CSRF token for secure requests | No            |
| POST   | `/api/auth/signup/` | Register a new user account               | No            |
| POST   | `/api/auth/login/`  | Authenticate user and create session      | No            |
| POST   | `/api/auth/logout/` | End user session                          | Yes           |
| GET    | `/api/auth/user/`   | Get current authenticated user details    | Yes           |

### Payment Endpoints

| Method | Endpoint                             | Description                           | Auth Required |
| ------ | ------------------------------------ | ------------------------------------- | ------------- |
| POST   | `/api/payments/create-order/`      | Create a new Razorpay payment order   | Yes           |
| POST   | `/api/payments/verify/`            | Verify Razorpay payment signature     | Yes           |
| POST   | `/api/payments/failure/`           | Mark a pending payment as failed      | Yes           |
| GET    | `/api/payments/transactions/`      | Get all transactions for current user | Yes           |
| GET    | `/api/payments/transactions/{id}/` | Get specific transaction details      | Yes           |

## Local Development Setup

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL
- Razorpay Account (Test Mode)

### Backend Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd payment_gateway
```

2. Create virtual environment:

```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file:

```env
DB_NAME=payment_gateway_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=your-secret-key-here
DEBUG=True

RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret

FRONTEND_URI=http://localhost:5173
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create superuser:

```bash
python manage.py createsuperuser
```

7. Run development server:

```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
```

4. Run development server:

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Production Deployment

### Backend (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `./build.sh`
4. Set start command: `python manage.py migrate && gunicorn payment_gateway.wsgi:application`
5. Add environment variables:
   - `DEBUG=False`
   - `SECRET_KEY=<your-secret-key>`
   - `DATABASE_URL=<auto-set-by-render>`
   - `FRONTEND_URI=https://your-frontend.vercel.app`
   - `RAZORPAY_KEY_ID=<your-key>`
   - `RAZORPAY_KEY_SECRET=<your-secret>`
   - `ADMIN_USERNAME=admin` (optional)
   - `ADMIN_EMAIL=admin@example.com` (optional)
   - `ADMIN_PASSWORD=secure_password` (optional)

### Frontend (Vercel)

1. Import your GitHub repository to Vercel
2. Set framework preset: Vite
3. Set root directory: `frontend`
4. Add environment variable:
   - `VITE_API_URL=https://your-backend.onrender.com/api`
5. Deploy

## Security Features

- CSRF protection for all state-changing requests
- Session-based authentication with secure cookies
- CORS configuration for cross-origin requests
- Password hashing with Django's built-in system
- Razorpay signature verification for payment security
- HTTPS enforcement in production

## Database Schema

### User (Django Built-in)

- id, username, email, password, first_name, last_name

### Transaction

- id, user (FK), order_id, amount, currency, status
- razorpay_order_id, razorpay_payment_id, razorpay_signature
- description, receipt, created_at, updated_at

### PaymentLog

- id, transaction (FK), event_type, payload (JSON)
- message, ip_address, created_at

## Frontend Routes

- `/` - Home page
- `/login` - User login
- `/signup` - User registration
- `/dashboard` - User dashboard (protected)
- `/payment` - Payment form (protected)
- `/transactions` - Transaction history (protected)
- `/checkout` - Razorpay checkout (protected)
- `/payment-success/:id` - Payment success page
- `/payment-failure/:id` - Payment failure page

## 🔧 Configuration Notes

### Cookie Settings

- **Development (HTTP):** `SameSite=Lax`, `Secure=False`
- **Production (HTTPS):** `SameSite=None`, `Secure=True`

## Admin Panel

Access the Django admin panel at `/admin` to:

- View and manage users
- Monitor all transactions
- Review payment logs
- Filter transactions by status
- Search by order ID or payment ID

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Author

**Aamir Belal Khan**

---

Built with ❤️ using Django and React