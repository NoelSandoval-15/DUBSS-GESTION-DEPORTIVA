"""
apps/users/views/user_views.py
Vistas CRUD de usuarios.
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from django.utils import timezone

from ..models import Usuario
from ..serializers import UsuarioSerializer, UsuarioResumenSerializer
from ..permissions import EsAdminDUBSS, EsDeportistaPropioOAdmin


@extend_schema(tags=["usuarios"])
class MiPerfilView(generics.RetrieveUpdateAPIView):
    """CU02 — Ver y actualizar el perfil del usuario autenticado."""
    serializer_class   = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def get_object(self):
        # Actualizar último acceso al consultar el perfil
        user = self.request.user
        user.ultimo_acceso = timezone.now()
        user.save(update_fields=["ultimo_acceso"])
        return user


@extend_schema(tags=["usuarios"])
class ListaUsuariosView(generics.ListAPIView):
    """Lista todos los usuarios — solo Admin DUBSS."""
    serializer_class   = UsuarioSerializer
    permission_classes = [EsAdminDUBSS]
    queryset           = Usuario.objects.all().order_by("apellido", "nombre")
    filterset_fields   = ["rol", "facultad", "is_active"]
    search_fields      = ["email", "nombre", "apellido", "ci"]


@extend_schema(tags=["usuarios"])
class DetalleUsuarioView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, edición y baja de un usuario — Admin DUBSS."""
    serializer_class   = UsuarioSerializer
    permission_classes = [EsAdminDUBSS]
    queryset           = Usuario.objects.all()

    def destroy(self, request, *args, **kwargs):
        # Baja lógica, no eliminación física
        usuario = self.get_object()
        usuario.is_active = False
        usuario.save(update_fields=["is_active"])
        return Response(
            {"mensaje": f"Usuario {usuario.nombre_completo} dado de baja."},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["usuarios"])
class ActualizarFCMTokenView(APIView):
    """Actualiza el token FCM para notificaciones push del usuario."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("fcm_token", "").strip()
        if not token:
            return Response(
                {"error": "fcm_token es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.fcm_token = token
        request.user.save(update_fields=["fcm_token"])
        return Response({"mensaje": "Token FCM actualizado."})
