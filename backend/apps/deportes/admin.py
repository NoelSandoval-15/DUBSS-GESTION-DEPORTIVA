from django.contrib import admin
from .models import Deporte, Categoria, Campeonato, Equipo, FichaJugador


@admin.register(Deporte)
class DeporteAdmin(admin.ModelAdmin):
    list_display  = ["nombre", "activo", "creado_en"]
    list_filter   = ["activo"]
    search_fields = ["nombre"]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display  = ["nombre", "deporte", "genero", "activa"]
    list_filter   = ["deporte", "genero", "activa"]


@admin.register(Campeonato)
class CampeonatoAdmin(admin.ModelAdmin):
    list_display  = ["nombre", "deporte", "categoria", "estado", "fecha_inicio", "fecha_fin"]
    list_filter   = ["estado", "deporte", "formato"]
    search_fields = ["nombre"]
    date_hierarchy = "fecha_inicio"


class FichaJugadorInline(admin.TabularInline):
    model = FichaJugador
    extra = 0
    fields = ["usuario", "numero_camiseta", "posicion", "activo"]


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display  = ["nombre", "campeonato", "facultad", "activo"]
    list_filter   = ["campeonato", "activo"]
    search_fields = ["nombre", "facultad"]
    inlines       = [FichaJugadorInline]


@admin.register(FichaJugador)
class FichaJugadorAdmin(admin.ModelAdmin):
    list_display  = ["usuario", "equipo", "numero_camiseta", "posicion", "activo"]
    list_filter   = ["posicion", "activo"]
    search_fields = ["usuario__nombre", "usuario__apellido"]
