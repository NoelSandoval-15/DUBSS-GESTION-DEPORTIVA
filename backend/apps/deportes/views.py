"""
apps/deportes/views.py
CU03, CU04, CU05, CU06, CU09
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.users.permissions import EsAdminDUBSS, EsCoordinadorOAdmin, EsLecturaPublica
from .models import Deporte, Categoria, Campeonato, Equipo, FichaJugador
from .serializers import (
    DeporteSerializer, CategoriaSerializer, CampeonatoSerializer,
    EquipoSerializer, FichaJugadorSerializer,
)


@extend_schema(tags=["deportes"])
class DeporteViewSet(viewsets.ModelViewSet):
    """CU05 — CRUD de deportes."""
    queryset           = Deporte.objects.filter(activo=True).order_by("nombre")
    serializer_class   = DeporteSerializer
    permission_classes = [EsLecturaPublica]
    search_fields      = ["nombre"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsAdminDUBSS()]
        return [EsLecturaPublica()]


@extend_schema(tags=["deportes"])
class CategoriaViewSet(viewsets.ModelViewSet):
    """CU04 — CRUD de categorías."""
    queryset           = Categoria.objects.filter(activa=True).select_related("deporte")
    serializer_class   = CategoriaSerializer
    permission_classes = [EsLecturaPublica]
    filterset_fields   = ["deporte", "genero"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsAdminDUBSS()]
        return [EsLecturaPublica()]


@extend_schema(tags=["deportes"])
class CampeonatoViewSet(viewsets.ModelViewSet):
    """CU09 — CRUD de campeonatos."""
    queryset = Campeonato.objects.select_related(
        "deporte", "categoria", "creado_por"
    ).order_by("-fecha_inicio")
    serializer_class   = CampeonatoSerializer
    filterset_fields   = ["estado", "deporte", "categoria"]
    search_fields      = ["nombre"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsCoordinadorOAdmin()]
        return [EsLecturaPublica()]

    @extend_schema(summary="Equipos inscritos en el campeonato")
    @action(detail=True, methods=["get"], url_path="equipos")
    def equipos(self, request, pk=None):
        campeonato = self.get_object()
        equipos    = campeonato.equipos.filter(activo=True).prefetch_related("jugadores")
        serializer = EquipoSerializer(equipos, many=True, context={"request": request})
        return Response(serializer.data)

    @extend_schema(summary="Cambiar estado del campeonato")
    @action(detail=True, methods=["patch"], url_path="estado",
            permission_classes=[EsCoordinadorOAdmin])
    def cambiar_estado(self, request, pk=None):
        campeonato = self.get_object()
        nuevo      = request.data.get("estado")
        opciones   = [c[0] for c in Campeonato.Estado.choices]
        if nuevo not in opciones:
            return Response(
                {"error": f"Estado inválido. Opciones: {opciones}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        campeonato.estado = nuevo
        campeonato.save(update_fields=["estado"])
        return Response({"estado": nuevo, "mensaje": "Estado actualizado."})


@extend_schema(tags=["equipos"])
class EquipoViewSet(viewsets.ModelViewSet):
    """CU03 — Inscripción y gestión de equipos."""
    queryset = Equipo.objects.filter(activo=True).select_related(
        "campeonato", "delegado"
    ).prefetch_related("jugadores__usuario")
    serializer_class   = EquipoSerializer
    filterset_fields   = ["campeonato", "facultad"]
    search_fields      = ["nombre", "facultad"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsCoordinadorOAdmin()]
        return [EsLecturaPublica()]


@extend_schema(tags=["equipos"])
class FichaJugadorViewSet(viewsets.ModelViewSet):
    """CU06 — Ficha de jugadores por equipo."""
    queryset = FichaJugador.objects.filter(activo=True).select_related(
        "equipo", "usuario"
    )
    serializer_class   = FichaJugadorSerializer
    filterset_fields   = ["equipo", "posicion"]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsCoordinadorOAdmin()]
        return [IsAuthenticated()]
