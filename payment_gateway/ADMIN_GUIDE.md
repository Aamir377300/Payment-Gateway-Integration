# Django Admin Panel Guide

## Accessing the Admin Panel

### Local Development
1. Navigate to: `http://localhost:8000/admin/`
2. Login with your superuser credentials

### Production (Render)
1. Navigate to: `https://payment-gateway-integration-371z.onrender.com/admin/`
2. Login with your superuser credentials

## Creating a Superuser

If you haven't created a superuser yet:

```bash
# Local
cd payment_gateway
python manage.py createsuperuser

# On Render (via SSH or console)
python manage.py createsuperuser
```

Follow the prompts to set:
- Username
- Email
- Password

## Admin Features

### 1. User Management (Accounts)
- View all registered users
- Filter by staff status, active status, join date
- Search by username, email, name
- Edit user permissions and groups
- View user login history

### 2. Transaction Management (Payments)
- **List View Features:**
  - Color-coded status badges (Pending, Success, Failed, Refunded)
  - Search by order ID, Razorpay IDs, user email
  - Filter by status, currency, date
  - Bulk actions to update transaction status
  
- **Detail View Features:**
  - Complete transaction information
  - Razorpay payment details
  - User information
  - Timestamps (created/updated)

- **Bulk Actions:**
  - Mark selected as SUCCESS
  - Mark selected as FAILED
  - Mark selected as REFUNDED

### 3. Payment Logs
- **List View Features:**
  - Color-coded event type badges
  - Quick links to related transactions
  - IP address tracking
  - Search by message, order ID, IP
  
- **Detail View Features:**
  - Event type and message
  - Related transaction link
  - JSON payload (collapsible)
  - IP address
  - Timestamp

## Common Admin Tasks

### View Recent Transactions
1. Go to Payments → Transactions
2. Use date hierarchy at top to filter by date
3. Click on any transaction to view details

### Search for a Specific Payment
1. Go to Payments → Transactions
2. Use search box to enter:
   - Order ID
   - Razorpay Order/Payment ID
   - User email

### Update Transaction Status
1. Go to Payments → Transactions
2. Select transactions using checkboxes
3. Choose action from dropdown (Mark as SUCCESS/FAILED/REFUNDED)
4. Click "Go"

### View Payment Logs for Debugging
1. Go to Payments → Payment logs
2. Filter by event type
3. Click on log entry to view full payload

### Export Data
1. Select items you want to export
2. Use Django admin's built-in export features
3. Or use database queries directly

## Security Notes

- Only superusers can access the admin panel
- All actions are logged
- Use strong passwords for admin accounts
- Consider enabling 2FA for production
- Regularly review user permissions

## Database Connection

The admin panel connects to your PostgreSQL database configured in:
- Local: `.env` file settings
- Production: Render PostgreSQL database via `DATABASE_URL`

All data displayed is real-time from your PostgreSQL database.
