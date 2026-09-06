"""
Production settings for the Azure App Service deployment.

Only active when DJANGO_SETTINGS_MODULE is set to
"knowlxcirclebackend.production"; everything else defaults to
"knowlxcirclebackend.settings".
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F401,F403
from .settings import ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DATABASES, SECRET_KEY

DEBUG = False

# settings.py chooses its insecure development fallbacks - the throwaway
# SECRET_KEY and the local sqlite file - from the DEBUG value it computed for
# itself. This module forces DEBUG off *afterwards*, so with DJANGO_DEBUG=True
# left set in the environment those fallbacks would survive into a deployment
# that then looks fully hardened: real traffic, HSTS and secure cookies on, but
# signing JWTs and sessions with a key that is published in this repository and
# reading a sqlite file. Re-validate both instead of trusting them.
if not SECRET_KEY or SECRET_KEY.startswith("django-insecure"):
    raise ImproperlyConfigured(
        "Refusing to start with the development SECRET_KEY. Export "
        "DJANGO_SECRET_KEY (or the legacy DJANGO_API_KEY / SECRET_KEY) for this "
        "deployment."
    )

if DATABASES["default"].get("ENGINE", "").endswith("sqlite3"):
    raise ImproperlyConfigured(
        "Refusing to start against the local sqlite database. Export DATABASE_URL "
        "(or DBNAME / DBUSER / DBPASSWORD / DBHOST / DBPORT) and leave "
        "DEVELOPMENT_MODE unset in this deployment."
    )

# settings.py already folds WEBSITE_HOSTNAME in; repeat it here so this module
# is still correct if it is imported with a different environment.
WEBSITE_HOSTNAME = os.getenv("WEBSITE_HOSTNAME", "").strip()

ALLOWED_HOSTS = list(ALLOWED_HOSTS)
CSRF_TRUSTED_ORIGINS = list(CSRF_TRUSTED_ORIGINS)

if WEBSITE_HOSTNAME:
    if WEBSITE_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(WEBSITE_HOSTNAME)
    if "https://" + WEBSITE_HOSTNAME not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append("https://" + WEBSITE_HOSTNAME)

# DEBUG is forced off above, so apply the hardening unconditionally here too -
# settings.py only applies it when it computed DEBUG as False itself.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
