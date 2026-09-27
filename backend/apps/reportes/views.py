"""
apps/reportes/views.py
CU21 — Exportación de reportes en PDF y Excel.
"""
import io
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.http import HttpResponse

from apps.users.permissions import EsCoordinadorOAdmin, EsLecturaPublica
from apps.deportes.models import Campeonato
from apps.fixture.models import Partido, TablaPosiciones


def _get_campeonato(campeonato_id):
    try:
        return Campeonato.objects.select_related("deporte", "categoria").get(pk=campeonato_id)
    except Campeonato.DoesNotExist:
        return None


@extend_schema(tags=["reportes"])
class ReportePDFView(APIView):
    """CU21 — Exportar reporte completo del campeonato en PDF."""
    permission_classes = [EsLecturaPublica]

    @extend_schema(summary="CU21 — Descargar reporte PDF del campeonato")
    def get(self, request, campeonato_id):
        campeonato = _get_campeonato(campeonato_id)
        if not campeonato:
            return Response({"error": "Campeonato no encontrado."},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
        except ImportError:
            return Response({"error": "reportlab no disponible."},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        buf    = io.BytesIO()
        doc    = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()
        story  = []

        # ── Encabezado ────────────────────────────────────────────────────────
        story.append(Paragraph("DUBSS — UAGRM", styles["Title"]))
        story.append(Paragraph(f"Reporte: {campeonato.nombre}", styles["Heading1"]))
        story.append(Paragraph(
            f"Deporte: {campeonato.deporte} | Categoría: {campeonato.categoria} | "
            f"Estado: {campeonato.estado}",
            styles["Normal"],
        ))
        story.append(Spacer(1, 0.3 * inch))

        # ── Tabla de posiciones ───────────────────────────────────────────────
        story.append(Paragraph("Tabla de Posiciones", styles["Heading2"]))
        tabla = TablaPosiciones.objects.filter(
            campeonato=campeonato
        ).select_related("equipo").order_by("-puntos", "-gf")

        data = [["#", "Equipo", "PJ", "PG", "PE", "PP", "GF", "GC", "DG", "Pts"]]
        for i, fila in enumerate(tabla, 1):
            data.append([
                str(i),
                fila.equipo.nombre,
                str(fila.pj), str(fila.pg), str(fila.pe), str(fila.pp),
                str(fila.gf), str(fila.gc),
                str(fila.diferencia_goles),
                str(fila.puntos),
            ])

        if len(data) > 1:
            t = Table(data, colWidths=[0.4*inch, 2*inch] + [0.5*inch]*8)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a6b3c")),
                ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
                ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(t)

        story.append(Spacer(1, 0.3 * inch))

        # ── Fixture / partidos ────────────────────────────────────────────────
        story.append(Paragraph("Fixture de Partidos", styles["Heading2"]))
        partidos = Partido.objects.filter(
            campeonato=campeonato
        ).select_related("equipo_local", "equipo_visitante", "cancha").order_by("jornada", "fecha_hora")

        data2 = [["Jornada", "Local", "Resultado", "Visitante", "Cancha", "Fecha"]]
        for p in partidos:
            try:
                res = f"{p.resultado.goles_local} - {p.resultado.goles_visitante}"
            except Exception:
                res = "Pend."
            data2.append([
                str(p.jornada),
                p.equipo_local.nombre,
                res,
                p.equipo_visitante.nombre,
                p.cancha.nombre if p.cancha else "—",
                p.fecha_hora.strftime("%d/%m/%Y %H:%M"),
            ])

        if len(data2) > 1:
            t2 = Table(data2, colWidths=[0.6*inch, 1.5*inch, 0.8*inch, 1.5*inch, 1.2*inch, 1.2*inch])
            t2.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a6b3c")),
                ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
                ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE",   (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(t2)

        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} — Sistema DUBSS",
            styles["Normal"],
        ))

        doc.build(story)
        buf.seek(0)
        nombre = f"reporte_{campeonato.nombre.replace(' ', '_')}.pdf"
        response = HttpResponse(buf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{nombre}"'
        return response


@extend_schema(tags=["reportes"])
class ReporteExcelView(APIView):
    """CU21 — Exportar reporte completo del campeonato en Excel."""
    permission_classes = [EsLecturaPublica]

    @extend_schema(summary="CU21 — Descargar reporte Excel del campeonato")
    def get(self, request, campeonato_id):
        campeonato = _get_campeonato(campeonato_id)
        if not campeonato:
            return Response({"error": "Campeonato no encontrado."},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            return Response({"error": "openpyxl no disponible."},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        wb = openpyxl.Workbook()

        # ── Hoja 1: Tabla de posiciones ───────────────────────────────────────
        ws1 = wb.active
        ws1.title = "Tabla de Posiciones"
        header_fill = PatternFill("solid", fgColor="1a6b3c")
        header_font = Font(bold=True, color="FFFFFF")

        headers = ["#", "Equipo", "PJ", "PG", "PE", "PP", "GF", "GC", "DG", "Pts"]
        for col, h in enumerate(headers, 1):
            cell = ws1.cell(row=1, column=col, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        tabla = TablaPosiciones.objects.filter(
            campeonato=campeonato
        ).select_related("equipo").order_by("-puntos", "-gf")

        for i, fila in enumerate(tabla, 1):
            ws1.append([
                i, fila.equipo.nombre,
                fila.pj, fila.pg, fila.pe, fila.pp,
                fila.gf, fila.gc, fila.diferencia_goles, fila.puntos,
            ])

        ws1.column_dimensions["B"].width = 25

        # ── Hoja 2: Fixture ───────────────────────────────────────────────────
        ws2 = wb.create_sheet("Fixture")
        headers2 = ["Jornada", "Local", "Goles L", "Goles V", "Visitante",
                    "Cancha", "Fecha", "Estado"]
        for col, h in enumerate(headers2, 1):
            cell = ws2.cell(row=1, column=col, value=h)
            cell.fill = header_fill
            cell.font = header_font

        partidos = Partido.objects.filter(
            campeonato=campeonato
        ).select_related("equipo_local", "equipo_visitante", "cancha").order_by("jornada", "fecha_hora")

        for p in partidos:
            try:
                gl = p.resultado.goles_local
                gv = p.resultado.goles_visitante
            except Exception:
                gl, gv = "", ""
            ws2.append([
                p.jornada,
                p.equipo_local.nombre,
                gl, gv,
                p.equipo_visitante.nombre,
                p.cancha.nombre if p.cancha else "—",
                p.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                p.estado,
            ])

        for col in ["B", "E"]:
            ws2.column_dimensions[col].width = 22

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        nombre = f"reporte_{campeonato.nombre.replace(' ', '_')}.xlsx"
        response = HttpResponse(
            buf,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{nombre}"'
        return response
