from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeporteViewSet, CategoriaViewSet,
    CampeonatoViewSet, EquipoViewSet, FichaJugadorViewSet,
)

router = DefaultRouter()
router.register(r"deportes",    DeporteViewSet,      basename="deporte")
router.register(r"categorias",  CategoriaViewSet,    basename="categoria")
router.register(r"campeonatos", CampeonatoViewSet,   basename="campeonato")
router.register(r"equipos",     EquipoViewSet,       basename="equipo")
router.register(r"jugadores",   FichaJugadorViewSet, basename="jugador")

urlpatterns = [path("", include(router.urls))]
