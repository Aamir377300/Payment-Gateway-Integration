#!/bin/bash

echo "Setting up Payment Gateway..."

pip install -r payment_gateway/requirements.txt

cd payment_gateway

python manage.py makemigrations
python manage.py migrate

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "1. Add Razorpay keys to payment_gateway/.env"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Run server: python manage.py runserver"
