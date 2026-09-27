from rest_framework import serializers
from .models import Instalacion, Cancha, BloqueoCancha


class InstalacionSerializer(serializers.ModelSerializer):
    total_canchas = serializers.SerializerMethodField()

    class Meta:
        model  = Instalacion
        fields = ["id", "nombre", "ubicacion", "latitud", "longitud",
                  "descripcion", "imagen", "activa", "total_canchas"]
        read_only_fields = ["id"]

    def get_total_canchas(self, obj):
        return obj.canchas.filter(activa=True).count()


class CanchaSerializer(serializers.ModelSerializer):
    instalacion_nombre = serializers.CharField(source="instalacion.nombre", read_only=True)
    deporte_nombre     = serializers.CharField(source="deporte.nombre",     read_only=True)

    class Meta:
        model  = Cancha
        fields = ["id", "instalacion", "instalacion_nombre", "nombre",
                  "deporte", "deporte_nombre", "superficie", "capacidad",
                  "techada", "activa", "observaciones"]
        read_only_fields = ["id"]


class BloqueoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BloqueoCancha
        fields = ["id", "cancha", "fecha_inicio", "fecha_fin",
                  "motivo", "creado_por", "creado_en"]
        read_only_fields = ["id", "creado_por", "creado_en"]

    def create(self, validated_data):
        validated_data["creado_por"] = self.context["request"].user
        return super().create(validated_data)
