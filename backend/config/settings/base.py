"""
config/settings/base.py
Configuración base compartida entre todos los entornos.
"""
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Lee variables desde .env
env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")

# ─── Aplicaciones ─────────────────────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",
]

LOCAL_APPS = [
    "apps.users",
    "apps.deportes",
    "apps.instalaciones",
    "apps.fixture",
    "apps.ml",
    "apps.notificaciones",
    "apps.reportes",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

# ─── Base de datos ─────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     env("POSTGRES_DB"),
        "USER":     env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST":     env("POSTGRES_HOST", default="db"),
        "PORT":     env("POSTGRES_PORT", default="5432"),
        "OPTIONS":  {"connect_timeout": 10},
    }
}

# ─── Auth / Password ──────────────────────────────────────────────────────────
AUTH_USER_MODEL = "users.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Internacionalización ──────────────────────────────────────────────────────
LANGUAGE_CODE = "es-bo"
TIME_ZONE     = "America/La_Paz"
USE_I18N      = True
USE_TZ        = True

# ─── Archivos estáticos y media ───────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "mediafiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Django REST Framework ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ─── JWT ─────────────────────────────────────────────────────────────────────
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=60)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS":  True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD":     "id",
    "USER_ID_CLAIM":     "user_id",
}

# ─── Swagger (drf-spectacular) ────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE":       "DUBSS API",
    "DESCRIPTION": "Sistema de Gestión Deportiva DUBSS - UAGRM. API REST documentada con OpenAPI 3.0.",
    "VERSION":     "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {"name": "Equipo DUBSS", "email": "dubss@uagrm.edu.bo"},
    "LICENSE": {"name": "MIT"},
    "TAGS": [
        {"name": "auth",           "description": "Autenticación y tokens JWT"},
        {"name": "usuarios",       "description": "Gestión de usuarios y perfiles"},
        {"name": "deportes",       "description": "Deportes, categorías y campeonatos"},
        {"name": "equipos",        "description": "Equipos y jugadores"},
        {"name": "instalaciones",  "description": "Canchas y horarios"},
        {"name": "fixture",        "description": "Generación y gestión de fixture"},
        {"name": "resultados",     "description": "Resultados e incidencias"},
        {"name": "ml",             "description": "Predicciones con Machine Learning"},
        {"name": "notificaciones", "description": "Envío de notificaciones"},
        {"name": "reportes",       "description": "Exportación de reportes"},
    ],
}

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000"],
)
CORS_ALLOW_CREDENTIALS = True

# ─── Email ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND      = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST         = env("EMAIL_HOST",          default="smtp.gmail.com")
EMAIL_PORT         = env.int("EMAIL_PORT",      default=587)
EMAIL_USE_TLS      = env.bool("EMAIL_USE_TLS",  default=True)
EMAIL_HOST_USER    = env("EMAIL_HOST_USER",     default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

# ─── Celery (tareas asíncronas) ───────────────────────────────────────────────
CELERY_BROKER_URL        = env("REDIS_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND    = env("REDIS_URL", default="redis://redis:6379/0")
CELERY_ACCEPT_CONTENT    = ["json"]
CELERY_TASK_SERIALIZER   = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE          = TIME_ZONE

# ─── APIs externas ────────────────────────────────────────────────────────────
GROQ_API_KEY         = env("GROQ_API_KEY",         default="")
OPENWEATHER_API_KEY  = env("OPENWEATHER_API_KEY",  default="")
FIREBASE_SERVER_KEY  = env("FIREBASE_SERVER_KEY",  default="")
