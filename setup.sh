#!/bin/bash

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating database migrations..."
cd freshtrack_project
python ../manage.py makemigrations

echo "Applying migrations..."
python ../manage.py migrate

echo "Creating superuser (admin)..."
python ../manage.py createsuperuser

echo "Setup complete! Run: python manage.py runserver"
