"""
apps/fixture/services/fixture_generator.py
Generación automática de fixture usando round-robin.
El módulo ML (apps.ml) puede sobreescribir el orden de partidos
mediante optimización de horarios.
"""
from itertools import combinations
from datetime import timedelta
from django.utils import timezone
from django.db import transaction

from apps.fixture.models import Partido, TablaPosiciones
from apps.deportes.models import Campeonato, Equipo
from apps.instalaciones.models import Cancha, BloqueoCancha


class FixtureGenerator:
    """
    Genera el fixture completo de un campeonato en formato liga
    (todos contra todos) usando el algoritmo Round Robin.

    Uso:
        gen = FixtureGenerator(campeonato_id=1)
        partidos = gen.generar()
    """

    DURACION_PARTIDO_MINUTOS = 90
    DESCANSO_ENTRE_PARTIDOS  = 30  # minutos entre partidos en misma cancha

    def __init__(self, campeonato_id: int, hora_inicio: str = "08:00",
                 dias_entre_jornadas: int = 7):
        self.campeonato = Campeonato.objects.get(pk=campeonato_id)
        self.hora_inicio = hora_inicio
        self.dias_entre_jornadas = dias_entre_jornadas

    def generar(self, usar_ml: bool = False) -> list[Partido]:
        """
        Genera y guarda los partidos del fixture.
        Si usar_ml=True, pasa los partidos al módulo ML para optimizar horarios.
        """
        equipos = list(
            Equipo.objects.filter(
                campeonato=self.campeonato,
                activo=True,
            ).order_by("id")
        )

        if len(equipos) < 2:
            raise ValueError("Se necesitan al menos 2 equipos para generar el fixture.")

        canchas = list(
            Cancha.objects.filter(
                deporte=self.campeonato.deporte,
                activa=True,
            )
        )
        if not canchas:
            raise ValueError("No hay canchas disponibles para este deporte.")

        # Eliminar fixture previo del campeonato si existe
        Partido.objects.filter(campeonato=self.campeonato).delete()

        jornadas = self._round_robin(equipos)
        partidos_creados = []

        with transaction.atomic():
            fecha_base = self.campeonato.fecha_inicio
            cancha_idx = 0

            for num_jornada, enfrentamientos in enumerate(jornadas, start=1):
                # Fecha de esta jornada
                fecha_jornada = fecha_base + timedelta(
                    days=(num_jornada - 1) * self.dias_entre_jornadas
                )
                hora_h, hora_m = map(int, self.hora_inicio.split(":"))
                from datetime import datetime as dt
                fecha_hora = dt(
                    fecha_jornada.year, fecha_jornada.month, fecha_jornada.day,
                    hora_h, hora_m, 0
                )

                for local, visitante in enfrentamientos:
                    cancha = canchas[cancha_idx % len(canchas)]
                    cancha_idx += 1

                    # Verificar que la cancha no esté bloqueada
                    while self._cancha_bloqueada(cancha, fecha_hora):
                        cancha_idx += 1
                        cancha = canchas[cancha_idx % len(canchas)]

                    partido = Partido.objects.create(
                        campeonato      = self.campeonato,
                        equipo_local    = local,
                        equipo_visitante = visitante,
                        cancha          = cancha,
                        fecha_hora      = fecha_hora,
                        jornada         = num_jornada,
                        fase            = "Liga",
                        generado_por_ml = usar_ml,
                    )
                    partidos_creados.append(partido)

                    # Siguiente partido en la misma cancha: +90min +30min descanso
                    fecha_hora = fecha_hora + timedelta(
                        minutes=self.DURACION_PARTIDO_MINUTOS + self.DESCANSO_ENTRE_PARTIDOS
                    )

            # Inicializar tabla de posiciones vacía para cada equipo
            for equipo in equipos:
                TablaPosiciones.objects.get_or_create(
                    campeonato=self.campeonato,
                    equipo=equipo,
                )

        if usar_ml and partidos_creados:
            # Hook para optimización ML (se implementa en apps.ml)
            try:
                from apps.ml.services.fixture_optimizer import FixtureOptimizer
                optimizer = FixtureOptimizer(self.campeonato)
                partidos_creados = optimizer.optimizar(partidos_creados)
            except ImportError:
                pass  # ML module not yet available

        return partidos_creados

    # ── Algoritmo interno ─────────────────────────────────────────────────────

    @staticmethod
    def _round_robin(equipos: list) -> list[list]:
        """
        Algoritmo Round Robin circular.
        Retorna una lista de jornadas, cada jornada es una lista de tuplas (local, visitante).
        Si el número de equipos es impar, se agrega un 'BYE' (equipo ficticio = None).
        """
        n = len(equipos)
        if n % 2 != 0:
            equipos = equipos + [None]  # BYE
            n += 1

        fijo    = equipos[0]
        rotativos = equipos[1:]
        jornadas  = []

        for ronda in range(n - 1):
            jornada = []
            circulo = [fijo] + rotativos

            for i in range(n // 2):
                local    = circulo[i]
                visitante = circulo[n - 1 - i]
                # Omitir si alguno es BYE
                if local is not None and visitante is not None:
                    # Alternar local/visitante cada dos rondas
                    if ronda % 2 == 0:
                        jornada.append((local, visitante))
                    else:
                        jornada.append((visitante, local))

            jornadas.append(jornada)
            # Rotar la lista (el primero queda fijo)
            rotativos = [rotativos[-1]] + rotativos[:-1]

        return jornadas

    @staticmethod
    def _cancha_bloqueada(cancha: Cancha, fecha_hora) -> bool:
        """Verifica si la cancha tiene un bloqueo en la fecha/hora dada."""
        fin_partido = fecha_hora + timedelta(minutes=90)
        return BloqueoCancha.objects.filter(
            cancha=cancha,
            fecha_inicio__lt=fin_partido,
            fecha_fin__gt=fecha_hora,
        ).exists()
