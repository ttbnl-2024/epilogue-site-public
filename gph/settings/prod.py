import os
import sys

import dj_database_url
import sentry_sdk
from huey import RedisHuey
from redis import ConnectionPool

from .base import *
from .base import CACHES, DATABASES, INSTALLED_APPS, LOGGING

DEBUG = False

IS_TEST = False

REDIS_URL = os.getenv("REDIS_URL", "")

if REDIS_URL:
    pool = ConnectionPool.from_url(REDIS_URL, ssl_cert_reqs=None, max_connections=20)
    HUEY = RedisHuey(connection_pool=pool)

DATABASE_URL = os.getenv("DATABASE_URL", "")
DATABASES["default"] = dj_database_url.parse(  # type: ignore
    DATABASE_URL, conn_max_age=600, conn_health_checks=True
)

DISCORD_GUILD_ID = "1065160431028670534"
DISCORD_HINT_CHANNEL_ID = "1343775110661935154"

if REDIS_URL:
    CACHES["default"] = {  # type: ignore
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "ssl_cert_reqs": None,
        },
    }

for handler in LOGGING["handlers"].values():
    if "filename" in handler:
        handler["class"] = "logging.StreamHandler"
        handler["stream"] = sys.stdout
        del handler["filename"]

SENTRY_URL = os.getenv("SENTRY_URL", "")
sentry_sdk.init(
    dsn=SENTRY_URL,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

INSTALLED_APPS.append("anymail")
# This will use the HTTP API, not SMTP
EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"
POSTMARK_SERVER_TOKEN = os.getenv("POSTMARK_SERVER_TOKEN", "")
ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": POSTMARK_SERVER_TOKEN,
}

# Used for constructing URLs; include the protocol and trailing
# slash (e.g. 'https://galacticpuzzlehunt.com/')
DOMAIN = "https://epilogue.mitmh2024.com/"

STATIC_URL = os.getenv("DJANGO_STATIC_HOST", "").rstrip("/") + "/static/"

# List of places you're serving from, e.g.
# ['galacticpuzzlehunt.com', 'gph.example.com']; or just ['*']
ALLOWED_HOSTS = ["*"]
