# PayGate

A small merchant payment desk. Create an account, open a checkout, confirm the payment with a signature check, then search the ledger, export it, open a receipt, or refund it.

Sandbox mode is the default when Razorpay keys are missing, so the whole flow can be demoed locally. Add test keys and the same screens talk to Razorpay.

## Stack

- Django and Django REST Framework, session auth, SQLite by default or PostgreSQL when configured
- React and Vite
- Razorpay, used only when `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are set
- pytest

## Run it locally

From `payment_gateway`:

```bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

From `frontend`:

```bash
npm install
npm run dev
```

Open `http://localhost:5173`.

The demo merchant is created on migrate while the app is in sandbox or `DEBUG=True`:

- Email: `demo@paygate.dev`
- Password: `DemoPass123`

You can recreate that account any time with `python manage.py seed_demo`.

No `.env` file is required for the sandbox. Copy `.env.example` when you want Postgres, a custom secret, or Razorpay.

## Take a real payment

Leave the code as it is. In `payment_gateway/.env`, set the two Razorpay values and restart the server:

```env
RAZORPAY_KEY_ID=rzp_test_your_key
RAZORPAY_KEY_SECRET=your_secret
```

`rzp_test_` opens the real Razorpay checkout and accepts their test card `4111 1111 1111 1111`. Nothing is charged. Replace those with your `rzp_live_` key id and live secret when a card should actually be charged. The same Pay button, signature check, receipt, and refund are used either way.

If the Razorpay webhook secret is different from the key secret, also set `RAZORPAY_WEBHOOK_SECRET`. Point the webhook at `https://<your-backend>/api/payments/webhook/`.

## Payment modes

| `PAYMENT_MODE` | Behavior |
| --- | --- |
| `auto` (default) | Razorpay if both keys exist, otherwise sandbox |
| `sandbox` | Always simulate checkout on this server |
| `razorpay` | Require Razorpay keys and open their checkout |

In sandbox, checkout asks you to mark the payment paid, declined, or cancelled. The server still builds an HMAC signature and runs it through the same verification function used for Razorpay. A bad signature fails the payment.

With Razorpay keys, checkout loads Razorpay and accepts the payment only when `order_id|payment_id` matches the returned signature.

## What the app covers

- Signup, login, and logout, with Django's password validators
- Orders scoped to the logged-in user
- Dashboard totals calculated on the server
- Search, status filter, and pagination
- CSV export of the current filter
- Receipt with an activity log
- Refund of a successful payment (immediate in sandbox, Razorpay refund API when live)
- Webhook endpoint that ignores a body unless `X-Razorpay-Signature` matches
- Django admin for users, transactions, and payment logs

## API

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/api/health/` | No |
| GET | `/api/config/` | No |
| GET | `/api/csrf/` | No |
| POST | `/api/auth/signup/` | No |
| POST | `/api/auth/login/` | No |
| POST | `/api/auth/logout/` | Yes |
| GET | `/api/auth/user/` | Yes |
| POST | `/api/payments/create-order/` | Yes |
| POST | `/api/payments/verify/` | Yes |
| POST | `/api/payments/failure/` | Yes |
| POST | `/api/payments/sandbox/complete/` | Yes |
| GET | `/api/payments/summary/` | Yes |
| GET | `/api/payments/transactions/` | Yes |
| GET | `/api/payments/transactions/export/` | Yes |
| GET | `/api/payments/transactions/<id>/` | Yes |
| POST | `/api/payments/transactions/<id>/refund/` | Yes |
| POST | `/api/payments/webhook/` | Signed body |

`GET /api/payments/transactions/` accepts `status`, `q`, and `page`.

## Tests

```bash
cd payment_gateway
source myenv/bin/activate
pytest -v
```

The suite uses SQLite even if a `.env` points at Postgres. It covers auth validation, sandbox checkout, bad signatures, ownership, refunds, filters, CSV export, webhooks, and the Razorpay order call with the client mocked.

## Deploy notes

Backend: set `DATABASE_URL`, `SECRET_KEY`, `DEBUG=False`, `FRONTEND_URI`, and the Razorpay keys. Build with `./build.sh`. Start with `python manage.py migrate && gunicorn payment_gateway.wsgi:application`.

Frontend: set the Vite root to `frontend` and `VITE_API_URL` to `https://<backend>/api`.

Set `SEED_DEMO=0` in production if you do not want the demo merchant created on migrate.

## Author

Aamir Belal Khan
