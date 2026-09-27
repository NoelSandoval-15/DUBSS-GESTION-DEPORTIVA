"""
apps/users/tests/test_auth.py
Tests de autenticación y registro de usuarios.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import Usuario


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def usuario_data():
    return {
        "email":     "test@uagrm.edu.bo",
        "nombre":    "Juan",
        "apellido":  "Pérez",
        "password":  "TestPass123!",
        "password2": "TestPass123!",
        "rol":       "DEPORTISTA",
    }


@pytest.fixture
def usuario_creado(db, usuario_data):
    return Usuario.objects.create_user(
        email    = usuario_data["email"],
        password = usuario_data["password"],
        nombre   = usuario_data["nombre"],
        apellido = usuario_data["apellido"],
    )


# ─── Tests de registro ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRegistro:

    def test_registro_exitoso(self, client, usuario_data):
        url = reverse("auth-registro")
        response = client.post(url, usuario_data, format="json")
        assert response.status_code == 201
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert Usuario.objects.filter(email=usuario_data["email"]).exists()

    def test_registro_passwords_no_coinciden(self, client, usuario_data):
        usuario_data["password2"] = "OtraPassword123!"
        url = reverse("auth-registro")
        response = client.post(url, usuario_data, format="json")
        assert response.status_code == 400
        assert "password" in response.data

    def test_registro_email_duplicado(self, client, usuario_data, usuario_creado):
        url = reverse("auth-registro")
        response = client.post(url, usuario_data, format="json")
        assert response.status_code == 400


# ─── Tests de login ───────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestLogin:

    def test_login_exitoso(self, client, usuario_creado):
        url = reverse("auth-login")
        response = client.post(url, {
            "email":    usuario_creado.email,
            "password": "TestPass123!",
        }, format="json")
        assert response.status_code == 200
        assert "access"  in response.data
        assert "refresh" in response.data
        assert "usuario" in response.data
        assert response.data["usuario"]["rol"] == "DEPORTISTA"

    def test_login_credenciales_incorrectas(self, client, usuario_creado):
        url = reverse("auth-login")
        response = client.post(url, {
            "email":    usuario_creado.email,
            "password": "WrongPassword",
        }, format="json")
        assert response.status_code == 401

    def test_login_usuario_inactivo(self, client, usuario_creado):
        usuario_creado.is_active = False
        usuario_creado.save()
        url = reverse("auth-login")
        response = client.post(url, {
            "email":    usuario_creado.email,
            "password": "TestPass123!",
        }, format="json")
        assert response.status_code == 401


# ─── Tests de perfil ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPerfil:

    def test_obtener_perfil_autenticado(self, client, usuario_creado):
        client.force_authenticate(user=usuario_creado)
        url = reverse("usuario-perfil")
        response = client.get(url)
        assert response.status_code == 200
        assert response.data["email"] == usuario_creado.email

    def test_obtener_perfil_sin_autenticar(self, client):
        url = reverse("usuario-perfil")
        response = client.get(url)
        assert response.status_code == 401
