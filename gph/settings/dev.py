import datetime
import os

from huey import SqliteHuey

from .base import *
from .base import INSTALLED_APPS, LOGS_DIR, MIDDLEWARE, PY_TIME_ZONE

DEBUG = True

IS_TEST = True

DOMAIN = "http://localhost:8000/"

ALLOWED_HOSTS = ["*"]

DEBUG_TOOLBAR_ENABLED = True
if DEBUG_TOOLBAR_ENABLED:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]
    DEBUG_TOOLBAR_CONFIG = {
        "RESULTS_CACHE_SIZE": 100,
    }

# Not strictly necessary since we run in immediate
HUEY = SqliteHuey(immediate=True)

SILK_ENABLED = True
if SILK_ENABLED:
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")
    # authentication for silk
    SILKY_AUTHENTICATION = True
    SILKY_AUTHORISATION = True
    # discard raw requests and responses exceeding size
    SILKY_MAX_REQUEST_BODY_SIZE = 0
    SILKY_MAX_RESPONSE_BODY_SIZE = 0
    # use cProfile
    SILKY_PYTHON_PROFILER = False

# Outgoing messages blocked by IS_TEST
FORCE_LOCAL_DISCORD = False

DISCORD_ENABLED = True

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_GUILD_ID = "1191611884533727272"
DISCORD_HINT_CHANNEL_ID = "1191612770882424972"

EMAIL_SUBJECT_PREFIX = "[MH24 Epilogue dev] "

HUNT_START_TIME = datetime.datetime(
    year=2025,
    month=3,
    day=8,
    hour=13,
    minute=0,
    tzinfo=PY_TIME_ZONE,
)

STATIC_ROOT = "static"
INSTALLED_APPS.insert(0, "whitenoise.runserver_nostatic")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "django-file": {
            "format": (
                "%(asctime)s (PID %(process)d) [%(levelname)s] %(module)s\n%(message)s"
            )
        },
        "puzzles-file": {
            "format": (
                "%(asctime)s (PID %(process)d) [%(levelname)s] %(name)s %(message)s"
            )
        },
        "django-console": {
            "format": (
                "\033[34;1m%(asctime)s \033[35;1m[%(levelname)s] \033[34;1m%(module)s\033[0m\n%(message)s"
            )
        },
        "puzzles-console": {
            "format": (
                "\033[36;1m%(asctime)s \033[35;1m[%(levelname)s] \033[36;1m%(name)s\033[0m %(message)s"
            )
        },
    },
    "handlers": {
        "django": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "django.log"),
            "formatter": "django-file",
        },
        "general": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "general.log"),
            "formatter": "puzzles-file",
        },
        "puzzle": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "puzzle.log"),
            "formatter": "puzzles-file",
        },
        "request": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "request.log"),
            "formatter": "puzzles-file",
        },
        "django-console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "django-console",
        },
        "puzzles-console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "puzzles-console",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["django", "django-console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.db.backends": {
            "level": "INFO",
            "handlers": ["django", "django-console"],
            "propagate": False,
        },
        "django.server": {
            "level": "INFO",
            "handlers": ["django"],
            "propagate": False,
        },
        "django.utils.autoreload": {
            "level": "INFO",
            "propagate": True,
        },
        "puzzles": {
            "handlers": ["general", "puzzles-console"],
            "level": "INFO",
            "propagate": True,
        },
        "puzzles.puzzle": {
            "handlers": ["puzzle", "puzzles-console"],
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
