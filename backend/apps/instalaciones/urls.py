from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstalacionViewSet, CanchaViewSet, BloqueoViewSet

router = DefaultRouter()
router.register(r"instalaciones", InstalacionViewSet, basename="instalacion")
router.register(r"canchas",       CanchaViewSet,      basename="cancha")
router.register(r"bloqueos",      BloqueoViewSet,     basename="bloqueo")

urlpatterns = [path("", include(router.urls))]
