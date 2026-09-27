"""
apps/fixture/views.py
CU08 — Creación de fixture
CU10 — Visualización de calendarios
CU11 — Registro de resultados
CU12 — Registro de incidencias
CU13 — Tabla de posiciones
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db import transaction

from apps.users.permissions import (
    EsAdminDUBSS, EsCoordinadorOAdmin,
    EsArbitroOAdmin, EsLecturaPublica,
)
from .models import Partido, Resultado, Incidencia, TablaPosiciones
from .serializers import (
    PartidoSerializer, PartidoResumenSerializer,
    ResultadoSerializer, IncidenciaSerializer,
    TablaPosicionesSerializer,
)
from .services.fixture_generator import FixtureGenerator


@extend_schema(tags=["fixture"])
class PartidoViewSet(viewsets.ModelViewSet):
    """CU10 — Calendarios / listado de partidos."""
    queryset = Partido.objects.select_related(
        "equipo_local", "equipo_visitante", "cancha",
        "arbitro", "campeonato",
    ).prefetch_related("incidencias").order_by("fecha_hora")

    filterset_fields = ["campeonato", "estado", "jornada", "equipo_local", "equipo_visitante"]
    search_fields    = ["equipo_local__nombre", "equipo_visitante__nombre"]

    def get_serializer_class(self):
        if self.action == "list":
            return PartidoResumenSerializer
        return PartidoSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsCoordinadorOAdmin()]
        return [EsLecturaPublica()]

    # ── CU11: Registrar resultado ─────────────────────────────────────────────
    @extend_schema(
        summary="CU11 — Registrar resultado del partido",
        request=ResultadoSerializer,
    )
    @action(detail=True, methods=["post"], url_path="resultado",
            permission_classes=[EsArbitroOAdmin])
    def registrar_resultado(self, request, pk=None):
        partido = self.get_object()

        if partido.estado == Partido.Estado.FINALIZADO:
            return Response(
                {"error": "Este partido ya tiene resultado registrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ResultadoSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            resultado = serializer.save(partido=partido)
            partido.estado = Partido.Estado.FINALIZADO
            partido.save(update_fields=["estado"])

            # Actualizar tabla de posiciones
            _actualizar_tabla(partido, resultado)

        return Response(ResultadoSerializer(resultado).data,
                        status=status.HTTP_201_CREATED)

    # ── CU12: Registrar incidencia ────────────────────────────────────────────
    @extend_schema(
        summary="CU12 — Registrar incidencia del partido",
        request=IncidenciaSerializer,
    )
    @action(detail=True, methods=["post"], url_path="incidencia",
            permission_classes=[EsArbitroOAdmin])
    def registrar_incidencia(self, request, pk=None):
        partido    = self.get_object()
        serializer = IncidenciaSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(partido=partido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["fixture"])
class GenerarFixtureView(APIView):
    """CU08 — Generar fixture automático de un campeonato."""
    permission_classes = [EsCoordinadorOAdmin]

    @extend_schema(
        summary="CU08 — Generar fixture del campeonato",
        parameters=[
            OpenApiParameter("campeonato_id", int,  required=True,
                             description="ID del campeonato"),
            OpenApiParameter("usar_ml",       bool, required=False,
                             description="Usar ML para optimizar horarios"),
            OpenApiParameter("hora_inicio",   str,  required=False,
                             description="Hora de inicio (HH:MM), por defecto 08:00"),
            OpenApiParameter("dias_entre_jornadas", int, required=False,
                             description="Días entre jornadas, por defecto 7"),
        ],
    )
    def post(self, request):
        # Lee desde query string (Swagger) O body JSON
        campeonato_id       = request.data.get("campeonato_id") or request.query_params.get("campeonato_id")
        usar_ml             = request.data.get("usar_ml", request.query_params.get("usar_ml", False))
        hora_inicio         = request.data.get("hora_inicio") or request.query_params.get("hora_inicio", "08:00")
        dias_entre_jornadas = int(request.data.get("dias_entre_jornadas") or request.query_params.get("dias_entre_jornadas", 7))






        if not campeonato_id:
            return Response(
                {"error": "campeonato_id es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            gen      = FixtureGenerator(
                campeonato_id=campeonato_id,
                hora_inicio=hora_inicio,
                dias_entre_jornadas=dias_entre_jornadas,
            )
            partidos = gen.generar(usar_ml=usar_ml)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Error generando fixture: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "mensaje":          f"Fixture generado: {len(partidos)} partidos creados.",
                "total_partidos":   len(partidos),
                "generado_por_ml":  usar_ml,
                "partidos":         PartidoResumenSerializer(partidos, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["fixture"])
class TablaPosicionesView(APIView):
    """CU13 — Tabla de posiciones de un campeonato."""
    permission_classes = [EsLecturaPublica]

    @extend_schema(
        summary="CU13 — Tabla de posiciones",
        parameters=[
            OpenApiParameter("campeonato", int, required=True,
                             description="ID del campeonato"),
        ],
    )
    def get(self, request):
        campeonato_id = request.query_params.get("campeonato")
        if not campeonato_id:
            return Response(
                {"error": "Parámetro 'campeonato' requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tabla = TablaPosiciones.objects.filter(
            campeonato_id=campeonato_id
        ).select_related("equipo").order_by("-puntos", "-gf")

        return Response(TablaPosicionesSerializer(tabla, many=True).data)


# ── Helper interno ─────────────────────────────────────────────────────────────

def _actualizar_tabla(partido: Partido, resultado: Resultado):
    """Actualiza la tabla de posiciones de ambos equipos tras un resultado."""
    tabla_local, _ = TablaPosiciones.objects.get_or_create(
        campeonato=partido.campeonato,
        equipo=partido.equipo_local,
    )
    tabla_visit, _ = TablaPosiciones.objects.get_or_create(
        campeonato=partido.campeonato,
        equipo=partido.equipo_visitante,
    )
    tabla_local.actualizar_con_resultado(
        resultado.goles_local, resultado.goles_visitante
    )
    tabla_visit.actualizar_con_resultado(
        resultado.goles_visitante, resultado.goles_local
    )
