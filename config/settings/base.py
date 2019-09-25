"""
Base settings for VarFish project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import environ
import sys

from dotenv import load_dotenv

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
]

# Apps specific for this project go here.
LOCAL_APPS = [
    # custom users app
    "varfish.users.apps.UsersConfig",
    # Your stuff: custom apps go here
    "clinvar.apps.ClinvarConfig",
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
DATABASES = {"default": env.db("DATABASE_URL", default="postgres:///varfish")}
DATABASES["default"]["ATOMIC_REQUESTS"] = False

# ALDJEMY CONFIGURATION
# ------------------------------------------------------------------------------
# We have to do some fixes to the Aldjemy data types...


def fixed_array_type(field):
    import aldjemy.table
    import sqlalchemy.dialects.postgresql

    data_types = aldjemy.table.DATA_TYPES
    internal_type = field.base_field.get_internal_type()

    # currently no support for multi-dimensional arrays
    if internal_type in data_types and internal_type != "ArrayField":
        sub_type = data_types[internal_type](field)
    else:
        raise RuntimeError("Unsupported array element type")

    return sqlalchemy.dialects.postgresql.ARRAY(sub_type)


import sqlalchemy.dialects.postgresql

ALDJEMY_DATA_TYPES = {
    "ArrayField": lambda field: fixed_array_type(field),
    "UUIDField": lambda _: sqlalchemy.dialects.postgresql.UUID(as_uuid=True),
    "JSONField": lambda _: sqlalchemy.dialects.postgresql.JSONB,
    "BinaryField": lambda _: sqlalchemy.dialects.postgresql.BYTEA,
}


# We need to tell Aldjemy that we're using the psycopg2 driver so the correct
# SQL Alchemy connection dialect is used.
ALDJEMY_ENGINES = {"postgres": "postgresql+psycopg2"}


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
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

# Set the number of partitions to create for the "SmallVariants" table.  This
# setting will be interpreted in the initial migration that creates the small
# variant table.  It must not be changed afterwards.
VARFISH_PARTITION_MODULUS_SMALLVARIANT = env.int("VARFISH_PARTITION_MODULUS_SMALLVARIANT", 1024)
# The same for structural variant tables
VARFISH_PARTITION_MODULUS_SVS = env.int(
    "VARFISH_PARTITION_MODULUS_SMALLVARIANT", VARFISH_PARTITION_MODULUS_SMALLVARIANT
)

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

# Enable CADD configuration, default is disabled.
VARFISH_ENABLE_CADD = env.bool("VARFISH_ENABLE_CADD", default=False)
# Configure URL to CADD REST API
VARFISH_CADD_REST_API_URL = env.str("VARFISH_CADD_REST_API_URL", "")
# Configure maximal number of genes to send to Exomiser API
VARFISH_CADD_MAX_VARS = env.int("VARFISH_CADD_MAX_VARS", 5000)

# Varfish: MutationTaster URL
VARFISH_MUTATIONTASTER_REST_API_URL = env.str(
    "VARFISH_MUTATIONTASTER_REST_API_URL", "https://www.mutationdistiller.org/MTc/MT_API.cgi"
)
VARFISH_MUTATIONTASTER_MAX_VARS = env.int("VARFISH_MUTATIONTASTER_MAX_VARS", 30)

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

# Your common stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "knox.auth.TokenAuthentication",
    )
}

SITE_TITLE = "VarFish"
SITE_SUBTITLE = env.str("SITE_SUBTITLE", "Beta")
SITE_INSTANCE_TITLE = env.str("SITE_INSTANCE_TITLE", "Deployment Instance Name")

PROJECTROLES_SECRET_LENGTH = 32
PROJECTROLES_INVITE_EXPIRY_DAYS = env.int("PROJECTROLES_INVITE_EXPIRY_DAYS", 14)
PROJECTROLES_SEND_EMAIL = env.bool("PROJECTROLES_SEND_EMAIL", False)
PROJECTROLES_HELP_HIGHLIGHT_DAYS = 7

PROJECTROLES_ENABLE_SEARCH = True
PROJECTROLES_SEARCH_PAGINATION = 5

SODAR_API_DEFAULT_VERSION = "0.1"
SODAR_API_MEDIA_TYPE = "application/vnd.bihealth.sodar+json"

PROJECTROLES_SITE_MODE = env.str("PROJECTROLES_SITE_MODE", "TARGET")
PROJECTROLES_TARGET_CREATE = env.bool("PROJECTROLES_TARGET_CREATE", True)
PROJECTROLES_ADMIN_OWNER = env.str("PROJECTROLES_DEFAULT_ADMIN", "admin")
PROJECTROLES_DEFAULT_ADMIN = env.str("PROJECTROLES_DEFAULT_ADMIN", "admin")

# Allow showing and synchronizing local non-admin users
PROJECTROLES_ALLOW_LOCAL_USERS = env.bool("PROJECTROLES_ALLOW_LOCAL_USERS", False)

PROJECTROLES_HIDE_APP_LINKS = ["svs"]

ENABLED_BACKEND_PLUGINS = ["timeline_backend"]
ENABLED_BACKEND_PLUGINS += env.list("ENABLED_BACKEND_PLUGINS", None, [])


def set_logging(debug):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"simple": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
        "handlers": {
            "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"}
        },
        "loggers": {
            "projectroles": {
                "level": "DEBUG" if debug else "INFO",
                "handlers": ["console"],
                "propagate": False,
            }
        },
    }


LOGGING = set_logging(DEBUG)

ENABLE_LDAP = env.bool("ENABLE_LDAP", False)
ENABLE_LDAP_SECONDARY = env.bool("ENABLE_LDAP_SECONDARY", False)

if ENABLE_LDAP:
    import itertools
    import ldap
    from django_auth_ldap.config import LDAPSearch

    # Default values
    LDAP_DEFAULT_CONN_OPTIONS = {ldap.OPT_REFERRALS: 0}
    LDAP_DEFAULT_FILTERSTR = "(sAMAccountName=%(user)s)"
    LDAP_DEFAULT_ATTR_MAP = {"first_name": "givenName", "last_name": "sn", "email": "mail"}

    # Primary LDAP server
    AUTH_LDAP_SERVER_URI = env.str("AUTH_LDAP_SERVER_URI", None)
    AUTH_LDAP_BIND_DN = env.str("AUTH_LDAP_BIND_DN", None)
    AUTH_LDAP_BIND_PASSWORD = env.str("AUTH_LDAP_BIND_PASSWORD", None)
    AUTH_LDAP_CONNECTION_OPTIONS = LDAP_DEFAULT_CONN_OPTIONS

    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        env.str("AUTH_LDAP_USER_SEARCH_BASE", None), ldap.SCOPE_SUBTREE, LDAP_DEFAULT_FILTERSTR
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
            env.str("AUTH_LDAP2_USER_SEARCH_BASE", None), ldap.SCOPE_SUBTREE, LDAP_DEFAULT_FILTERSTR
        )
        AUTH_LDAP2_USER_ATTR_MAP = LDAP_DEFAULT_ATTR_MAP
        AUTH_LDAP2_USERNAME_DOMAIN = env.str("AUTH_LDAP2_USERNAME_DOMAIN")
        AUTH_LDAP2_DOMAIN_PRINTABLE = env.str("AUTH_LDAP2_DOMAIN_PRINTABLE", None)

        AUTHENTICATION_BACKENDS = tuple(
            itertools.chain(
                ("projectroles.auth_backends.SecondaryLDAPBackend",), AUTHENTICATION_BACKENDS
            )
        )
