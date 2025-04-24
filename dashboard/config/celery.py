import os
import logging
from celery import Celery
from celery.signals import setup_logging

logger = logging.getLogger(__name__)

# Validate settings module exists
DJANGO_SETTINGS_MODULE = 'config.settings'
if not os.path.exists(DJANGO_SETTINGS_MODULE.replace('.', '/') + '.py'):
    raise ImportError(f"Settings module '{DJANGO_SETTINGS_MODULE}' not found")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', DJANGO_SETTINGS_MODULE)

# Initialize Celery with proper error handling
try:
    app = Celery('config')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
except Exception as e:
    logger.error(f"Failed to initialize Celery: {str(e)}")
    raise

@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure logging for Celery"""
    logging.basicConfig(level=logging.INFO)

@app.task(bind=True,
         max_retries=3,
         default_retry_delay=60,
         time_limit=30)
def debug_task(self):
    try:
        logger.info(f'Request: {self.request!r}')
    except Exception as exc:
        logger.error(f"Task failed: {str(exc)}")
        self.retry(exc=exc)