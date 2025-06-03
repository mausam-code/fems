"""
ASGI config for fems project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import pathlib
from django.core.asgi import get_asgi_application

# Load environment variables from .env file if it exists
from dotenv import load_dotenv
env_path = pathlib.Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fems.settings')
# Override with environment variable if set
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'fems.settings')
os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

application = get_asgi_application()
