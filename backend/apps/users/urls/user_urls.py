"""
apps/users/urls/user_urls.py
Rutas de gestión de usuarios.
"""
from django.urls import path
from ..views.user_views import (
    MiPerfilView,
    ListaUsuariosView,
    DetalleUsuarioView,
    ActualizarFCMTokenView,
)

urlpatterns = [
    path("perfil/",          MiPerfilView.as_view(),        name="usuario-perfil"),
    path("",                 ListaUsuariosView.as_view(),    name="usuario-lista"),
    path("<int:pk>/",        DetalleUsuarioView.as_view(),   name="usuario-detalle"),
    path("fcm-token/",       ActualizarFCMTokenView.as_view(), name="usuario-fcm-token"),
]
