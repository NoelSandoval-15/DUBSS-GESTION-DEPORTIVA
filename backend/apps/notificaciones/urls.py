from django.urls import path
from .views import EnviarNotificacionView

urlpatterns = [
    path("enviar/", EnviarNotificacionView.as_view(), name="notificacion-enviar"),
]
