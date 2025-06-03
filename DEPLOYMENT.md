# FEMS Production Deployment Guide

This guide provides instructions for deploying the Foreign Employment Management System (FEMS) Django application in a production environment using Gunicorn and Nginx.

## Prerequisites

- A Linux server (Ubuntu 20.04 LTS or later recommended)
- Python 3.8 or higher
- PostgreSQL database
- Nginx web server
- Domain name (optional, but recommended for production)
- SSL certificate (Let's Encrypt recommended)

## Step 1: Server Preparation

### Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required Packages

```bash
sudo apt install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
sudo apt install -y build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install -y python3-venv git
```

## Step 2: Database Setup

### Create PostgreSQL Database and User

```bash
sudo -u postgres psql
```

In the PostgreSQL shell:

```sql
CREATE DATABASE fems_db;
CREATE USER fems_user WITH PASSWORD 'your-secure-password';
ALTER ROLE fems_user SET client_encoding TO 'utf8';
ALTER ROLE fems_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE fems_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE fems_db TO fems_user;
\q
```

## Step 3: Application Setup

### Clone the Repository

```bash
mkdir -p /var/www/fems
cd /var/www/fems
git clone https://your-repository-url.git .
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements_prod.txt
```

### Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
nano .env
```

Update the values in the `.env` file with your actual settings.

### Collect Static Files

```bash
python manage.py collectstatic --noinput --settings=fems.settings_prod
```

### Apply Migrations

```bash
python manage.py migrate --settings=fems.settings_prod
```

### Create Superuser

```bash
python manage.py createsuperuser --settings=fems.settings_prod
```

## Step 4: Gunicorn Setup

### Test Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 fems.wsgi:application --env DJANGO_SETTINGS_MODULE=fems.settings_prod
```

Press CTRL+C to stop after testing.

### Create Systemd Service

Copy the Gunicorn service file to the systemd directory:

```bash
sudo cp gunicorn.service /etc/systemd/system/
```

Edit the service file to update paths:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Update the `WorkingDirectory` and `ExecStart` paths to match your actual installation.

### Enable and Start Gunicorn Service

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## Step 5: Nginx Setup

### Configure Nginx

Copy the Nginx configuration file:

```bash
sudo cp nginx/fems_nginx.conf /etc/nginx/sites-available/fems
```

Edit the configuration file:

```bash
sudo nano /etc/nginx/sites-available/fems
```

Update the `server_name`, paths to static/media files, and SSL certificate paths.

### Enable the Site

```bash
sudo ln -s /etc/nginx/sites-available/fems /etc/nginx/sites-enabled/
sudo nginx -t  # Test the configuration
sudo systemctl restart nginx
```

## Step 6: SSL Certificate (Let's Encrypt)

### Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts to complete the certificate installation.

## Step 7: Firewall Configuration

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
sudo ufw status
```

## Step 8: Maintenance and Updates

### Automated Deployment

Use the provided deployment script for updates:

```bash
chmod +x deploy.sh
./deploy.sh
```

### Backup Strategy

1. **Database Backups**: Set up regular PostgreSQL dumps
   ```bash
pg_dump -U fems_user fems_db > fems_backup_$(date +%Y%m%d).sql
   ```

2. **Media Files Backup**: Regularly backup the media directory
   ```bash
rsync -av /var/www/fems/mediafiles/ /path/to/backup/media/
   ```

## Troubleshooting

### Check Logs

- Gunicorn logs: `/var/log/gunicorn/`
- Nginx access logs: `/var/log/nginx/fems_access.log`
- Nginx error logs: `/var/log/nginx/fems_error.log`
- Django logs: `/var/www/fems/logs/django-error.log`

### Common Issues

1. **502 Bad Gateway**: Check if Gunicorn is running
   ```bash
sudo systemctl status gunicorn
   ```

2. **Static files not loading**: Check Nginx configuration and file permissions
   ```bash
sudo nginx -t
sudo chown -R www-data:www-data /var/www/fems/staticfiles/
   ```

3. **Database connection issues**: Verify PostgreSQL is running and credentials are correct
   ```bash
sudo systemctl status postgresql
   ```

## Security Considerations

1. Regularly update all packages: `sudo apt update && sudo apt upgrade -y`
2. Set up automatic security updates: `sudo apt install unattended-upgrades`
3. Configure a firewall (UFW) as shown above
4. Use strong passwords for all services
5. Implement rate limiting in Nginx for sensitive endpoints
6. Regularly review logs for suspicious activity
7. Consider using a Web Application Firewall (WAF)

## Performance Optimization

1. Adjust Gunicorn worker count based on server resources
2. Enable Nginx caching for static assets
3. Consider using a CDN for static files
4. Optimize database queries and add indexes
5. Implement database connection pooling

## Monitoring

Consider setting up monitoring with tools like:

1. Prometheus and Grafana for metrics
2. Sentry for error tracking
3. Uptime Robot or similar for availability monitoring

---

For additional help or questions, please contact the development team.