"""
apps/ml/serializers.py
Serializers para predicciones, riesgos climáticos y bitácora.
"""
from rest_framework import serializers
from apps.users.serializers import UsuarioResumenSerializer
from .models import PrediccionPartido, PrediccionAsistencia, RiesgoClimatico, Bitacora


class PrediccionPartidoSerializer(serializers.ModelSerializer):
    resultado_probable = serializers.SerializerMethodField()

    class Meta:
        model  = PrediccionPartido
        fields = [
            "id", "partido",
            "prob_victoria_local", "prob_empate", "prob_victoria_visit",
            "goles_local_pred", "goles_visit_pred",
            "confianza", "modelo_version",
            "resultado_probable", "generado_en",
        ]
        read_only_fields = fields

    def get_resultado_probable(self, obj):
        probs = {
            "local":    obj.prob_victoria_local,
            "empate":   obj.prob_empate,
            "visitante": obj.prob_victoria_visit,
        }
        return max(probs, key=probs.get)


class PrediccionAsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PrediccionAsistencia
        fields = ["id", "partido", "asistencia_predicha",
                  "rango_min", "rango_max", "factores", "generado_en"]
        read_only_fields = fields


class RiesgoClimaticoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RiesgoClimatico
        fields = ["id", "partido", "nivel_riesgo", "temperatura",
                  "precipitacion", "viento", "descripcion",
                  "recomendacion", "fuente_api", "consultado_en"]
        read_only_fields = fields


class BitacoraSerializer(serializers.ModelSerializer):
    usuario_detalle = UsuarioResumenSerializer(source="usuario", read_only=True)

    class Meta:
        model  = Bitacora
        fields = ["id", "usuario", "usuario_detalle", "accion", "modulo",
                  "descripcion", "objeto_id", "ip_address", "timestamp"]
        read_only_fields = fields


class TableroPrediccionesSerializer(serializers.Serializer):
    """Respuesta del tablero general de predicciones (CU14)."""
    partido_id       = serializers.IntegerField()
    local            = serializers.CharField()
    visitante        = serializers.CharField()
    fecha_hora       = serializers.DateTimeField()
    prob_local       = serializers.FloatField()
    prob_empate      = serializers.FloatField()
    prob_visitante   = serializers.FloatField()
    resultado_probable = serializers.CharField()
    confianza        = serializers.FloatField()
