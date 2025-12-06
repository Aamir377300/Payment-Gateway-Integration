
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Create admin user for render
python manage.py create_admin