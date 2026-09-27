"""
apps/ml/models.py
CU14–CU16, CU18, CU20 — Predicciones ML y bitácora del sistema.
"""
from django.db import models
from apps.fixture.models import Partido
from apps.deportes.models import Campeonato, Equipo


class PrediccionPartido(models.Model):
    """CU16 — Predicción de resultado de un partido generada por el modelo ML."""

    partido             = models.OneToOneField(Partido, on_delete=models.CASCADE,
                                               related_name="prediccion")
    prob_victoria_local = models.FloatField(verbose_name="prob. victoria local (0-1)")
    prob_empate         = models.FloatField(verbose_name="prob. empate (0-1)")
    prob_victoria_visit = models.FloatField(verbose_name="prob. victoria visitante (0-1)")
    goles_local_pred    = models.FloatField(verbose_name="goles local predichos")
    goles_visit_pred    = models.FloatField(verbose_name="goles visitante predichos")
    confianza           = models.FloatField(verbose_name="confianza del modelo (0-1)")
    modelo_version      = models.CharField(max_length=50, default="v1.0")
    generado_en         = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Predicción de Partido"
        verbose_name_plural = "Predicciones de Partidos"

    def __str__(self):
        return f"Predicción: {self.partido}"


class PrediccionAsistencia(models.Model):
    """CU20 — Predicción de asistencia de espectadores a un partido."""

    partido             = models.OneToOneField(Partido, on_delete=models.CASCADE,
                                               related_name="pred_asistencia")
    asistencia_predicha = models.PositiveIntegerField(verbose_name="asistencia predicha")
    rango_min           = models.PositiveIntegerField()
    rango_max           = models.PositiveIntegerField()
    factores            = models.JSONField(default=dict,
                                           verbose_name="factores considerados")
    generado_en         = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Predicción de Asistencia"
        verbose_name_plural = "Predicciones de Asistencia"


class RiesgoClimatico(models.Model):
    """CU15 — Pronóstico de riesgo climático para un partido."""

    class NivelRiesgo(models.TextChoices):
        BAJO   = "BAJO",   "Bajo"
        MEDIO  = "MEDIO",  "Medio"
        ALTO   = "ALTO",   "Alto"
        CRITICO = "CRITICO", "Crítico — considerar suspensión"

    partido         = models.ForeignKey(Partido, on_delete=models.CASCADE,
                                        related_name="riesgos_climaticos")
    nivel_riesgo    = models.CharField(max_length=10, choices=NivelRiesgo.choices)
    temperatura     = models.FloatField(null=True, blank=True, verbose_name="temperatura (°C)")
    precipitacion   = models.FloatField(null=True, blank=True, verbose_name="precipitación (mm)")
    viento          = models.FloatField(null=True, blank=True, verbose_name="viento (km/h)")
    descripcion     = models.TextField(blank=True)
    recomendacion   = models.TextField(blank=True)
    fuente_api      = models.CharField(max_length=50, default="OpenWeatherMap")
    consultado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Riesgo Climático"
        verbose_name_plural = "Riesgos Climáticos"
        ordering            = ["-consultado_en"]


class Bitacora(models.Model):
    """CU19 — Bitácora de acciones del sistema para auditoría."""

    class Accion(models.TextChoices):
        CREAR    = "CREAR",    "Crear"
        EDITAR   = "EDITAR",   "Editar"
        ELIMINAR = "ELIMINAR", "Eliminar"
        LOGIN    = "LOGIN",    "Inicio de sesión"
        LOGOUT   = "LOGOUT",   "Cierre de sesión"
        EXPORTAR = "EXPORTAR", "Exportar reporte"
        ML_PRED  = "ML_PRED",  "Predicción ML generada"

    usuario     = models.ForeignKey("users.Usuario", on_delete=models.SET_NULL,
                                    null=True, related_name="bitacora")
    accion      = models.CharField(max_length=20, choices=Accion.choices)
    modulo      = models.CharField(max_length=50, verbose_name="módulo del sistema")
    descripcion = models.TextField(verbose_name="descripción de la acción")
    objeto_id   = models.PositiveIntegerField(null=True, blank=True,
                                              verbose_name="ID del objeto afectado")
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Bitácora"
        verbose_name_plural = "Bitácora"
        ordering            = ["-timestamp"]

    def __str__(self):
        return f"[{self.timestamp:%d/%m/%Y %H:%M}] {self.usuario} — {self.accion} en {self.modulo}"
