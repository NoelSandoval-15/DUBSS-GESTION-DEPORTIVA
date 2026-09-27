from rest_framework import serializers
from apps.deportes.serializers import EquipoResumenSerializer
from apps.instalaciones.serializers import CanchaSerializer
from apps.users.serializers import UsuarioResumenSerializer
from .models import Partido, Resultado, Incidencia, TablaPosiciones


class ResultadoSerializer(serializers.ModelSerializer):
    ganador       = serializers.SerializerMethodField()
    es_empate     = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Resultado
        fields = ["id", "partido", "goles_local", "goles_visitante",
                  "ganador", "es_empate", "registrado_por",
                  "registrado_en", "verificado", "observaciones"]
        read_only_fields = ["id", "registrado_por", "registrado_en"]

    def get_ganador(self, obj):
        g = obj.ganador
        return {"id": g.id, "nombre": g.nombre} if g else None

    def create(self, validated_data):
        validated_data["registrado_por"] = self.context["request"].user
        return super().create(validated_data)


class IncidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Incidencia
        fields = ["id", "partido", "tipo", "jugador", "minuto",
                  "descripcion", "registrado_por", "registrado_en"]
        read_only_fields = ["id", "registrado_por", "registrado_en"]

    def create(self, validated_data):
        validated_data["registrado_por"] = self.context["request"].user
        return super().create(validated_data)


class PartidoSerializer(serializers.ModelSerializer):
    equipo_local_detalle    = EquipoResumenSerializer(source="equipo_local",    read_only=True)
    equipo_visitante_detalle = EquipoResumenSerializer(source="equipo_visitante", read_only=True)
    cancha_detalle          = CanchaSerializer(source="cancha",                 read_only=True)
    arbitro_detalle         = UsuarioResumenSerializer(source="arbitro",        read_only=True)
    resultado               = ResultadoSerializer(read_only=True)
    incidencias             = IncidenciaSerializer(many=True, read_only=True)

    class Meta:
        model  = Partido
        fields = [
            "id", "campeonato", "jornada", "fase",
            "equipo_local",     "equipo_local_detalle",
            "equipo_visitante", "equipo_visitante_detalle",
            "cancha",           "cancha_detalle",
            "fecha_hora", "estado", "generado_por_ml",
            "arbitro",    "arbitro_detalle",
            "resultado", "incidencias",
            "observaciones", "creado_en", "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]


class PartidoResumenSerializer(serializers.ModelSerializer):
    """Compacto para calendarios y listados."""
    local    = serializers.CharField(source="equipo_local.nombre")
    visitante = serializers.CharField(source="equipo_visitante.nombre")
    cancha   = serializers.CharField(source="cancha.nombre", default="")

    class Meta:
        model  = Partido
        fields = ["id", "jornada", "fase", "local", "visitante",
                  "cancha", "fecha_hora", "estado"]


class TablaPosicionesSerializer(serializers.ModelSerializer):
    equipo_detalle     = EquipoResumenSerializer(source="equipo", read_only=True)
    diferencia_goles   = serializers.IntegerField(read_only=True)

    class Meta:
        model  = TablaPosiciones
        fields = ["id", "campeonato", "equipo", "equipo_detalle",
                  "pj", "pg", "pe", "pp", "gf", "gc",
                  "diferencia_goles", "puntos"]
        read_only_fields = fields
