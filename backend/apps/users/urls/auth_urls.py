"""
apps/users/urls/auth_urls.py
Rutas de autenticación JWT.
"""
from django.urls import path
from ..views.auth_views import (
    RegistroView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    CambioPasswordView,
)

urlpatterns = [
    path("registro/",         RegistroView.as_view(),      name="auth-registro"),
    path("login/",            LoginView.as_view(),          name="auth-login"),
    path("token/refresh/",    RefreshTokenView.as_view(),   name="auth-refresh"),
    path("logout/",           LogoutView.as_view(),         name="auth-logout"),
    path("cambio-password/",  CambioPasswordView.as_view(), name="auth-cambio-password"),
]
