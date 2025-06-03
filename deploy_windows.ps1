# FEMS Deployment Script for Windows
# This PowerShell script automates the deployment process for the FEMS Django application on Windows

# Stop on errors
$ErrorActionPreference = "Stop"

Write-Host "Starting deployment process..." -ForegroundColor Green

# 1. Activate virtual environment (adjust path as needed)
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
$venvPath = "C:\path\to\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
} else {
    Write-Host "Virtual environment not found at $venvPath" -ForegroundColor Red
    exit 1
}

# 2. Navigate to project directory
Write-Host "Navigating to project directory..." -ForegroundColor Cyan
$projectPath = "C:\path\to\fems_project"
Set-Location -Path $projectPath

# 3. Pull latest changes from repository (if using git)
Write-Host "Pulling latest changes from repository..." -ForegroundColor Cyan
git pull

# 4. Install or update dependencies
Write-Host "Installing/updating dependencies..." -ForegroundColor Cyan
pip install -r requirements_prod.txt

# 5. Collect static files
Write-Host "Collecting static files..." -ForegroundColor Cyan
python manage.py collectstatic --noinput --settings=fems.settings_prod

# 6. Apply database migrations
Write-Host "Applying database migrations..." -ForegroundColor Cyan
python manage.py migrate --settings=fems.settings_prod

# 7. Restart Gunicorn (using NSSM service manager for Windows)
Write-Host "Restarting Gunicorn service..." -ForegroundColor Cyan
Restart-Service -Name "GunicornFEMS" -ErrorAction SilentlyContinue
if ($?) {
    Write-Host "Gunicorn service restarted successfully" -ForegroundColor Green
} else {
    Write-Host "Starting Gunicorn manually..." -ForegroundColor Yellow
    # Start Gunicorn manually if service doesn't exist
    $gunicornPath = "C:\path\to\venv\Scripts\gunicorn.exe"
    $gunicornArgs = "-c gunicorn_config.py fems.wsgi:application"
    Start-Process -FilePath $gunicornPath -ArgumentList $gunicornArgs -NoNewWindow
}

# 8. Restart Nginx (if installed on Windows)
Write-Host "Restarting Nginx service..." -ForegroundColor Cyan
Restart-Service -Name "nginx" -ErrorAction SilentlyContinue
if ($?) {
    Write-Host "Nginx service restarted successfully" -ForegroundColor Green
} else {
    Write-Host "Nginx service not found or could not be restarted" -ForegroundColor Yellow
    Write-Host "You may need to restart Nginx manually" -ForegroundColor Yellow
}

Write-Host "Deployment completed successfully!" -ForegroundColor Green

# Notes for Windows deployment:
# 1. For production on Windows, consider using NSSM (Non-Sucking Service Manager) to run Gunicorn as a Windows service
# 2. Install Nginx for Windows from http://nginx.org/en/download.html
# 3. Configure Nginx as a Windows service using NSSM or similar tool
# 4. Adjust all paths in this script to match your actual installation