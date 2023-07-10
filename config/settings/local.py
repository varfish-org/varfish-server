"""
Local settings for VarFish project.

- Run in Debug mode

- Use mailhog for emails

- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .base import *  # noqa

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = True
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="A0@><8J,K@Ed/jbgci:zS!uvIhJC5Hpgb%DOV{?8vc#Q]OaeoX")

# Mail settings
# ------------------------------------------------------------------------------

EMAIL_PORT = 1025

EMAIL_HOST = "localhost"


# CACHING
# ------------------------------------------------------------------------------
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": ""}}

# django-debug-toolbar
# ------------------------------------------------------------------------------
if DEBUG:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INSTALLED_APPS += ["debug_toolbar"]

    INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
        "SHOW_TEMPLATE_CONTEXT": True,
        "ALCHEMY_DB_ALIASES": "config.settings.local.alchemy_dbs",
    }

    DEBUG_TOOLBAR_PANELS = [
        # Basic values
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]


# Celery
# ------------------------------------------------------------------------------
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = False
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = False

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["django_extensions"]

# VarFish Microservices
#
# Setup of the "microservices" such as viguno, mehari, annonars, and nginx.
# ------------------------------------------------------------------------------
VARFISH_BACKEND_URL_ANNONARS = env.str(
    "VARFISH_BACKEND_URL_ANNONARS", default="http://localhost:3001"
)
VARFISH_BACKEND_URL_MEHARI = env.str("VARFISH_BACKEND_URL_MEHARI", default="http://localhost:3002")
VARFISH_BACKEND_URL_VIGUNO = env.str("VARFISH_BACKEND_URL_VIGUNO", default="http://localhost:3003")
VARFISH_BACKEND_URL_NGINX = env.str("VARFISH_BACKEND_URL_NGINX", default="http://localhost:3004")

# URL prefix through the front reverse proxy (traefik for production).
VARFISH_BACKEND_URL_PREFIX_ANNONARS = env.str(
    "VARFISH_BACKEND_URL_PREFIX_ANNONARS", default="/proxy/varfish/annonars"
)
VARFISH_BACKEND_URL_PREFIX_MEHARI = env.str(
    "VARFISH_BACKEND_URL_PREFIX_MEHARI", default="/proxy/varfish/mehari"
)
VARFISH_BACKEND_URL_PREFIX_VIGUNO = env.str(
    "VARFISH_BACKEND_URL_PREFIX_VIGUNO", default="/proxy/varfish/viguno"
)
VARFISH_BACKEND_URL_PREFIX_NGINX = env.str(
    "VARFISH_BACKEND_URL_PREFIX_NGINX", default="/proxy/varfish/nginx"
)

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Your local stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

VITE_DEV_SERVER = env.str("VITE_DEV_SERVER", "http://localhost:3000")
