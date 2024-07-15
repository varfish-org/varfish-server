import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("varfish")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

if "production" in os.environ.get("DJANGO_SETTINGS_MODULE"):
    # Configure routing as we nee different degrees of concurrency for the background job processing.
    app.conf.task_routes = {
        # The bulk import jobs share a common name pattern and should go to the "import" queue.
        "*.run_import_*_bg_job": {"queue": "import"},
        # Also use this for kiosk annotation and import jobs.
        "*.run_kiosk_bg_job": {"queue": "import"},
        # The filter tasks go to the "query" queue.
        "*.*_filter_task": {"queue": "query"},
        "*.run_*query_bg_job": {"queue": "query"},
        # The export tasks go to the "export" queue.
        "*.export_*_task": {"queue": "export"},
        # The maintenance tasks go to the "maintenance" queue.
        "*.refresh_*": {"queue": "maintenance"},
        "*.clear_*": {"queue": "maintenance"},
        "*.compute_*": {"queue": "maintenance"},
        "*.sync_*": {"queue": "maintenance"},
    }

    # Explicitely set the name of the default queue to default (is celery).
    app.conf.task_default_queue = "default"

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
