"""
Test settings for VarFish project.

- Used to run tests fast on the continuous integration server and locally
"""

from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
# Turn debug off so tests run faster
DEBUG = False
TEMPLATES[0]["OPTIONS"]["debug"] = True  # coverage needs this

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="CHANGEME!!!")

FIELD_ENCRYPTION_KEY = env(
    "FIELD_ENCRYPTION_KEY", default="_XRAzgLd6NHj8G4q9FNV0p3Um9g4hy8BPBN-AL0JWO0="
)

# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

# In-memory email backend stores messages in django.core.mail.outbox
# for unit testing purposes
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# CACHING
# ------------------------------------------------------------------------------
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": ""}}

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = "snapshottest.django.TestRunner"

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = True
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# In tests ... everything goes.
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])
# END SITE CONFIGURATION

# PROJECTROLES TEST
# ------------------------------------------------------------------------------
PROJECTROLES_TEST_UI_CHROME_OPTIONS = [
    "headless",
    "no-sandbox",  # For Gitlab-CI compatibility
    "disable-dev-shm-usage",  # For testing stability
]
PROJECTROLES_TEST_UI_WINDOW_SIZE = (1400, 1000)
PROJECTROLES_TEST_UI_WAIT_TIME = 30

# PASSWORD HASHING
# ------------------------------------------------------------------------------
# Use fast password hasher so tests run faster
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATE LOADERS
# ------------------------------------------------------------------------------
# Keep templates in memory so tests run faster
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    [
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ]
]

# Logging
# ------------------------------------------------------------------------------

LOGGING_LEVEL = env.str("LOGGING_LEVEL", "CRITICAL")
LOGGING = set_logging(LOGGING_LEVEL)

# Varfish: REST Services
# ------------------------------------------------------------------------------

# Eanble v2 analysis
VARFISH_GEN2_ANALYSIS = True

# Disable all REST services for testing.

VARFISH_ENABLE_CADD = False

# VarFish: Import
# ------------------------------------------------------------------------------

# Allow importing from file for testing.
VARFISH_CASE_IMPORT_ALLOW_FILE = True

# Varfish: Beacon Feature
# ------------------------------------------------------------------------------

# Eanble for testing.
VARFISH_ENABLE_BEACON_SITE = env.bool("VARFISH_ENABLE_BEACON_SITE", default=True)

# Varfish: S3 Internal Storage
# ------------------------------------------------------------------------------

#: Configure the internal storage
VARFISH_CASE_IMPORT_INTERNAL_STORAGE = InternalStorageConfig(
    **env.json(
        "VARFISH_CASE_IMPORT_INTERNAL_STORAGE",
        # configure with default settings to use for testing, same as in
        # varfish-docker-compose-ng default setup
        {
            "bucket": "varfish-server-test",
            "host": "localhost",
            "port": 3010,
            "access_key": "minioadmin",
            "secret_key": "minio-root-password",
        },
    )
)
