"""
apps/notificaciones/views.py
CU17 — Envío de notificaciones push y por email.
"""
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.core.mail import send_mail
from django.conf import settings

from apps.users.models import Usuario
from apps.users.permissions import EsCoordinadorOAdmin


@extend_schema(tags=["notificaciones"])
class EnviarNotificacionView(APIView):
    """CU17 — Envía notificación push FCM y/o email a usuarios del sistema."""
    permission_classes = [EsCoordinadorOAdmin]

    @extend_schema(summary="CU17 — Enviar notificación a usuarios")
    def post(self, request):
        titulo   = request.data.get("titulo", "DUBSS")
        mensaje  = request.data.get("mensaje", "")
        rol      = request.data.get("rol")          # opcional: filtrar por rol
        usuarios_ids = request.data.get("usuarios") # opcional: lista de IDs

        if not mensaje:
            return Response({"error": "El campo 'mensaje' es requerido."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Filtrar destinatarios
        qs = Usuario.objects.filter(is_active=True)
        if rol:
            qs = qs.filter(rol=rol)
        if usuarios_ids:
            qs = qs.filter(id__in=usuarios_ids)

        # Envío push (FCM)
        tokens     = list(qs.exclude(fcm_token="").values_list("fcm_token", flat=True))
        push_sent  = 0
        if tokens and settings.FIREBASE_SERVER_KEY:
            try:
                resp = requests.post(
                    "https://fcm.googleapis.com/fcm/send",
                    headers={
                        "Authorization": f"key={settings.FIREBASE_SERVER_KEY}",
                        "Content-Type":  "application/json",
                    },
                    json={
                        "registration_ids": tokens,
                        "notification": {"title": titulo, "body": mensaje},
                    },
                    timeout=10,
                )
                push_sent = resp.json().get("success", 0)
            except Exception:
                pass

        # Envío email
        emails     = list(qs.values_list("email", flat=True))
        email_sent = 0
        if emails and settings.EMAIL_HOST_USER:
            try:
                send_mail(
                    subject=titulo,
                    message=mensaje,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=emails,
                    fail_silently=True,
                )
                email_sent = len(emails)
            except Exception:
                pass

        return Response({
            "mensaje":     "Notificación enviada.",
            "push_sent":   push_sent,
            "email_sent":  email_sent,
            "total_dest":  qs.count(),
        })
