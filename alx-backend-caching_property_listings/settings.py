#!/bin/bash

# Create the Django project with correct naming
echo "Creating Django project with underscores..."
django-admin startproject alx_backend_caching_property_listings .

# Create the properties app
echo "Creating properties app..."
python manage.py startapp properties

# Create necessary directories
mkdir -p logs
mkdir -p static
mkdir -p media
mkdir -p templates

# Install required packages
echo "Installing required packages..."
pip install django django-redis psycopg2-binary redis python-dotenv hiredis

# Create and run migrations
echo "Creating migrations..."
python manage.py makemigrations properties

echo "Running migrations..."
python manage.py migrate

# Create superuser (optional - will prompt for input)
echo "Creating superuser..."
python manage.py createsuperuser

echo "Setup complete!"
echo ""
echo "Project structure:"
echo "alx_backend_caching_property_listings/"
echo "├── alx_backend_caching_property_listings/"
echo "│   ├── __init__.py"
echo "│   ├── settings.py"
echo "│   ├── urls.py"
echo "│   └── wsgi.py"
echo "├── properties/"
echo "│   ├── __init__.py"
echo "│   ├── admin.py"
echo "│   ├── apps.py"
echo "│   ├── models.py"
echo "│   ├── migrations/"
echo "│   ├── tests.py"
echo "│   └── views.py"
echo "├── docker-compose.yml"
echo "├── Dockerfile"
echo "├── requirements.txt"
echo "├── manage.py"
echo "└── logs/"
echo ""
echo "To start the application:"
echo "1. Start services: docker-compose up -d"
echo "2. Run migrations: docker-compose exec web python manage.py migrate"
echo "3. Access at: http://localhost:8000"
