"""
config/settings/development.py
Configuración para entorno de desarrollo local.
"""
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Debug Toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa
INTERNAL_IPS = ["127.0.0.1"]

# En desarrollo envía emails a la consola
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logging detallado
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module}: {message}",
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
        "level": "DEBUG",
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",  # Cambia a DEBUG para ver todas las queries SQL
        },
    },
}
