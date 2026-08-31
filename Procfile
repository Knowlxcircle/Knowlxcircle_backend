# Railway/Heroku run `release:` before the new version goes live.
release: python manage.py migrate --noinput
# Azure App Service (Oryx) only ever reads `web:` and has no release phase, so
# the migration is chained here too. It runs once, before gunicorn forks.
web: python manage.py migrate --noinput && gunicorn knowlxcirclebackend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 --access-logfile - --error-logfile -
