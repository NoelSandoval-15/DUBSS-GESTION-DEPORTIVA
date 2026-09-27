from django.contrib import admin
from .models import PrediccionPartido, PrediccionAsistencia, RiesgoClimatico, Bitacora


@admin.register(PrediccionPartido)
class PrediccionAdmin(admin.ModelAdmin):
    list_display  = ["partido", "prob_victoria_local", "prob_empate",
                     "prob_victoria_visit", "confianza", "modelo_version"]
    list_filter   = ["modelo_version"]


@admin.register(RiesgoClimatico)
class RiesgoClimaticoAdmin(admin.ModelAdmin):
    list_display  = ["partido", "nivel_riesgo", "temperatura",
                     "precipitacion", "consultado_en"]
    list_filter   = ["nivel_riesgo"]


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display  = ["timestamp", "usuario", "accion", "modulo", "objeto_id"]
    list_filter   = ["accion", "modulo"]
    search_fields = ["descripcion", "usuario__email"]
    readonly_fields = ["timestamp", "ip_address"]
    date_hierarchy  = "timestamp"
