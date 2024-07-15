echo "Applying database migrations"
python manage.py makemigrations
python manage.py migrate --no-input

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --no-input

# Start Django development server
echo "Starting Django development server"
python manage.py runserver 0.0.0.0:8000
