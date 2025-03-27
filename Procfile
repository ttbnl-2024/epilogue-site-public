release: python manage.py migrate --no-input
web: bin/start-pgbouncer gunicorn -c gph/gunicorn.py
worker: python manage.py run_huey --workers 4
