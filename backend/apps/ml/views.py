"""
apps/ml/views.py
CU14 — Tablero de predicciones
CU15 — Riesgo climático
CU16 — Predicción de resultados
CU18 — Recomendaciones de actividades (Groq AI)
CU19 — Bitácora
CU20 — Predicción de asistencia
"""
import requests
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.conf import settings

from apps.users.permissions import EsAdminDUBSS, EsLecturaPublica
from apps.fixture.models import Partido
from .models import PrediccionPartido, PrediccionAsistencia, RiesgoClimatico, Bitacora
from .serializers import (
    PrediccionPartidoSerializer, PrediccionAsistenciaSerializer,
    RiesgoClimaticoSerializer, BitacoraSerializer,
    TableroPrediccionesSerializer,
)
from .services.predictor import PredictorResultados
from .services.clima import ServicioClima


# ── CU14 — Tablero general de predicciones ─────────────────────────────────────

@extend_schema(tags=["ml"])
class TableroPrediccionesView(APIView):
    """CU14 — Tablero con predicciones de todos los partidos próximos de un campeonato."""
    permission_classes = [EsLecturaPublica]

    @extend_schema(
        summary="CU14 — Tablero de predicciones del campeonato",
        parameters=[OpenApiParameter("campeonato", int, required=True)],
    )
    def get(self, request):
        campeonato_id = request.query_params.get("campeonato")
        if not campeonato_id:
            return Response({"error": "Parámetro 'campeonato' requerido."},
                            status=status.HTTP_400_BAD_REQUEST)

        partidos = Partido.objects.filter(
            campeonato_id=campeonato_id,
            estado=Partido.Estado.PROGRAMADO,
        ).select_related(
            "equipo_local", "equipo_visitante", "prediccion"
        ).order_by("fecha_hora")[:20]

        predictor = PredictorResultados()
        resultado = []

        for p in partidos:
            # Genera predicción si no existe
            try:
                pred = p.prediccion
            except PrediccionPartido.DoesNotExist:
                pred = predictor.predecir(p)

            probs = {
                "local":    pred.prob_victoria_local,
                "empate":   pred.prob_empate,
                "visitante": pred.prob_victoria_visit,
            }
            resultado.append({
                "partido_id":        p.id,
                "local":             p.equipo_local.nombre,
                "visitante":         p.equipo_visitante.nombre,
                "fecha_hora":        p.fecha_hora,
                "prob_local":        round(pred.prob_victoria_local * 100, 1),
                "prob_empate":       round(pred.prob_empate * 100, 1),
                "prob_visitante":    round(pred.prob_victoria_visit * 100, 1),
                "resultado_probable": max(probs, key=probs.get),
                "confianza":         round(pred.confianza * 100, 1),
            })

        return Response(resultado)


# ── CU16 — Predicción individual ───────────────────────────────────────────────

@extend_schema(tags=["ml"])
class PrediccionPartidoView(APIView):
    """CU16 — Predicción de resultado de un partido específico."""
    permission_classes = [EsLecturaPublica]

    @extend_schema(summary="CU16 — Predecir resultado de un partido")
    def get(self, request, partido_id):
        try:
            partido = Partido.objects.select_related(
                "equipo_local", "equipo_visitante", "campeonato"
            ).get(pk=partido_id)
        except Partido.DoesNotExist:
            return Response({"error": "Partido no encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

        pred = PredictorResultados().predecir(partido)
        return Response(PrediccionPartidoSerializer(pred).data)


# ── CU15 — Riesgo climático ────────────────────────────────────────────────────

@extend_schema(tags=["ml"])
class RiesgoClimaticoView(APIView):
    """CU15 — Pronóstico de riesgo climático para un partido."""
    permission_classes = [EsLecturaPublica]

    @extend_schema(summary="CU15 — Riesgo climático del partido")
    def get(self, request, partido_id):
        try:
            partido = Partido.objects.select_related(
                "cancha__instalacion"
            ).get(pk=partido_id)
        except Partido.DoesNotExist:
            return Response({"error": "Partido no encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

        riesgo = ServicioClima().consultar(partido)
        return Response(RiesgoClimaticoSerializer(riesgo).data)


# ── CU20 — Predicción de asistencia ───────────────────────────────────────────

@extend_schema(tags=["ml"])
class PrediccionAsistenciaView(APIView):
    """CU20 — Estima asistencia de espectadores para un partido."""
    permission_classes = [EsLecturaPublica]

    @extend_schema(summary="CU20 — Predicción de asistencia")
    def get(self, request, partido_id):
        try:
            partido = Partido.objects.select_related(
                "equipo_local", "equipo_visitante",
                "campeonato", "cancha",
            ).get(pk=partido_id)
        except Partido.DoesNotExist:
            return Response({"error": "Partido no encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

        # Heurística basada en capacidad y relevancia del partido
        cancha_cap = partido.cancha.capacidad if partido.cancha else 500
        base       = min(cancha_cap * 0.6, 800)
        variacion  = int(base * 0.25)

        pred, _ = PrediccionAsistencia.objects.update_or_create(
            partido=partido,
            defaults={
                "asistencia_predicha": int(base),
                "rango_min":           max(0, int(base - variacion)),
                "rango_max":           int(base + variacion),
                "factores": {
                    "capacidad_cancha": cancha_cap,
                    "fase":             partido.fase,
                    "jornada":          partido.jornada,
                },
            },
        )
        return Response(PrediccionAsistenciaSerializer(pred).data)


# ── CU18 — Recomendaciones con Groq AI ────────────────────────────────────────

@extend_schema(tags=["ml"])
class RecomendacionesView(APIView):
    """CU18 — Recomendaciones de actividades deportivas generadas con Groq AI."""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="CU18 — Recomendaciones de actividades deportivas")
    def get(self, request):
        usuario    = request.user
        groq_key   = settings.GROQ_API_KEY

        prompt = (
            f"Soy un estudiante universitario de la UAGRM con rol '{usuario.rol}' "
            f"en la facultad '{usuario.facultad or 'no especificada'}'. "
            "Dame 5 recomendaciones concretas de actividades deportivas universitarias "
            "que puedo practicar esta semana. Sé breve y directo. Responde en español."
        )

        if not groq_key:
            # Respuesta de ejemplo sin API key
            return Response({
                "recomendaciones": [
                    "Participa en el torneo de fútbol sala de tu facultad.",
                    "Inscríbete en las clases de natación de la DUBSS los martes y jueves.",
                    "Únete al equipo de voleibol mixto — los entrenamientos son los lunes.",
                    "Aprovecha las canchas de básquetbol disponibles de 7am a 9am.",
                    "Consulta la agenda semanal de la DUBSS para eventos deportivos abiertos.",
                ],
                "fuente": "ejemplo (configura GROQ_API_KEY para respuestas dinámicas)",
            })

        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       "llama3-8b-8192",
                    "messages":    [{"role": "user", "content": prompt}],
                    "max_tokens":  400,
                    "temperature": 0.7,
                },
                timeout=15,
            )
            resp.raise_for_status()
            texto = resp.json()["choices"][0]["message"]["content"]
            return Response({"recomendaciones": texto, "fuente": "Groq / LLaMA3"})
        except Exception as e:
            return Response(
                {"error": f"Error al consultar Groq: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


# ── CU19 — Bitácora ────────────────────────────────────────────────────────────

@extend_schema(tags=["ml"])
class BitacoraListView(generics.ListAPIView):
    """CU19 — Consulta del registro de auditoría del sistema."""
    serializer_class   = BitacoraSerializer
    permission_classes = [EsAdminDUBSS]
    filterset_fields   = ["accion", "modulo", "usuario"]
    search_fields      = ["descripcion", "modulo"]
    ordering_fields    = ["timestamp"]

    def get_queryset(self):
        return Bitacora.objects.select_related("usuario").order_by("-timestamp")


# ── Entrenamiento del modelo ML ────────────────────────────────────────────────

@extend_schema(tags=["ml"])
class EntrenarModeloView(APIView):
    """Entrena el modelo de predicción con el historial de un campeonato."""
    permission_classes = [EsAdminDUBSS]

    @extend_schema(
        summary="Entrenar modelo ML con historial del campeonato",
        parameters=[OpenApiParameter("campeonato_id", int, required=True)],
    )
    def post(self, request):
        campeonato_id = request.data.get("campeonato_id")
        if not campeonato_id:
            return Response({"error": "campeonato_id requerido."},
                            status=status.HTTP_400_BAD_REQUEST)
        resultado = PredictorResultados().entrenar(campeonato_id)
        return Response(resultado)
