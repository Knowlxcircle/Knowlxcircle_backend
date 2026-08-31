"""
Django settings for knowlxcirclebackend project.

Targets Django 5.2 LTS on Python >= 3.12.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    """Read a boolean environment variable ("1"/"true"/"yes"/"on" are true)."""
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_csv(name):
    """Read a comma separated environment variable into a list of strings."""
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


def extend(base, extra):
    """Append `extra` to `base` preserving order and skipping duplicates."""
    for item in extra:
        if item not in base:
            base.append(item)
    return base


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool("DJANGO_DEBUG", False)

# SECURITY WARNING: keep the secret key used in production secret!
# DJANGO_SECRET_KEY is the canonical name; DJANGO_API_KEY and SECRET_KEY are the
# legacy names the CI workflow and Azure app settings still export.
SECRET_KEY = (
    os.getenv("DJANGO_SECRET_KEY")
    or os.getenv("DJANGO_API_KEY")
    or os.getenv("SECRET_KEY")
    or ""
).strip()

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-development-only-key-do-not-use-in-production"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY is not set. Export DJANGO_SECRET_KEY (or the legacy "
            "DJANGO_API_KEY / SECRET_KEY) before running with DJANGO_DEBUG turned off."
        )

# Azure App Service publishes the site hostname here.
WEBSITE_HOSTNAME = os.getenv("WEBSITE_HOSTNAME", "").strip()

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
extend(ALLOWED_HOSTS, env_csv("DJANGO_ALLOWED_HOSTS"))
if WEBSITE_HOSTNAME:
    extend(ALLOWED_HOSTS, [WEBSITE_HOSTNAME])

CSRF_TRUSTED_ORIGINS = [
    "https://knowlxcircleapi.azurewebsites.net",
    "http://localhost:8000",
]
extend(CSRF_TRUSTED_ORIGINS, env_csv("CSRF_TRUSTED_ORIGINS"))
if WEBSITE_HOSTNAME:
    extend(CSRF_TRUSTED_ORIGINS, ["https://" + WEBSITE_HOSTNAME])


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "gemini",
    "rest_framework",
    "corsheaders",
    "dashboard",
    "authentication",
    "article",
    "circle",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
]

# django.contrib.sites primary key. This is a Sites row id, not an app id.
SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile', 'user_friends'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'updated_time',
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'en_US',
        'VERIFIED_EMAIL': False,
        'VERSION': os.getenv("FACEBOOK_GRAPH_API_VERSION", "v23.0"),
    }
}

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "").strip()
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "").strip()

# Only advertise the app credentials when both are configured; otherwise allauth
# falls back to a SocialApp row in the database.
if FACEBOOK_APP_ID and FACEBOOK_APP_SECRET:
    SOCIALACCOUNT_PROVIDERS['facebook']['APP'] = {
        "client_id": FACEBOOK_APP_ID,
        "secret": FACEBOOK_APP_SECRET,
        "key": "",
    }

# django-cors-headers requires CorsMiddleware as high as possible, and in any
# case above CommonMiddleware and WhiteNoiseMiddleware, so that CORS headers
# survive short-circuited responses (redirects, 304s, static files).
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "knowlxcirclebackend.urls"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "knowlxcirclebackend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# The driver is psycopg 3 (`psycopg[binary]`), not psycopg2.

DEVELOPMENT_MODE = env_bool("DEVELOPMENT_MODE", False)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DEVELOPMENT_MODE or (not DATABASE_URL and DEBUG):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(conn_max_age=600, conn_health_checks=True),
    }
else:
    raise ImproperlyConfigured(
        "DATABASE_URL is not set. Export DATABASE_URL, or set DEVELOPMENT_MODE=True "
        "to use the local sqlite database."
    )


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static and media files
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# CompressedStaticFilesStorage, not the Manifest variant: nothing in CI runs
# collectstatic, and a missing manifest turns every admin page into a 500.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_LIFETIME': timedelta(days=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME_LATE_USER': timedelta(days=1),
    'SLIDING_TOKEN_LIFETIME_LATE_USER': timedelta(days=30),
}


# Cache. Redis only when a location is actually configured - pointing
# django_redis at an empty location fails on first use in every environment
# that has no Redis.

REDIS_URL = (os.getenv("CACHELOCATION") or os.getenv("REDIS_URL") or "").strip()

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "knowlxcircle-locmem",
        }
    }


# CORS. A wildcard origin is invalid alongside credentialed requests, so the
# allow-list is explicit and extended from the environment.

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://knowlxcircleapi.azurewebsites.net',
    'https://knowlxcirclebackend-production.up.railway.app',
]
extend(CORS_ALLOWED_ORIGINS, env_csv("CORS_ALLOWED_ORIGINS"))
if WEBSITE_HOSTNAME:
    extend(CORS_ALLOWED_ORIGINS, ["https://" + WEBSITE_HOSTNAME])


# OpenRouter fronts hundreds of models behind one OpenAI-compatible endpoint;
# gemini/client.py reads these. Pick the model with OPENROUTER_MODEL.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-5-mini").strip() or "openai/gpt-5-mini"
OPENROUTER_TIMEOUT = float(os.getenv("OPENROUTER_TIMEOUT", "60"))
OPENROUTER_MAX_RETRIES = int(os.getenv("OPENROUTER_MAX_RETRIES", "2"))
# Optional: credits this app on the OpenRouter leaderboards.
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "").strip()
OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "Knowlxcircle").strip()


# Logging. The views swallow exceptions, so without this nothing reaches the
# App Service log stream.

_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO").strip().upper()
if _LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    _LOG_LEVEL = "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": _LOG_LEVEL,
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "article": {"handlers": ["console"], "level": _LOG_LEVEL, "propagate": False},
        "authentication": {"handlers": ["console"], "level": _LOG_LEVEL, "propagate": False},
        "circle": {"handlers": ["console"], "level": _LOG_LEVEL, "propagate": False},
        "dashboard": {"handlers": ["console"], "level": _LOG_LEVEL, "propagate": False},
        "gemini": {"handlers": ["console"], "level": _LOG_LEVEL, "propagate": False},
    },
}


# Production hardening. Only applied with DEBUG off so local development over
# plain http keeps working.

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
