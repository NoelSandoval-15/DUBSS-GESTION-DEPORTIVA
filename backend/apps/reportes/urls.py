from django.urls import path
from .views import ReportePDFView, ReporteExcelView

urlpatterns = [
    path("campeonato/<int:campeonato_id>/pdf/",   ReportePDFView.as_view(),   name="reporte-pdf"),
    path("campeonato/<int:campeonato_id>/excel/",  ReporteExcelView.as_view(), name="reporte-excel"),
]
