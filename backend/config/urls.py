"""
config/urls.py
Rutas principales del proyecto DUBSS.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# ─── Prefijo de API ───────────────────────────────────────────────────────────
API_V1 = "api/v1/"

urlpatterns = [
    # Admin Django
    path("admin/", admin.site.urls),

    # ── Módulos de la API ────────────────────────────────────────────────────
    path(API_V1 + "auth/",           include("apps.users.urls.auth_urls")),
    path(API_V1 + "usuarios/",       include("apps.users.urls.user_urls")),
    path(API_V1 + "deportes/",       include("apps.deportes.urls")),
    path(API_V1 + "instalaciones/",  include("apps.instalaciones.urls")),
    path(API_V1 + "fixture/",        include("apps.fixture.urls")),
    path(API_V1 + "ml/",             include("apps.ml.urls")),
    path(API_V1 + "notificaciones/", include("apps.notificaciones.urls")),
    path(API_V1 + "reportes/",       include("apps.reportes.urls")),

    # ── Swagger / OpenAPI ─────────────────────────────────────────────────────
    path("api/schema/",         SpectacularAPIView.as_view(),        name="schema"),
    path("api/docs/",           SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/",          SpectacularRedocView.as_view(url_name="schema"),   name="redoc"),
]

# Archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug Toolbar
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
