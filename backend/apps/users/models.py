"""
apps/users/models.py
Modelo de usuario personalizado para el sistema DUBSS.
Roles: ADMIN_DUBSS, COORDINADOR, ARBITRO, DEPORTISTA, PUBLICO
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff",     True)
        extra_fields.setdefault("is_superuser",  True)
        extra_fields.setdefault("rol",           "ADMIN_DUBSS")
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Usuario del sistema DUBSS.
    Reemplaza al User de Django para manejar roles institucionales.
    """

    class Rol(models.TextChoices):
        ADMIN_DUBSS   = "ADMIN_DUBSS",   "Administrador DUBSS"
        COORDINADOR   = "COORDINADOR",   "Coordinador de Facultad"
        ARBITRO       = "ARBITRO",       "Árbitro"
        DEPORTISTA    = "DEPORTISTA",    "Deportista"
        PUBLICO       = "PUBLICO",       "Público General"

    # ── Campos de identidad ──────────────────────────────────────────────────
    email           = models.EmailField(unique=True, verbose_name="correo electrónico")
    nombre          = models.CharField(max_length=100, verbose_name="nombre")
    apellido        = models.CharField(max_length=100, verbose_name="apellido")
    ci              = models.CharField(max_length=20, unique=True, blank=True, null=True,
                                       verbose_name="cédula de identidad")
    telefono        = models.CharField(max_length=20, blank=True, verbose_name="teléfono")
    foto_perfil     = models.ImageField(upload_to="usuarios/fotos/", blank=True, null=True,
                                        verbose_name="foto de perfil")

    # ── Rol institucional ────────────────────────────────────────────────────
    rol             = models.CharField(max_length=20, choices=Rol.choices,
                                       default=Rol.DEPORTISTA, verbose_name="rol")
    facultad        = models.CharField(max_length=150, blank=True, verbose_name="facultad")

    # ── Estado ───────────────────────────────────────────────────────────────
    is_active       = models.BooleanField(default=True,  verbose_name="activo")
    is_staff        = models.BooleanField(default=False, verbose_name="staff")

    # ── Auditoría ────────────────────────────────────────────────────────────
    fecha_registro  = models.DateTimeField(default=timezone.now, verbose_name="fecha de registro")
    ultimo_acceso   = models.DateTimeField(null=True, blank=True, verbose_name="último acceso")

    # ── Notificaciones ───────────────────────────────────────────────────────
    fcm_token       = models.CharField(max_length=255, blank=True,
                                       verbose_name="token FCM (push notifications)")

    objects = UsuarioManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["nombre", "apellido"]

    class Meta:
        verbose_name        = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering            = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.nombre} {self.apellido} <{self.email}>"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    # ── Helpers de roles ─────────────────────────────────────────────────────
    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN_DUBSS

    @property
    def es_coordinador(self):
        return self.rol in (self.Rol.ADMIN_DUBSS, self.Rol.COORDINADOR)

    @property
    def es_arbitro(self):
        return self.rol == self.Rol.ARBITRO
