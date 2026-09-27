from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartidoViewSet, GenerarFixtureView, TablaPosicionesView

router = DefaultRouter()
router.register(r"partidos", PartidoViewSet, basename="partido")

urlpatterns = [
    path("", include(router.urls)),
    path("generar/",          GenerarFixtureView.as_view(),   name="fixture-generar"),
    path("tabla-posiciones/", TablaPosicionesView.as_view(),  name="fixture-tabla"),
]
