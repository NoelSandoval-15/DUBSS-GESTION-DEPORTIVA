"""
apps/deportes/serializers.py
Serializers para Deporte, Categoria, Campeonato, Equipo, FichaJugador.
"""
from rest_framework import serializers
from apps.users.serializers import UsuarioResumenSerializer
from .models import Deporte, Categoria, Campeonato, Equipo, FichaJugador


class DeporteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Deporte
        fields = ["id", "nombre", "descripcion", "imagen", "activo", "creado_en"]
        read_only_fields = ["id", "creado_en"]


class CategoriaSerializer(serializers.ModelSerializer):
    deporte_nombre = serializers.CharField(source="deporte.nombre", read_only=True)

    class Meta:
        model  = Categoria
        fields = ["id", "deporte", "deporte_nombre", "nombre", "genero",
                  "edad_min", "edad_max", "descripcion", "activa"]
        read_only_fields = ["id"]


class CampeonatoSerializer(serializers.ModelSerializer):
    deporte_detalle  = DeporteSerializer(source="deporte",   read_only=True)
    categoria_detalle = CategoriaSerializer(source="categoria", read_only=True)
    creado_por_detalle = UsuarioResumenSerializer(source="creado_por", read_only=True)
    total_equipos    = serializers.SerializerMethodField()

    class Meta:
        model  = Campeonato
        fields = [
            "id", "nombre",
            "deporte", "deporte_detalle",
            "categoria", "categoria_detalle",
            "estado", "formato",
            "fecha_inicio", "fecha_fin", "max_equipos", "total_equipos",
            "descripcion", "imagen_banner",
            "creado_por", "creado_por_detalle",
            "creado_en", "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en", "creado_por"]

    def get_total_equipos(self, obj):
        return obj.equipos.filter(activo=True).count()

    def create(self, validated_data):
        validated_data["creado_por"] = self.context["request"].user
        return super().create(validated_data)


class FichaJugadorSerializer(serializers.ModelSerializer):
    usuario_detalle = UsuarioResumenSerializer(source="usuario", read_only=True)

    class Meta:
        model  = FichaJugador
        fields = ["id", "equipo", "usuario", "usuario_detalle",
                  "numero_camiseta", "posicion", "activo", "inscrito_en"]
        read_only_fields = ["id", "inscrito_en"]


class EquipoSerializer(serializers.ModelSerializer):
    delegado_detalle  = UsuarioResumenSerializer(source="delegado", read_only=True)
    jugadores         = FichaJugadorSerializer(many=True, read_only=True)
    cantidad_jugadores = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Equipo
        fields = [
            "id", "campeonato", "nombre", "facultad",
            "logo", "delegado", "delegado_detalle",
            "color_principal", "color_secundario",
            "activo", "inscrito_en",
            "jugadores", "cantidad_jugadores",
        ]
        read_only_fields = ["id", "inscrito_en"]


class EquipoResumenSerializer(serializers.ModelSerializer):
    """Serializer compacto para usar en fixture/partidos."""
    class Meta:
        model  = Equipo
        fields = ["id", "nombre", "facultad", "logo", "color_principal"]
