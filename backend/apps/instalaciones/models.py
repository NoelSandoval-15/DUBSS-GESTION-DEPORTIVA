"""
apps/instalaciones/models.py
CU07 — Registro y gestión de instalaciones deportivas (canchas).
"""
from django.db import models
from django.core.exceptions import ValidationError


class Instalacion(models.Model):
    """Instalación deportiva (pabellón, estadio, etc.)."""

    nombre      = models.CharField(max_length=150, unique=True, verbose_name="nombre")
    ubicacion   = models.CharField(max_length=255, verbose_name="ubicación / dirección")
    latitud     = models.DecimalField(max_digits=10, decimal_places=7,
                                      null=True, blank=True)
    longitud    = models.DecimalField(max_digits=10, decimal_places=7,
                                      null=True, blank=True)
    descripcion = models.TextField(blank=True)
    imagen      = models.ImageField(upload_to="instalaciones/", blank=True, null=True)
    activa      = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Instalación"
        verbose_name_plural = "Instalaciones"
        ordering            = ["nombre"]

    def __str__(self):
        return self.nombre


class Cancha(models.Model):
    """Cancha específica dentro de una instalación."""

    class TipoSuperficie(models.TextChoices):
        CESPED_NATURAL   = "CESPED_NATURAL",   "Césped natural"
        CESPED_SINTETICO = "CESPED_SINTETICO",  "Césped sintético"
        PARQUET          = "PARQUET",           "Parquet"
        CEMENTO          = "CEMENTO",           "Cemento"
        TIERRA           = "TIERRA",            "Tierra"

    instalacion = models.ForeignKey(Instalacion, on_delete=models.CASCADE,
                                    related_name="canchas")
    nombre      = models.CharField(max_length=100, verbose_name="nombre / número")
    deporte     = models.ForeignKey("deportes.Deporte", on_delete=models.PROTECT,
                                    related_name="canchas")
    superficie  = models.CharField(max_length=20, choices=TipoSuperficie.choices,
                                   blank=True)
    capacidad   = models.PositiveSmallIntegerField(default=0,
                                                    verbose_name="capacidad de espectadores")
    techada     = models.BooleanField(default=False, verbose_name="¿techada?")
    activa      = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name        = "Cancha"
        verbose_name_plural = "Canchas"
        unique_together     = ["instalacion", "nombre"]
        ordering            = ["instalacion", "nombre"]

    def __str__(self):
        return f"{self.nombre} — {self.instalacion}"


class BloqueoCancha(models.Model):
    """
    Bloqueo de una cancha por mantenimiento, evento externo, etc.
    El sistema de fixture respeta estos bloqueos al programar partidos.
    """
    cancha      = models.ForeignKey(Cancha, on_delete=models.CASCADE,
                                    related_name="bloqueos")
    fecha_inicio = models.DateTimeField(verbose_name="inicio del bloqueo")
    fecha_fin    = models.DateTimeField(verbose_name="fin del bloqueo")
    motivo       = models.CharField(max_length=255, verbose_name="motivo")
    creado_por   = models.ForeignKey("users.Usuario", on_delete=models.SET_NULL,
                                     null=True, related_name="bloqueos_creados")
    creado_en    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Bloqueo de Cancha"
        verbose_name_plural = "Bloqueos de Canchas"
        ordering            = ["fecha_inicio"]

    def __str__(self):
        return f"Bloqueo {self.cancha} | {self.fecha_inicio:%d/%m/%Y %H:%M}"

    def clean(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
