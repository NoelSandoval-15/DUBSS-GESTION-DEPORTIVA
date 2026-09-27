from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ["email", "nombre", "apellido", "rol", "facultad", "is_active"]
    list_filter   = ["rol", "facultad", "is_active"]
    search_fields = ["email", "nombre", "apellido", "ci"]
    ordering      = ["apellido", "nombre"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información personal", {"fields": ("nombre", "apellido", "ci", "telefono", "foto_perfil")}),
        ("Rol institucional",    {"fields": ("rol", "facultad")}),
        ("Notificaciones",       {"fields": ("fcm_token",)}),
        ("Permisos",             {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas",               {"fields": ("fecha_registro", "ultimo_acceso")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "nombre", "apellido", "rol", "password1", "password2"),
        }),
    )
    readonly_fields = ["fecha_registro", "ultimo_acceso"]
