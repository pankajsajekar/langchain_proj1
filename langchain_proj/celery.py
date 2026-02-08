"""
Celery Configuration for RAG System
Place this in your project root (same level as manage.py)
"""
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'langchain_proj.settings')

# Create Celery app
app = Celery('langchain_proj')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

