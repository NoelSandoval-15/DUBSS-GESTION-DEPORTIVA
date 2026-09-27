"""
apps/users/permissions.py
Permisos basados en roles del sistema DUBSS.
"""
from rest_framework.permissions import BasePermission
from .models import Usuario


class EsAdminDUBSS(BasePermission):
    """Solo el administrador DUBSS puede acceder."""
    message = "Requiere rol de Administrador DUBSS."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == Usuario.Rol.ADMIN_DUBSS
        )


class EsCoordinadorOAdmin(BasePermission):
    """Coordinador de facultad o administrador."""
    message = "Requiere rol de Coordinador o Administrador DUBSS."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in (
                Usuario.Rol.ADMIN_DUBSS,
                Usuario.Rol.COORDINADOR,
            )
        )


class EsArbitroOAdmin(BasePermission):
    """Árbitro o administrador (para registro de resultados)."""
    message = "Requiere rol de Árbitro o Administrador DUBSS."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in (
                Usuario.Rol.ADMIN_DUBSS,
                Usuario.Rol.ARBITRO,
            )
        )


class EsDeportistaPropioOAdmin(BasePermission):
    """Un deportista solo puede ver/editar su propio perfil; admin puede todo."""

    def has_object_permission(self, request, view, obj):
        if request.user.rol == Usuario.Rol.ADMIN_DUBSS:
            return True
        return obj == request.user


class EsLecturaPublica(BasePermission):
    """GET permitido para todos; escritura solo para autenticados."""

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user and request.user.is_authenticated
