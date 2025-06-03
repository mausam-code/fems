#!/bin/bash

# FEMS Deployment Script
# This script automates the deployment process for the FEMS Django application

set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting deployment process..."

# 1. Activate virtual environment (adjust path as needed)
echo "Activating virtual environment..."
source /path/to/venv/bin/activate

# 2. Navigate to project directory
echo "Navigating to project directory..."
cd /path/to/fems_project

# 3. Pull latest changes from repository
echo "Pulling latest changes from repository..."
git pull

# 4. Install or update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements_prod.txt

# 5. Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=fems.settings_prod

# 6. Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --settings=fems.settings_prod

# 7. Restart Gunicorn (adjust service name if different)
echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

# 8. Reload Nginx
echo "Reloading Nginx..."
sudo systemctl reload nginx

echo "Deployment completed successfully!"