"""
apps/users/serializers.py
Serializers para registro, login y gestión de usuarios.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import Usuario


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Registro de nuevo usuario con validación de contraseña."""
    password  = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmar contraseña")

    class Meta:
        model  = Usuario
        fields = [
            "email", "nombre", "apellido", "ci",
            "telefono", "rol", "facultad",
            "password", "password2",
        ]
        extra_kwargs = {
            "rol": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer completo de usuario (lectura y edición de perfil)."""
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model  = Usuario
        fields = [
            "id", "email", "nombre", "apellido", "nombre_completo",
            "ci", "telefono", "foto_perfil",
            "rol", "facultad",
            "is_active", "fecha_registro", "ultimo_acceso",
        ]
        read_only_fields = ["id", "email", "is_active", "fecha_registro", "ultimo_acceso"]


class UsuarioResumenSerializer(serializers.ModelSerializer):
    """Serializer compacto para listas y relaciones."""
    class Meta:
        model  = Usuario
        fields = ["id", "nombre_completo", "email", "rol", "facultad"]


class CambioPasswordSerializer(serializers.Serializer):
    """Cambio de contraseña autenticado."""
    password_actual = serializers.CharField(required=True)
    password_nuevo  = serializers.CharField(required=True, validators=[validate_password])
    password_nuevo2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["password_nuevo"] != attrs["password_nuevo2"]:
            raise serializers.ValidationError({"password_nuevo": "Las contraseñas no coinciden."})
        return attrs


class TokenPersonalizadoSerializer(TokenObtainPairSerializer):
    """JWT con datos extra del usuario en el payload."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claims personalizados incluidos en el token
        token["nombre_completo"] = user.nombre_completo
        token["email"]           = user.email
        token["rol"]             = user.rol
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # También retorna info del usuario en el cuerpo de la respuesta
        data["usuario"] = UsuarioSerializer(self.user).data
        return data
