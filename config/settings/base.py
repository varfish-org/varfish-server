"""
Base settings for VarFish project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import logging
import os
import re
import sys

from dotenv import load_dotenv
import environ

from varfish import __version__ as varfish_version

logger = logging.getLogger(__name__)

SITE_PACKAGE = "varfish"
ROOT_DIR = environ.Path(__file__) - 3  # (varfish/config/settings/base.py - 3 = varfish/)
APPS_DIR = ROOT_DIR.path("varfish")

# Check whether we are running tsts (this is important to use models and not materialized views in tests).
IS_TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = False
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = False

# Load environment from .env file if available.
load_dotenv()

# Load operating system environment variables and then prepare to use them
env = environ.Env()

# .env file, should load only in development environment
READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)

if READ_DOT_ENV_FILE:
    # Operating System Environment variables have precedence over variables defined in the .env file,
    # that is to say variables from the .env files will only be used if not defined
    # as environment variables.
    env_file = str(ROOT_DIR.path(".env"))
    print("Loading : {}".format(env_file))
    env.read_env(env_file)
    print("The .env file has been loaded. See base.py for more information")

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    # Technically, django-su is a third party app, but must be before ``django.contrib.admin``
    "django_su",
    # Default Django apps:
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",  # Handy template tags
    # Useful template tags:
    # 'django.contrib.humanize',
    # Admin
    "django.contrib.admin",
]
THIRD_PARTY_APPS = [
    "crispy_forms",  # Form layouts
    "rules.apps.AutodiscoverRulesConfig",
    "djangoplugins",
    "pagedown",
    "markupfield",
    "rest_framework",
    "knox",
    "aldjemy",
    "adminalerts",
    "userprofile.apps.UserprofileConfig",
    "projectroles.apps.ProjectrolesConfig",
    "timeline.apps.TimelineConfig",
    "siteinfo.apps.SiteinfoConfig",
    "docs",  # For the online user documentation/manual
    "dal",
    "dal_select2",
    "cryptographic_fields",
    "rest_framework_httpsignature",
    "django_saml2_auth",
    "dj_iconify.apps.DjIconifyConfig",
]

# Apps specific for this project go here.
LOCAL_APPS = [
    # custom users app
    "varfish.users.apps.UsersConfig",
    "varfish.vueapp.apps.VueappConfig",
    # Your stuff: custom apps go here
    "clinvar.apps.ClinvarConfig",
    "clinvar_export.apps.ClinvarExportConfig",
    "cohorts.apps.CohortsConfig",
    "conservation.apps.ConservationConfig",
    "dbsnp.apps.DbsnpConfig",
    "frequencies.apps.FrequenciesConfig",
    "hgmd.apps.HgmdConfig",
    "geneinfo.apps.GeneinfoConfig",
    "importer.apps.ImporterConfig",
    "genomicfeatures.apps.GenomicFeaturesConfig",
    "pathways.apps.PathwaysConfig",
    "variants.apps.VariantsConfig",
    "bgjobs.apps.BgjobsConfig",
    "var_stats_qc.apps.VarStatsQcConfig",
    "templatetags.apps.TemplatetagsConfig",
    "svdbs.apps.SvDbsConfig",
    "svs.apps.SvsConfig",
    "extra_annos.apps.ExtraAnnosConfig",
    "tokens.apps.TokensConfig",
    "maintenance.apps.MaintenanceConfig",
    "regmaps.apps.RegmapsConfig",
    "beaconsite.apps.BeaconsiteConfig",
    "genepanels.apps.GenepanelsConfig",
    "cases.apps.CasesConfig",
    "varannos.apps.VarannosConfig",
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Django-docs Settings
# ------------------------------------------------------------------------------

# Note: for serving to work, the docs have to be built after deployment.
DOCS_ROOT = ROOT_DIR.path("docs_manual/_build/html/")
# DOCS_ACCESS = 'public'  # default

# Bump the default number of fields in forms.
DATA_UPLOAD_MAX_NUMBER_FIELDS = env.int("DATA_UPLOAD_MAX_NUMBER_FIELDS", 100_000)

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {"sites": "varfish.contrib.sites.migrations"}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)

# GENERAL VARFISH SETTINGS
# ------------------------------------------------------------------------------
# Query timeout in seconds, "0" to disable.
QUERY_TIMEOUT = env.int("VARFISH_QUERY_TIMEOUT", 600) or None

# KIOSK-MODE RELATED
# ------------------------------------------------------------------------------
# Enable/disable kiosk mode.
KIOSK_MODE = env.bool("VARFISH_KIOSK_MODE", False)
# Name of the Kiosk user
KIOSK_USER = env.str("VARFISH_KIOSK_USER", "kiosk_user")
# Name of top-level category with kiosk cases.
KIOSK_CAT = "VarFish Kiosk"
# Name of project below that Kategory (mandatory structure from SODAR core).
KIOSK_PROJ_PREFIX = "Cases"
# Define conda path for loading varfish-annotator environment
KIOSK_CONDA_PATH = env.str("VARFISH_KIOSK_CONDA_PATH", "")
# Varfish Annotator database path
KIOSK_VARFISH_ANNOTATOR_DB_PATH = env.str("VARFISH_KIOSK_VARFISH_ANNOTATOR_DB_PATH", "")
# Varfish Annotator ensembl ser path
KIOSK_VARFISH_ANNOTATOR_ENSEMBL_SER_PATH = env.str(
    "VARFISH_KIOSK_VARFISH_ANNOTATOR_ENSEMBL_SER_PATH", ""
)
# Varfish Annotator refseq ser path
KIOSK_VARFISH_ANNOTATOR_REFSEQ_SER_PATH = env.str(
    "VARFISH_KIOSK_VARFISH_ANNOTATOR_REFSEQ_SER_PATH", ""
)
# Varfish Annotator reference path
KIOSK_VARFISH_ANNOTATOR_REFERENCE_PATH = env.str(
    "VARFISH_KIOSK_VARFISH_ANNOTATOR_REFERENCE_PATH", ""
)
# Varfish Annotator release
KIOSK_VARFISH_ANNOTATOR_RELEASE = env.str("VARFISH_KIOSK_VARFISH_ANNOTATOR_RELEASE", "GRCh37")
# Activate Kiosk mode in project roles
PROJECTROLES_KIOSK_MODE = KIOSK_MODE
# Set limit for delegate roles per project to 1.
PROJECTROLES_DELEGATE_LIMIT = 1
# Allow including of additional HTML into the head.
PROJECTROLES_INLINE_HEAD_INCLUDE = env.str("PROJECTROLES_INLINE_HEAD_INCLUDE", "")

# Enable VarFishKioskUserMiddlerware in Kiosk mode.
if KIOSK_MODE:
    logger.info("Enabling VarFishKioskUserMiddleware")
    MIDDLEWARE += ["varfish.utils.VarFishKioskUserMiddleware"]


# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)


# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_SENDER = env("EMAIL_SENDER", default="noreply@example.com")
EMAIL_SUBJECT_PREFIX = env("EMAIL_SUBJECT_PREFIX", default="")


# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ("""Oliver Stolpe""", "oliver.stolpe@bihealth.de"),
    ("""Manuel Holtgrewe""", "manuel.holtgrewe@bihealth.de"),
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Uses django-environ to accept uri format
# See: https://django-environ.readthedocs.io/en/latest/#supported-types
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres:///varfish"),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = False

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# SENTRY CONFIGURATION
# ------------------------------------------------------------------------------
if env.bool("ENABLE_SENTRY", default=False):
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    SENTRY_DSN = "%s?verify_ssl=0" % env.str("SENTRY_DSN")
    sentry_sdk.init(
        SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
            SqlalchemyIntegration(),
        ],
    )

# ALDJEMY CONFIGURATION
# ------------------------------------------------------------------------------

# We need to tell Aldjemy that we're using the psycopg2 driver so the correct
# SQL Alchemy connection dialect is used.
ALDJEMY_ENGINES = {"postgres": "postgresql+psycopg2"}


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local  zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "UTC"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])
# END SITE CONFIGURATION


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        "OPTIONS": {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            "debug": DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # Your stuff: custom template context processors go here
                "projectroles.context_processors.urls_processor",
                "projectroles.context_processors.site_app_processor",
                "projectroles.context_processors.app_alerts_processor",
                "django_su.context_processors.is_su",
            ],
        },
    }
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap4"

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("staticfiles"))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR.path("static"))]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR("media"))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# PASSWORD STORAGE SETTINGS
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "rules.permissions.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
    "django_su.backends.SuBackend",
]

# Some really nice defaults

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "home"
LOGIN_URL = "login"

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = "slugify.slugify"


# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r"^admin/"

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "redis://localhost:6379/0")
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
CELERYD_TASK_TIME_LIMIT = 5 * 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
CELERYD_TASK_SOFT_TIME_LIMIT = 60

# Varfish: Base
# ------------------------------------------------------------------------------

# Limit on number of cases to allow project/cohort wide queries for.
VARFISH_MAX_CASE_QUERY_COUNT = env.int("VARFISH_MAX_CASE_QUERY_COUNT", 100)

# Yes, we want ForeinKey(unique=True), thank you very much.
SILENCED_SYSTEM_CHECKS = ["fields.W342"]

# Use URLs to represent files in DRF.
UPLOADED_FILES_USE_URL = True

# Set the number of partitions to create for the "SmallVariants" table.  This
# setting will be interpreted in the initial migration that creates the small
# variant table.  It must not be changed afterwards.
VARFISH_PARTITION_MODULUS_SMALLVARIANT = env.int("VARFISH_PARTITION_MODULUS_SMALLVARIANT", 1024)
# The same for structural variant tables
VARFISH_PARTITION_MODULUS_SVS = env.int(
    "VARFISH_PARTITION_MODULUS_SMALLVARIANT", VARFISH_PARTITION_MODULUS_SMALLVARIANT
)

# Text to display on the login page.
VARFISH_LOGIN_PAGE_TEXT = env.str("VARFISH_LOGIN_PAGE_TEXT", "")

# Key to use for the encryption of secrets such as the secret RSA keys used by
# the beaconsite module.  Losing/changing means losing all encrypted data.  While
# DJANGO_SECRET_KEY can be changed and only session data is lost, this is worse.
#
# Leave blank to use no secret key.
FIELD_ENCRYPTION_KEY = env.str(
    "FIELD_ENCRYPTION_KEY", "_XRAzgLd6NHj8G4q9FNV0p3Um9g4hy8BPBN-AL0JWO0="
)

# Number of cases to perform in one query for joint queries.
QUERY_MAX_UNION = env.int("VARFISH_QUERY_MAX_UNION", 20)

# Timeout (in hours) for VarFish cleaning up background SV sets in "building" state.
SV_CLEANUP_BUILDING_SV_SETS = env.int("VARFISH_SV_CLEANUP_BUILDING_SV_SETS", 48)

# Path to database for the worker.
WORKER_DB_PATH = env.str("VARFISH_WORKER_DB_PATH", "")

# Path to executable for worker.
WORKER_EXE_PATH = env.str("VARFISH_WORKER_EXE_PATH", "varfish-server-worker")

# URL prefix to look at for worker.
WORKER_REST_BASE_URL = env.str("VARFISH_WORKER_REST_BASE_URL", "http://127.0.0.1:8081")

# Varfish: Exomiser
# ------------------------------------------------------------------------------

# Enable exomiser configuration, default is disabled.
VARFISH_ENABLE_EXOMISER_PRIORITISER = env.bool("VARFISH_ENABLE_EXOMISER_PRIORITISER", default=False)
# Configure URL to API
VARFISH_EXOMISER_PRIORITISER_API_URL = env.str("VARFISH_EXOMISER_PRIORITISER_API_URL", "")
# Configure maximal number of genes to send to Exomiser API
VARFISH_EXOMISER_PRIORITISER_MAX_GENES = env.int("VARFISH_EXOMISER_PRIORITISER_MAX_GENES", 1000)

# Varfish: CADD
# ------------------------------------------------------------------------------

# Note well that while VarFish is released under a permissive open source license
# the CADD score is only freely available for non-commercial use.

# Enable CADD prioritization.
VARFISH_ENABLE_CADD = env.bool("VARFISH_ENABLE_CADD", default=False)
# Configure URL to CADD REST API
VARFISH_CADD_REST_API_URL = env.str("VARFISH_CADD_REST_API_URL", "")
# CADD version to use with CADD REST API.
VARFISH_CADD_REST_API_CADD_VERSION = env.str("VARFISH_CADD_REST_API_CADD_VERSION", "v1.6")
# Configure maximal number of genes to send to Exomiser API
VARFISH_CADD_MAX_VARS = env.int("VARFISH_CADD_MAX_VARS", 5000)

# Enable CADA prioritization.
VARFISH_ENABLE_CADA = env.bool("VARFISH_ENABLE_CADA", default=False)
# Configure URL to CADA REST API
# REST API documentation for CADA can be found here: https://app.swaggerhub.com/apis-docs/schmida/CADA/1.0.0
VARFISH_CADA_REST_API_URL = env.str(
    "VARFISH_CADA_REST_API_URL", "https://cada.gene-talk.de/api/process"
)

# Enable submission of variants to CADD server.
VARFISH_ENABLE_CADD_SUBMISSION = env.bool("VARFISH_ENABLE_CADD_SUBMISSION", default=False)
# CADD version to use for for submission
VARFISH_CADD_SUBMISSION_VERSION = env.str("VARFISH_CADD_SUBMISSION_VERSION", default="v1.6")

# Varfish: MutationTaster URL
VARFISH_MUTATIONTASTER_REST_API_URL = env.str(
    "VARFISH_MUTATIONTASTER_REST_API_URL",
    "https://www.genecascade.org/MTc85/MT_API.cgi",
)
VARFISH_MUTATIONTASTER_BATCH_VARS = env.int("VARFISH_MUTATIONTASTER_BATCH_VARS", 50)
VARFISH_MUTATIONTASTER_MAX_VARS = env.int("VARFISH_MUTATIONTASTER_MAX_VARS", 500)

# VarfFish: Enable SPANR
VARFISH_ENABLE_SPANR_SUBMISSION = env.bool("VARFISH_ENABLE_SPANR_SUBMISSION", False)

# Varfish: UMD URL
VARFISH_UMD_REST_API_URL = env.str(
    "VARFISH_UMD_REST_API_URL", "http://umd-predictor.eu/webservice.php"
)

# Varfish: Jannovar
# ------------------------------------------------------------------------------

# Enable Jannovar configuration, default is disabled.
VARFISH_ENABLE_JANNOVAR = env.bool("VARFISH_ENABLE_JANNOVAR", default=False)
# Configure URL to Jannovar REST API
VARFISH_JANNOVAR_REST_API_URL = env.str("VARFISH_JANNOVAR_REST_API_URL", "")

# Varfish: SVs
# ------------------------------------------------------------------------------

# Configure experimental SV filtration feature.
VARFISH_ENABLE_SVS = env.bool("VARFISH_ENABLE_SVS", default=False)

# Varfish: HGMD Professional
# ------------------------------------------------------------------------------

# Enable link-out to HGMD Professional
VARFISH_ENABLE_HGMD_PRO_LINKOUT = env.bool("VARFISH_ENABLE_HGMD_PRO_LINKOUT", default=False)
# Configure URL prefix for HGMD Professional
VARFISH_HGMD_PRO_LINKOUT_URL_PREFIX = env.bool(
    "VARFISH_HGMD_PRO_LINKOUT_URL_PREFIX",
    default="https://my.qiagendigitalinsights.com/bbp/view/hgmd/pro",
)

# Varfish: GAGH Beacon
# ------------------------------------------------------------------------------

# Enabling or disabling Beacon site.
VARFISH_ENABLE_BEACON_SITE = env.bool("VARFISH_ENABLE_BEACON_SITE", default=False)

# Your common stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "knox.auth.TokenAuthentication",
    ),
}

if KIOSK_MODE:
    SITE_TITLE = "VarFish (Kiosk)"
else:
    SITE_TITLE = "VarFish"
SITE_SUBTITLE = env.str("SITE_SUBTITLE", "Bollonaster")
SITE_INSTANCE_TITLE = env.str("SITE_INSTANCE_TITLE", "Deployment Instance Name")

PROJECTROLES_SECRET_LENGTH = 32
PROJECTROLES_INVITE_EXPIRY_DAYS = env.int("PROJECTROLES_INVITE_EXPIRY_DAYS", 14)
PROJECTROLES_SEND_EMAIL = env.bool("PROJECTROLES_SEND_EMAIL", False)
PROJECTROLES_HELP_HIGHLIGHT_DAYS = 7

PROJECTROLES_ENABLE_SEARCH = not KIOSK_MODE
PROJECTROLES_SEARCH_PAGINATION = 5

SODAR_API_MEDIA_TYPE = "application/vnd.bihealth.varfish+json"
SODAR_API_DEFAULT_VERSION = varfish_version.split("-")[0]
SODAR_API_ALLOWED_VERSIONS = [
    "0.23.9",
]


PROJECTROLES_SITE_MODE = env.str("PROJECTROLES_SITE_MODE", "TARGET")
PROJECTROLES_TARGET_CREATE = env.bool("PROJECTROLES_TARGET_CREATE", True)
PROJECTROLES_ADMIN_OWNER = env.str("PROJECTROLES_DEFAULT_ADMIN", "root")
PROJECTROLES_DEFAULT_ADMIN = env.str("PROJECTROLES_DEFAULT_ADMIN", PROJECTROLES_ADMIN_OWNER)
PROJECTROLES_EMAIL_SENDER_REPLY = env.bool("PROJECTROLES_EMAIL_SENDER_REPLY", False)

# Allow showing and synchronizing local non-admin users
PROJECTROLES_ALLOW_LOCAL_USERS = env.bool("PROJECTROLES_ALLOW_LOCAL_USERS", False)

# Hide selected apps
PROJECTROLES_HIDE_APP_LINKS = ["svs", "variants"]

# Whether or not to sync from remote (disable only locally).
VARFISH_PROJECTROLES_SYNC_REMOTE = env.bool("VARFISH_PROJECTROLES_SYNC_REMOTE", True)

ENABLED_BACKEND_PLUGINS = ["timeline_backend"]
ENABLED_BACKEND_PLUGINS += env.list("ENABLED_BACKEND_PLUGINS", None, [])

PROJECTROLES_DISABLE_CATEGORIES = env.bool("PROJECTROLES_DISABLE_CATEGORIES", False)

# Warn about unsupported browsers (IE)
PROJECTROLES_BROWSER_WARNING = True

# Disable default CDN JS/CSS includes to replace with local files.  This
# is primarily used for Docker-based deployments.
PROJECTROLES_DISABLE_CDN_INCLUDES = env.bool("PROJECTROLES_DISABLE_CDN_INCLUDES", False)

if PROJECTROLES_DISABLE_CDN_INCLUDES:
    PROJECTROLES_CUSTOM_JS_INCLUDES = [
        "/static/local/js/jquery-3.5.1.min.js",
        "/static/local/js/bootstrap.bundle.min.js",
        "/static/local/js/tether.min.js",
        "/static/local/js/shepherd.min.js",
        "/static/local/js/clipboard.min.js",
        "/static/local/js/bundle.tracing.min.js",
        "/static/local/js/jquery.dataTables.min.js",
        "/static/local/js/bootstrap-select.min.js",
        "/static/local/js/tagsinput.js",
        "/static/local/js/jsrender.min.js",
        "/static/local/js/plotly-1.54.5.min.js",
        "/static/local/js/axios.min.js",
        "/static/local/js/palette.min.js",
        "/static/local/js/lodash.min.js",
    ]
    PROJECTROLES_CUSTOM_CSS_INCLUDES = [
        "/static/local/css/font-awesome.min.css",
        "/static/local/css/bootstrap.min.css",
        "/static/local/css/bootstrap-select.min.css",
        "/static/local/css/dataTables.jqueryui.min.css",
        "/static/local/css/tagsinput.css",
    ]
else:
    PROJECTROLES_CUSTOM_JS_INCLUDES = []
    PROJECTROLES_CUSTOM_CSS_INCLUDES = []


# Logging
# ------------------------------------------------------------------------------

# Custom logging level
LOGGING_LEVEL = env.str("LOGGING_LEVEL", "DEBUG" if DEBUG else "ERROR")

LOGGING_APPS = env.list(
    "LOGGING_APPS",
    default=[
        "irodsadmin",
        "irodsbackend",
        "landingzones",
        "ontologyaccess",
        "projectroles",
        "samplesheets",
        "sodarcache",
        "taskflowbackend",
        "svs",
        "variants",
        #        'django',
        #        'django.requests',
    ],
)

LOGGING_FILE_PATH = env.str("LOGGING_FILE_PATH", None)


def set_logging(level):
    app_logger_config = {
        "level": level,
        "handlers": ["console", "file"] if LOGGING_FILE_PATH else ["console"],
        "propagate": True,
    }
    log_handlers = {
        "console": {
            "level": level,
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    }
    if LOGGING_FILE_PATH:
        log_handlers["file"] = {
            "level": level,
            "class": "logging.FileHandler",
            "filename": LOGGING_FILE_PATH,
            "formatter": "simple",
        }
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"simple": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
        "handlers": log_handlers,
        "loggers": {a: app_logger_config for a in LOGGING_APPS},
    }


LOGGING_DEBUG = env.bool("LOGGING_DEBUG", False)
LOGGING = set_logging("DEBUG" if (DEBUG or LOGGING_DEBUG) else "INFO")

# LDAP configuration
# ------------------------------------------------------------------------------

ENABLE_LDAP = env.bool("ENABLE_LDAP", False)
ENABLE_LDAP_SECONDARY = env.bool("ENABLE_LDAP_SECONDARY", False)

if ENABLE_LDAP:
    import itertools

    from django_auth_ldap.config import LDAPSearch
    import ldap

    # Default values
    LDAP_DEFAULT_CONN_OPTIONS = {ldap.OPT_REFERRALS: 0}
    LDAP_DEFAULT_FILTERSTR = "(sAMAccountName=%(user)s)"
    LDAP_DEFAULT_ATTR_MAP = {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail",
    }

    # Primary LDAP server
    AUTH_LDAP_SERVER_URI = env.str("AUTH_LDAP_SERVER_URI", None)
    AUTH_LDAP_BIND_DN = env.str("AUTH_LDAP_BIND_DN", None)
    AUTH_LDAP_BIND_PASSWORD = env.str("AUTH_LDAP_BIND_PASSWORD", None)
    AUTH_LDAP_CONNECTION_OPTIONS = LDAP_DEFAULT_CONN_OPTIONS

    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        env.str("AUTH_LDAP_USER_SEARCH_BASE", None),
        ldap.SCOPE_SUBTREE,
        LDAP_DEFAULT_FILTERSTR,
    )
    AUTH_LDAP_USER_ATTR_MAP = LDAP_DEFAULT_ATTR_MAP
    AUTH_LDAP_USERNAME_DOMAIN = env.str("AUTH_LDAP_USERNAME_DOMAIN", None)
    AUTH_LDAP_DOMAIN_PRINTABLE = env.str("AUTH_LDAP_DOMAIN_PRINTABLE", None)

    AUTHENTICATION_BACKENDS = tuple(
        itertools.chain(("projectroles.auth_backends.PrimaryLDAPBackend",), AUTHENTICATION_BACKENDS)
    )

    # Secondary LDAP server
    if ENABLE_LDAP_SECONDARY:
        AUTH_LDAP2_SERVER_URI = env.str("AUTH_LDAP2_SERVER_URI", None)
        AUTH_LDAP2_BIND_DN = env.str("AUTH_LDAP2_BIND_DN", None)
        AUTH_LDAP2_BIND_PASSWORD = env.str("AUTH_LDAP2_BIND_PASSWORD", None)
        AUTH_LDAP2_CONNECTION_OPTIONS = LDAP_DEFAULT_CONN_OPTIONS

        AUTH_LDAP2_USER_SEARCH = LDAPSearch(
            env.str("AUTH_LDAP2_USER_SEARCH_BASE", None),
            ldap.SCOPE_SUBTREE,
            LDAP_DEFAULT_FILTERSTR,
        )
        AUTH_LDAP2_USER_ATTR_MAP = LDAP_DEFAULT_ATTR_MAP
        AUTH_LDAP2_USERNAME_DOMAIN = env.str("AUTH_LDAP2_USERNAME_DOMAIN")
        AUTH_LDAP2_DOMAIN_PRINTABLE = env.str("AUTH_LDAP2_DOMAIN_PRINTABLE", None)

        AUTHENTICATION_BACKENDS = tuple(
            itertools.chain(
                ("projectroles.auth_backends.SecondaryLDAPBackend",),
                AUTHENTICATION_BACKENDS,
            )
        )

# DJANGO SU configuration
# ------------------------------------------------------------------------------

# URL to redirect after the login.
# Default: "/"
DJANGO_SU_LOGIN_REDIRECT_URL = "/"

# URL to redirect after the logout.
# Default: "/"
DJANGO_SU_LOGOUT_REDIRECT_URL = "/"

# A function to specify the perms that the user must have can use su
# Default: None
DJANGO_SU_LOGIN_CALLBACK = None

# A function to override the django.contrib.auth.login(request, user)
# function so you can set session data, etc.
# Default: None
DJANGO_SU_CUSTOM_LOGIN_ACTION = None


# SAML configuration
# ------------------------------------------------------------------------------


ENABLE_SAML = env.bool("ENABLE_SAML", False)
SAML2_AUTH = {
    # Required setting
    #
    # Pysaml2 Saml client settings, cf.
    # https://pysaml2.readthedocs.io/en/latest/howto/config.html
    "SAML_CLIENT_SETTINGS": {
        # The optional entity ID string to be passed in the 'Issuer'
        # element of authn request, if required by the IDP.
        "entityid": env.str("SAML_CLIENT_ENTITY_ID", "SODARcore"),
        "entitybaseurl": env.str("SAML_CLIENT_ENTITY_URL", "https://localhost:8000"),
        "metadata": {
            "local": [
                env.str(
                    "SAML_CLIENT_METADATA_FILE", "metadata.xml"
                ),  # The auto(dynamic) metadata configuration URL of SAML2
            ],
        },
        "service": {
            "sp": {
                "idp": env.str(
                    "SAML_CLIENT_IDP",
                    "https://sso.hpc.bihealth.org/auth/realms/cubi",
                ),
                # Keycloak expects client signature
                "authn_requests_signed": "true",
                # Enforce POST binding which is required by keycloak
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
        },
        "key_file": env.str("SAML_CLIENT_KEY_FILE", "key.pem"),
        "cert_file": env.str("SAML_CLIENT_CERT_FILE", "cert.pem"),
        "xmlsec_binary": env.str("SAML_CLIENT_XMLSEC1", "/usr/bin/xmlsec1"),
        "encryption_keypairs": [
            {
                "key_file": env.str("SAML_CLIENT_KEY_FILE", "key.pem"),
                "cert_file": env.str("SAML_CLIENT_CERT_FILE", "cert.pem"),
            }
        ],
    },
    # Custom target redirect URL after the user get logged in. Default to
    # /admin if not set. This setting will be overwritten if you have parameter
    # ?next= specificed in the login URL.
    "DEFAULT_NEXT_URL": "/",
    # Optional settings
    "NEW_USER_PROFILE": {
        "USER_GROUPS": env.list("SAML_NEW_USER_GROUPS", default=[]),
        "ACTIVE_STATUS": env.bool("SAML_NEW_USER_ACTIVE_STATUS", True),
        "STAFF_STATUS": env.bool("SAML_NEW_USER_STAFF_STATUS", True),
        "SUPERUSER_STATUS": env.bool("SAML_NEW_USER_SUPERUSER_STATUS", False),
    },
    "ATTRIBUTES_MAP": env.dict(
        "SAML_ATTRIBUTES_MAP",
        default={
            "email": "urn:oid:1.2.840.113549.1.9.1",
            "username": "username",
            "first_name": "urn:oid:2.5.4.42",
            "last_name": "urn:oid:2.5.4.4",
        },
    ),
    # Optional SAML Trigger
    # Very unlikely to be needed in configuration, since it requires
    # changes to the codebase
    # 'TRIGGER': {
    #     'FIND_USER': 'path.to.your.find.user.hook.method',
    #     'NEW_USER': 'path.to.your.new.user.hook.method',
    #     'CREATE_USER': 'path.to.your.create.user.hook.method',
    #     'BEFORE_LOGIN': 'path.to.your.login.hook.method',
    # },
}

# 'ASSERTION_URL': 'https://your.url.here',  # Custom URL to validate incoming SAML requests against
assertion_url = env.str("SAML_ASSERTION_URL", None)
if assertion_url is not None:
    SAML2_AUTH = {**SAML2_AUTH, **{"ASSERTION_URL": assertion_url}}


# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------

# Uploaded Media Files
# ------------------------
# See: http://django-storages.readthedocs.io/en/latest/index.html
ENABLE_S3 = env.bool("VARFISH_USE_S3", False)
if ENABLE_S3:
    INSTALLED_APPS += ["storages"]

    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
    AWS_AUTO_CREATE_BUCKET = env.bool("AWS_AUTO_CREATE_BUCKET", True)
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", None)
    AWS_AUTO_CREATE_BUCKET = True
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = None

    # AWS cache settings, don't change unless you know what you're doing:
    AWS_EXPIRY = 60 * 60 * 24 * 7

    # TODO See: https://github.com/jschneier/django-storages/issues/47
    # Revert the following and use str after the above-mentioned bug is fixed in
    # either django-storage-redux or boto
    control = "max-age=%d, s-maxage=%d, must-revalidate" % (AWS_EXPIRY, AWS_EXPIRY)
    AWS_HEADERS = {"Cache-Control": bytes(control, encoding="latin-1")}

    # URL that handles the media served from MEDIA_ROOT, used for managing
    # stored files.
    MEDIA_URL = "http://localhost/-minio/%s/" % AWS_STORAGE_BUCKET_NAME
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"


# ICONIFY CONFIGURATION
# ------------------------------------------------------------------------------
ICONIFY_JSON_ROOT = os.path.join(STATIC_ROOT, "iconify")

VARFISH_ENABLE_VARIANTS_VUEAPP = env.bool("VARFISH_ENABLE_VARIANTS_VUEAPP", default=False)
