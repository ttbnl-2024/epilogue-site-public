#!/usr/bin/env python3
import multiprocessing
import os

wsgi_app = "gph.wsgi:application"

workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count()))
workers *= 2
loglevel = "error"
pidfile = "gunicorn.pid"
reload = True

# Log to stdout
accesslog = "-"

# Time out after 25 seconds (notably shorter than Heroku's)
timeout = 25

# Restart gunicorn worker processes every 1200-1250 requests
max_requests = 1200
max_requests_jitter = 50

# Load app pre-fork to save memory and worker startup time
preload_app = True
