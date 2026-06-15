"""
Vercel Serverless Entry Point for Django Backend
This file tells Vercel how to run Django as a serverless function.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wallet_project.settings')

from django.core.wsgi import get_wsgi_application

# Initialize Django - Vercel's @vercel/python builder
# auto-detects the 'application' WSGI callable
application = get_wsgi_application()
