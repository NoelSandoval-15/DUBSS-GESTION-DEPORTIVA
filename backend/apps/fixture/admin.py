from django.contrib import admin
from .models import Partido, Resultado, Incidencia, TablaPosiciones


class ResultadoInline(admin.StackedInline):
    model  = Resultado
    extra  = 0
    fields = ["goles_local", "goles_visitante", "verificado", "observaciones"]


class IncidenciaInline(admin.TabularInline):
    model  = Incidencia
    extra  = 0
    fields = ["tipo", "jugador", "minuto", "descripcion"]


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display  = ["__str__", "campeonato", "jornada", "estado", "cancha"]
    list_filter   = ["campeonato", "estado", "jornada"]
    search_fields = ["equipo_local__nombre", "equipo_visitante__nombre"]
    date_hierarchy = "fecha_hora"
    inlines        = [ResultadoInline, IncidenciaInline]


@admin.register(TablaPosiciones)
class TablaPosicionesAdmin(admin.ModelAdmin):
    list_display = ["equipo", "campeonato", "pj", "pg", "pe", "pp", "gf", "gc", "puntos"]
    list_filter  = ["campeonato"]
    ordering     = ["-puntos"]
