from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.users.permissions import EsAdminDUBSS, EsLecturaPublica
from .models import Instalacion, Cancha, BloqueoCancha
from .serializers import InstalacionSerializer, CanchaSerializer, BloqueoSerializer


@extend_schema(tags=["instalaciones"])
class InstalacionViewSet(viewsets.ModelViewSet):
    """CU07 — Gestión de instalaciones deportivas."""
    queryset           = Instalacion.objects.filter(activa=True)
    serializer_class   = InstalacionSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsAdminDUBSS()]
        return [EsLecturaPublica()]

    @extend_schema(summary="Canchas de esta instalación")
    @action(detail=True, methods=["get"])
    def canchas(self, request, pk=None):
        instalacion = self.get_object()
        qs = instalacion.canchas.filter(activa=True)
        return Response(CanchaSerializer(qs, many=True).data)


@extend_schema(tags=["instalaciones"])
class CanchaViewSet(viewsets.ModelViewSet):
    """CU07 — Gestión de canchas."""
    queryset         = Cancha.objects.filter(activa=True).select_related("instalacion", "deporte")
    serializer_class = CanchaSerializer
    filterset_fields = ["instalacion", "deporte", "techada"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsAdminDUBSS()]
        return [EsLecturaPublica()]


@extend_schema(tags=["instalaciones"])
class BloqueoViewSet(viewsets.ModelViewSet):
    """Bloqueos de canchas por mantenimiento o eventos."""
    queryset           = BloqueoCancha.objects.select_related("cancha", "creado_por")
    serializer_class   = BloqueoSerializer
    filterset_fields   = ["cancha"]
    permission_classes = [EsAdminDUBSS]
