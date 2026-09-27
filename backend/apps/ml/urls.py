from django.urls import path
from .views import (
    TableroPrediccionesView,
    PrediccionPartidoView,
    RiesgoClimaticoView,
    PrediccionAsistenciaView,
    RecomendacionesView,
    BitacoraListView,
    EntrenarModeloView,
)

urlpatterns = [
    # CU14
    path("tablero/",                              TableroPrediccionesView.as_view(),  name="ml-tablero"),
    # CU15
    path("riesgo-climatico/<int:partido_id>/",    RiesgoClimaticoView.as_view(),      name="ml-riesgo"),
    # CU16
    path("prediccion-partido/<int:partido_id>/",  PrediccionPartidoView.as_view(),    name="ml-prediccion"),
    # CU18
    path("recomendaciones/",                      RecomendacionesView.as_view(),      name="ml-recomendaciones"),
    # CU19
    path("bitacora/",                             BitacoraListView.as_view(),         name="ml-bitacora"),
    # CU20
    path("asistencia/<int:partido_id>/",          PrediccionAsistenciaView.as_view(), name="ml-asistencia"),
    # Entrenamiento
    path("entrenar/",                             EntrenarModeloView.as_view(),       name="ml-entrenar"),
]
