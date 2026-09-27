"""
apps/users/views/auth_views.py
Vistas de autenticación: registro, login JWT, refresh, logout.
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample

from ..serializers import (
    UsuarioRegistroSerializer,
    TokenPersonalizadoSerializer,
    CambioPasswordSerializer,
)


@extend_schema(tags=["auth"])
class RegistroView(generics.CreateAPIView):
    """
    CU01 — Registro de nuevo usuario.
    Devuelve los tokens JWT al registrarse exitosamente.
    """
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generar tokens automáticamente al registrarse
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "mensaje":  "Usuario registrado exitosamente.",
                "usuario":  serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access":  str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["auth"])
class LoginView(TokenObtainPairView):
    """
    CU01 — Login. Devuelve access + refresh token con datos del usuario.
    """
    serializer_class = TokenPersonalizadoSerializer


@extend_schema(tags=["auth"])
class RefreshTokenView(TokenRefreshView):
    """Renueva el access token usando el refresh token."""


@extend_schema(tags=["auth"])
class LogoutView(APIView):
    """
    Cierre de sesión: invalida el refresh token (blacklist JWT).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"mensaje": "Sesión cerrada correctamente."},
                status=status.HTTP_200_OK,
            )
        except KeyError:
            return Response(
                {"error": "Se requiere el refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(tags=["auth"])
class CambioPasswordView(APIView):
    """
    CU02 — Cambio de contraseña del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CambioPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["password_actual"]):
            return Response(
                {"error": "La contraseña actual es incorrecta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["password_nuevo"])
        user.save()

        # Invalidar todos los tokens anteriores del usuario
        RefreshToken.for_user(user)

        return Response(
            {"mensaje": "Contraseña actualizada correctamente."},
            status=status.HTTP_200_OK,
        )
