"""
apps/deportes/models.py
Modelos: Deporte, Categoria, Campeonato, Equipo, FichaJugador.
Cubre CU03, CU04, CU05, CU06, CU09.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.users.models import Usuario


class Deporte(models.Model):
    """CU05 — Registro de deportes disponibles en la DUBSS."""

    nombre      = models.CharField(max_length=100, unique=True, verbose_name="nombre")
    descripcion = models.TextField(blank=True, verbose_name="descripción")
    imagen      = models.ImageField(upload_to="deportes/", blank=True, null=True)
    activo      = models.BooleanField(default=True)
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Deporte"
        verbose_name_plural = "Deportes"
        ordering            = ["nombre"]

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """CU04 — Categorías dentro de un deporte (Varones, Damas, Mixto, etc.)."""

    class Genero(models.TextChoices):
        VARONES = "VARONES", "Varones"
        DAMAS   = "DAMAS",   "Damas"
        MIXTO   = "MIXTO",   "Mixto"

    deporte     = models.ForeignKey(Deporte, on_delete=models.CASCADE,
                                    related_name="categorias")
    nombre      = models.CharField(max_length=100, verbose_name="nombre")
    genero      = models.CharField(max_length=10, choices=Genero.choices,
                                   default=Genero.VARONES)
    edad_min    = models.PositiveSmallIntegerField(null=True, blank=True,
                                                   verbose_name="edad mínima")
    edad_max    = models.PositiveSmallIntegerField(null=True, blank=True,
                                                   verbose_name="edad máxima")
    descripcion = models.TextField(blank=True)
    activa      = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Categoría"
        verbose_name_plural = "Categorías"
        unique_together     = ["deporte", "nombre", "genero"]
        ordering            = ["deporte", "nombre"]

    def __str__(self):
        return f"{self.deporte} — {self.nombre} ({self.genero})"


class Campeonato(models.Model):
    """CU09 — Gestión de campeonatos universitarios."""

    class Estado(models.TextChoices):
        PLANIFICACION = "PLANIFICACION", "En planificación"
        INSCRIPCIONES = "INSCRIPCIONES", "Inscripciones abiertas"
        EN_CURSO      = "EN_CURSO",      "En curso"
        FINALIZADO    = "FINALIZADO",    "Finalizado"
        CANCELADO     = "CANCELADO",     "Cancelado"

    class Formato(models.TextChoices):
        LIGA        = "LIGA",        "Liga (todos contra todos)"
        ELIMINACION = "ELIMINACION", "Eliminación directa"
        GRUPOS      = "GRUPOS",      "Fase de grupos + eliminación"

    nombre          = models.CharField(max_length=200, verbose_name="nombre")
    deporte         = models.ForeignKey(Deporte,   on_delete=models.PROTECT,
                                        related_name="campeonatos")
    categoria       = models.ForeignKey(Categoria, on_delete=models.PROTECT,
                                        related_name="campeonatos")
    estado          = models.CharField(max_length=20, choices=Estado.choices,
                                       default=Estado.PLANIFICACION)
    formato         = models.CharField(max_length=20, choices=Formato.choices,
                                       default=Formato.LIGA)
    fecha_inicio    = models.DateField(verbose_name="fecha de inicio")
    fecha_fin       = models.DateField(verbose_name="fecha de fin")
    max_equipos     = models.PositiveSmallIntegerField(default=8,
                                                        verbose_name="máximo de equipos")
    descripcion     = models.TextField(blank=True)
    imagen_banner   = models.ImageField(upload_to="campeonatos/", blank=True, null=True)
    creado_por      = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True,
                                        related_name="campeonatos_creados")
    creado_en       = models.DateTimeField(auto_now_add=True)
    actualizado_en  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Campeonato"
        verbose_name_plural = "Campeonatos"
        ordering            = ["-fecha_inicio"]

    def __str__(self):
        return f"{self.nombre} ({self.deporte})"

    @property
    def esta_activo(self):
        return self.estado == self.Estado.EN_CURSO


class Equipo(models.Model):
    """CU03 — Inscripción de equipos a un campeonato."""

    campeonato  = models.ForeignKey(Campeonato, on_delete=models.CASCADE,
                                    related_name="equipos")
    nombre      = models.CharField(max_length=150, verbose_name="nombre del equipo")
    facultad    = models.CharField(max_length=150, verbose_name="facultad representada")
    logo        = models.ImageField(upload_to="equipos/logos/", blank=True, null=True)
    delegado    = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True,
                                    related_name="equipos_delegado",
                                    verbose_name="delegado responsable")
    color_principal   = models.CharField(max_length=7, default="#000000",
                                         verbose_name="color principal (hex)")
    color_secundario  = models.CharField(max_length=7, default="#FFFFFF",
                                         verbose_name="color secundario (hex)")
    activo      = models.BooleanField(default=True)
    inscrito_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Equipo"
        verbose_name_plural = "Equipos"
        unique_together     = ["campeonato", "nombre"]
        ordering            = ["nombre"]

    def __str__(self):
        return f"{self.nombre} — {self.campeonato}"

    @property
    def cantidad_jugadores(self):
        return self.jugadores.filter(activo=True).count()


class FichaJugador(models.Model):
    """CU06 — Ficha de participante (jugador registrado en un equipo)."""

    class Posicion(models.TextChoices):
        # Genéricas — cada deporte puede tener las suyas
        TITULAR  = "TITULAR",  "Titular"
        SUPLENTE = "SUPLENTE", "Suplente"
        CAPITAN  = "CAPITAN",  "Capitán"

    equipo    = models.ForeignKey(Equipo,  on_delete=models.CASCADE,
                                  related_name="jugadores")
    usuario   = models.ForeignKey(Usuario, on_delete=models.CASCADE,
                                  related_name="fichas_jugador")
    numero_camiseta = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        verbose_name="número de camiseta",
    )
    posicion  = models.CharField(max_length=20, choices=Posicion.choices,
                                  default=Posicion.TITULAR)
    activo    = models.BooleanField(default=True)
    inscrito_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Ficha de Jugador"
        verbose_name_plural = "Fichas de Jugadores"
        unique_together     = [
            ["equipo", "usuario"],
            ["equipo", "numero_camiseta"],
        ]
        ordering = ["equipo", "numero_camiseta"]

    def __str__(self):
        return f"#{self.numero_camiseta} {self.usuario.nombre_completo} — {self.equipo}"
