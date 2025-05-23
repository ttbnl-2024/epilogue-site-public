"""
Django settings for gph project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import datetime
import os
from zoneinfo import ZoneInfo

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure logs directory exists.
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

SECRET_KEY = os.environ.get("SECRET_KEY", "FIXME_SECRET_KEY_HERE")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "huey.contrib.djhuey",
    "corsheaders",
    "impersonate",
    "mathfilters",
    "puzzles",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
    "puzzles.messaging.log_request_middleware",
    "puzzles.context.context_middleware",
    "puzzles.puzzlehandlers.reverse_proxy_middleware",
    "puzzles.views.accept_ranges_middleware",
]

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_CACHE_ALIAS = "default"

ROOT_URLCONF = "gph.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "puzzles.context.context_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "gph.wsgi.application"
ASGI_APPLICATION = "gph.asgi.application"


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        "NAME": os.path.join(BASE_DIR, "prod-export/prod-export.sqlite3"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"
PY_TIME_ZONE = ZoneInfo(TIME_ZONE)

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.normpath(os.path.join(BASE_DIR, "locale"))]
FORMAT_MODULE_PATH = ["gph.formats"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, "static"))
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Email SMTP information

EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "mitmh2024@gmail.com"
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_PORT = 587
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_SUBJECT_PREFIX = "[MH24 Epilogue] "

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_GUILD_ID = "1065160431028670534"
DISCORD_HINT_CHANNEL_ID = "1191612770882424972"

ALERT_WEBHOOK_URL = os.environ.get("ALERT_WEBHOOK_URL", "")
SUBMISSION_WEBHOOK_URL = os.environ.get("SUBMISSION_WEBHOOK_URL", "")
FREE_ANSWER_WEBHOOK_URL = os.environ.get("FREE_ANSWER_WEBHOOK_URL", "")
VICTORY_WEBHOOK_URL = os.environ.get("VICTORY_WEBHOOK_URL", "")

SILK_ENABLED = False
DEBUG_TOOLBAR_ENABLED = False
DISCORD_ENABLED = os.getenv("DISCORD_ENABLED", "").lower() in ("true", "1", "t")
FORCE_LOCAL_EMAIL = False
FORCE_LOCAL_DISCORD = False

# https://docs.djangoproject.com/en/3.1/topics/logging/

# Loggers and handlers both have a log level; handlers ignore messages at lower
# levels. This is useful because a logger can have multiple handlers with
# different log levels.

# The levels are DEBUG < INFO < WARNING < ERROR < CRITICAL. DEBUG logs a *lot*,
# like exceptions every time a template variable is looked up and missing,
# which happens literally all the time, so that might be a bit too much.

# If you want to log to stdout (e.g. on Heroku), the handler looks as follows:
# {
#     'level': 'INFO',
#     'class': 'logging.StreamHandler',
#     'stream': sys.stdout,
#     'formatter': 'django',
# },

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "django": {
            "format": (
                "%(asctime)s (PID %(process)d) [%(levelname)s] %(module)s\n%(message)s"
            )
        },
        "puzzles": {
            "format": (
                "%(asctime)s (PID %(process)d) [%(levelname)s] %(name)s %(message)s"
            )
        },
    },
    # FIXME you may want to change the filenames to something like
    # /srv/logs/django.log or similar
    "handlers": {
        "django": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "django.log"),
            "formatter": "django",
        },
        "general": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "general.log"),
            "formatter": "puzzles",
        },
        "puzzle": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "puzzle.log"),
            "formatter": "puzzles",
        },
        "request": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "request.log"),
            "formatter": "puzzles",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["django"],
            "level": "INFO",
            "propagate": True,
        },
        "puzzles": {
            "handlers": ["general"],
            "level": "INFO",
            "propagate": True,
        },
        "puzzles.puzzle": {
            "handlers": ["puzzle"],
            "level": "INFO",
            "propagate": False,
        },
        "puzzles.request": {
            "handlers": ["request"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Google Analytics
GA_CODE = ""

LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"

# Hunt config. These are defined here to make them easy to override
# under different environments.

HUNT_START_TIME = datetime.datetime(
    year=2025,
    month=3,
    day=8,
    hour=14,
    minute=0,
    tzinfo=PY_TIME_ZONE,
)

HUNT_END_TIME = datetime.datetime(
    year=2025,
    month=3,
    day=16,
    hour=23,
    minute=0,
    tzinfo=PY_TIME_ZONE,
)


HUNT_CLOSE_TIME = datetime.datetime(
    year=2025,
    month=3,
    day=31,
    hour=23,
    minute=59,
    tzinfo=PY_TIME_ZONE,
)
