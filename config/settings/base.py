import os
from ast import literal_eval
from datetime import timedelta
from pathlib import Path

import environ

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

DISABLE_DOT_ENV = os.environ.get("DISABLE_DOT_ENV", default="False")

DOT_ENV_PATH = ROOT_DIR / ".env" if (ROOT_DIR / ".env").exists() else ROOT_DIR / ".env.example"

env = environ.Env()
if DISABLE_DOT_ENV != "True":
    env.read_env(DOT_ENV_PATH)

# General
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG", default=False)
TIME_ZONE = "Asia/Taipei"
LANGUAGE_CODE = "en-us"
SITE_ID = 1
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [
    ROOT_DIR / "locale",
]
APPEND_SLASH = False
SERVER_HOST = env("SERVER_HOST", default="127.0.0.1")
SERVER_PORT = env.int("SERVER_PORT", default=80)

# Frontend
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "[::1]"],
)

AUTH_USER_MODEL = "core.User"

# Storage
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Application
APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Required for allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # "allauth.headless",  # This module doesn't exist in this version
    "rest_framework",  # Django REST Framework
    "rest_framework.authtoken",  # Required for dj-rest-auth
    "rest_framework_simplejwt",  # JWT authentication
    "dj_rest_auth",  # REST API for allauth
    "dj_rest_auth.registration",  # Registration endpoints
    "ninja",
    "ninja_extra",
    "guardian",
]
LOCAL_APPS = [
    "features.core",
    "features.helper",
    "features.host",
]
INSTALLED_APPS = APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

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
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                "django.template.context_processors.i18n",
                "django.template.context_processors.tz",
                "django.template.context_processors.debug",
            ],
        },
    },
]
FORM_RENDERER = "django.forms.renderers.DjangoTemplates"
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# Security
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# URL Configuration
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("DATABASE_HOST"),
        "PORT": env("DATABASE_PORT"),
        "NAME": env("DATABASE_DB"),
    },
}
DATABASES["default"]["USER"] = env("DATABASE_USER")
DATABASES["default"]["PASSWORD"] = env("DATABASE_PASSWORD")

# Cache
CACHES = {
    "default": {
        "BACKEND": env("CACHES_BACKEND", default="django_valkey.cache.ValkeyCache"),
        "LOCATION": env("CACHES_LOCATION", default="redis://localhost:6379/0"),
    },
}

# Authentication
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "guardian.backends.ObjectPermissionBackend",
]
LOGIN_REDIRECT_URL = ""
LOGIN_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

SOCIALACCOUNT_LOGIN_ON_GET = True
ANONYMOUS_USER_NAME = "anonymous"

ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = env("ACCOUNT_LOGOUT_REDIRECT_URL", default="")
ACCOUNT_USER_MODEL_USERNAME_FIELD = "name"
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_EMAIL_VERIFICATION = env("ACCOUNT_EMAIL_VERIFICATION", default="mandatory")
ACCOUNT_ADAPTER = "config.adapters.AccountAdapter"

# Social account settings for Google login
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Simple JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# dj-rest-auth settings
REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "access_token",
    "JWT_AUTH_REFRESH_COOKIE": "refresh_token",
    "USER_DETAILS_SERIALIZER": "dj_rest_auth.serializers.UserDetailsSerializer",
}

# Password validation
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Cors
CORS_ALLOWED_ORIGINS = []
CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOW_CREDENTIALS = True

# Admin
ADMIN_URL = "admin/"
ADMINS = [("""sks""", "estel105293@gmail.com")]
MANAGERS = ADMINS
# Force the `admin` sign in process to go through the `django-allauth` workflow
DJANGO_ADMIN_FORCE_ALLAUTH = env("DJANGO_ADMIN_FORCE_ALLAUTH", default=False)

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = ROOT_DIR / "static"
STATIC_URL = "static/"
MEDIA_ROOT = ROOT_DIR / "media"
MEDIA_URL = "/api/media/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# LOGGING
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
if literal_eval(DISABLE_DOT_ENV):
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_logging_filter": {
                "()": "utils.logging.RequestLoggingFilter",
            }
        },
        "formatters": {
            "json_formatter": {
                "()": "utils.logging.JsonFormatter",
            },
            "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
        },
        "handlers": {
            "uvicorn_console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "json_formatter",
                "filters": ["request_logging_filter"],
            },
            "uvicorn_error_handler": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["uvicorn_console"],
                "propagate": False,
                "level": "INFO",
            },
            "common.middlewares": {
                "handlers": ["uvicorn_console"],
                "propagate": False,
                "level": "INFO",
            },
            "uvicorn.access": {
                "handlers": [],
                "propagate": False,
                "level": "INFO",
            },
            "uvicorn.error": {
                "handlers": ["uvicorn_error_handler"],
                "propagate": False,
                "level": "INFO",
            },
            "uvicorn": {
                "handlers": ["uvicorn_error_handler"],
                "propagate": False,
                "level": "INFO",
            },
            "sentry_sdk": {
                "handlers": ["uvicorn_console"],
                "propagate": False,
                "level": "ERROR",
            },
            "django.security.DisallowedHost": {
                "handlers": ["uvicorn_console"],
                "propagate": False,
                "level": "ERROR",
            },
        },
    }

else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "default": {
                "()": "utils.logging.RequestLoggingFilter",
            }
        },
        "formatters": {
            "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
            "color_formatter": {"()": "utils.logging.ColorFormatter"},
            "json_formatter": {"()": "utils.logging.JsonFormatter"},
        },
        "handlers": {
            "django_console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "color_formatter",
                "filters": ["default"],
            },
            "uvicorn_console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "color_formatter",
                "filters": ["default"],
            },
        },
        "loggers": {
            "django": {
                "handlers": ["django_console"],
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["uvicorn_console"],
                "propagate": True,
            },
        },
    }
