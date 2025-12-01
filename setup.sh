#!/bin/bash

echo "🚀 Setting up Payment Gateway..."
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Navigate to project directory
cd payment_gateway

# Run migrations
echo "📦 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your Razorpay keys to payment_gateway/.env"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Run server: python manage.py runserver"
echo ""
echo "📖 Read SETUP_GUIDE.md for detailed instructions"
