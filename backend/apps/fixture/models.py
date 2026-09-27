"""
apps/fixture/models.py
CU08, CU10, CU11, CU12, CU13.
Modelos: Partido, Resultado, Incidencia, TablaPosiciones.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from apps.deportes.models import Campeonato, Equipo, FichaJugador
from apps.instalaciones.models import Cancha


class Partido(models.Model):
    """CU08 / CU10 — Partido generado por el fixture."""

    class Estado(models.TextChoices):
        PROGRAMADO  = "PROGRAMADO",  "Programado"
        EN_CURSO    = "EN_CURSO",    "En curso"
        FINALIZADO  = "FINALIZADO",  "Finalizado"
        SUSPENDIDO  = "SUSPENDIDO",  "Suspendido"
        POSTERGADO  = "POSTERGADO",  "Postergado"
        WALKOVER    = "WALKOVER",    "Walkover (W.O.)"

    campeonato      = models.ForeignKey(Campeonato, on_delete=models.CASCADE,
                                        related_name="partidos")
    equipo_local    = models.ForeignKey(Equipo, on_delete=models.PROTECT,
                                        related_name="partidos_local")
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.PROTECT,
                                         related_name="partidos_visitante")
    cancha          = models.ForeignKey(Cancha, on_delete=models.SET_NULL,
                                        null=True, related_name="partidos")
    fecha_hora      = models.DateTimeField(verbose_name="fecha y hora del partido")
    jornada         = models.PositiveSmallIntegerField(default=1,
                                                        verbose_name="jornada / fecha")
    fase            = models.CharField(max_length=50, default="Fase de grupos",
                                       verbose_name="fase del campeonato")
    estado          = models.CharField(max_length=20, choices=Estado.choices,
                                       default=Estado.PROGRAMADO)
    arbitro         = models.ForeignKey("users.Usuario", on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name="partidos_arbitrados")
    generado_por_ml = models.BooleanField(default=False,
                                          verbose_name="generado por ML")
    observaciones   = models.TextField(blank=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
    actualizado_en  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Partido"
        verbose_name_plural = "Partidos"
        ordering            = ["fecha_hora"]

    def __str__(self):
        return (
            f"{self.equipo_local} vs {self.equipo_visitante} "
            f"| {self.fecha_hora:%d/%m/%Y %H:%M}"
        )

    def clean(self):
        if self.equipo_local == self.equipo_visitante:
            raise ValidationError("El equipo local y visitante no pueden ser el mismo.")
        if (self.equipo_local.campeonato != self.campeonato or
                self.equipo_visitante.campeonato != self.campeonato):
            raise ValidationError("Ambos equipos deben pertenecer al mismo campeonato.")


class Resultado(models.Model):
    """CU11 — Resultado oficial de un partido."""

    partido         = models.OneToOneField(Partido, on_delete=models.CASCADE,
                                           related_name="resultado")
    goles_local     = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0)])
    goles_visitante = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0)])
    registrado_por  = models.ForeignKey("users.Usuario", on_delete=models.SET_NULL,
                                        null=True, related_name="resultados_registrados")
    registrado_en   = models.DateTimeField(auto_now_add=True)
    verificado      = models.BooleanField(default=False, verbose_name="verificado por admin")
    observaciones   = models.TextField(blank=True)

    class Meta:
        verbose_name        = "Resultado"
        verbose_name_plural = "Resultados"

    def __str__(self):
        return (
            f"{self.partido.equipo_local} {self.goles_local} - "
            f"{self.goles_visitante} {self.partido.equipo_visitante}"
        )

    @property
    def ganador(self):
        if self.goles_local > self.goles_visitante:
            return self.partido.equipo_local
        if self.goles_visitante > self.goles_local:
            return self.partido.equipo_visitante
        return None  # Empate

    @property
    def es_empate(self):
        return self.goles_local == self.goles_visitante


class Incidencia(models.Model):
    """CU12 — Incidencias durante un partido (tarjetas, lesiones, etc.)."""

    class Tipo(models.TextChoices):
        GOL             = "GOL",             "Gol"
        TARJETA_AMARILLA = "TARJETA_AMARILLA", "Tarjeta amarilla"
        TARJETA_ROJA    = "TARJETA_ROJA",    "Tarjeta roja"
        LESION          = "LESION",          "Lesión"
        SUSTITUCION     = "SUSTITUCION",     "Sustitución"
        OTRO            = "OTRO",            "Otro"

    partido    = models.ForeignKey(Partido, on_delete=models.CASCADE,
                                   related_name="incidencias")
    tipo       = models.CharField(max_length=20, choices=Tipo.choices)
    jugador    = models.ForeignKey(FichaJugador, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="incidencias")
    minuto     = models.PositiveSmallIntegerField(null=True, blank=True,
                                                   verbose_name="minuto del partido")
    descripcion = models.TextField(blank=True)
    registrado_por = models.ForeignKey("users.Usuario", on_delete=models.SET_NULL,
                                       null=True, related_name="incidencias_registradas")
    registrado_en  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Incidencia"
        verbose_name_plural = "Incidencias"
        ordering            = ["partido", "minuto"]

    def __str__(self):
        return f"{self.tipo} — {self.partido} min. {self.minuto}"


class TablaPosiciones(models.Model):
    """
    CU13 — Tabla de posiciones calculada por campeonato y equipo.
    Se actualiza automáticamente al registrar cada resultado.
    """
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE,
                                   related_name="tabla_posiciones")
    equipo     = models.ForeignKey(Equipo, on_delete=models.CASCADE,
                                   related_name="posicion_en_tabla")
    pj  = models.PositiveSmallIntegerField(default=0, verbose_name="partidos jugados")
    pg  = models.PositiveSmallIntegerField(default=0, verbose_name="partidos ganados")
    pe  = models.PositiveSmallIntegerField(default=0, verbose_name="partidos empatados")
    pp  = models.PositiveSmallIntegerField(default=0, verbose_name="partidos perdidos")
    gf  = models.PositiveSmallIntegerField(default=0, verbose_name="goles a favor")
    gc  = models.PositiveSmallIntegerField(default=0, verbose_name="goles en contra")
    puntos = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name        = "Tabla de Posiciones"
        verbose_name_plural = "Tabla de Posiciones"
        unique_together     = ["campeonato", "equipo"]
        ordering            = ["-puntos", "-gf"]

    def __str__(self):
        return f"{self.equipo} — {self.puntos} pts"

    @property
    def diferencia_goles(self):
        return self.gf - self.gc

    def actualizar_con_resultado(self, goles_favor, goles_contra):
        """Actualiza las estadísticas con el resultado de un partido."""
        self.pj += 1
        self.gf += goles_favor
        self.gc += goles_contra
        if goles_favor > goles_contra:
            self.pg += 1
            self.puntos += 3
        elif goles_favor == goles_contra:
            self.pe += 1
            self.puntos += 1
        else:
            self.pp += 1
        self.save()
