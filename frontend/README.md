# PayGate React Frontend

This is the React frontend for the PayGate payment gateway application, built with Vite.

## Development Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will run on `http://localhost:5173`

## Production Build

Build the production-ready files:
```bash
npm run build
```

The built files will be in the `dist` directory, which Django will serve in production.

## Features

- User authentication (Login/Signup)
- Dashboard with transaction overview
- Payment processing with Razorpay
- Transaction history
- Responsive design matching the original Django templates

## Tech Stack

- React 18
- React Router DOM
- Axios for API calls
- Vite for build tooling
- CSS (matching original Django template styles)
