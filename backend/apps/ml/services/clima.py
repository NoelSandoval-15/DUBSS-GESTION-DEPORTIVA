"""
apps/ml/services/clima.py
CU15 — Consulta de pronóstico climático usando OpenWeatherMap.
"""
import requests
from django.conf import settings
from apps.fixture.models import Partido
from apps.ml.models import RiesgoClimatico


OWMAP_URL = "https://api.openweathermap.org/data/2.5/forecast"


class ServicioClima:
    """Consulta el pronóstico para la cancha de un partido y determina el nivel de riesgo."""

    UMBRALES = {
        "lluvia_mm":    {"medio": 2.5, "alto": 7.5, "critico": 15.0},
        "viento_kmh":   {"medio": 30,  "alto": 50,  "critico": 70},
        "temp_c_baja":  {"medio": 10,  "alto": 5,   "critico": 0},
    }

    def consultar(self, partido: Partido) -> RiesgoClimatico:
        cancha = partido.cancha
        if not cancha or not cancha.instalacion.latitud:
            return self._riesgo_sin_datos(partido)

        api_key = settings.OPENWEATHER_API_KEY
        if not api_key:
            return self._riesgo_sin_datos(partido)

        try:
            resp = requests.get(OWMAP_URL, params={
                "lat":   float(cancha.instalacion.latitud),
                "lon":   float(cancha.instalacion.longitud),
                "appid": api_key,
                "units": "metric",
                "lang":  "es",
                "cnt":   8,  # próximas 24h
            }, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException:
            return self._riesgo_sin_datos(partido)

        # Buscar el bloque más cercano a la hora del partido
        objetivo    = partido.fecha_hora.timestamp()
        pronostico  = min(data["list"], key=lambda x: abs(x["dt"] - objetivo))

        temp        = pronostico["main"]["temp"]
        viento      = pronostico["wind"]["speed"] * 3.6  # m/s → km/h
        lluvia      = pronostico.get("rain", {}).get("3h", 0.0)
        descripcion = pronostico["weather"][0]["description"].capitalize()

        nivel, recomendacion = self._calcular_riesgo(temp, viento, lluvia, cancha.techada)

        obj, _ = RiesgoClimatico.objects.update_or_create(
            partido=partido,
            defaults={
                "nivel_riesgo":  nivel,
                "temperatura":   round(temp, 1),
                "precipitacion": round(lluvia, 1),
                "viento":        round(viento, 1),
                "descripcion":   descripcion,
                "recomendacion": recomendacion,
                "fuente_api":    "OpenWeatherMap",
            },
        )
        return obj

    def _calcular_riesgo(self, temp, viento, lluvia, techada):
        u = self.UMBRALES
        nivel = RiesgoClimatico.NivelRiesgo.BAJO
        factores = []

        if lluvia >= u["lluvia_mm"]["critico"] and not techada:
            nivel = RiesgoClimatico.NivelRiesgo.CRITICO
            factores.append(f"Lluvia intensa ({lluvia:.1f} mm)")
        elif lluvia >= u["lluvia_mm"]["alto"] and not techada:
            nivel = RiesgoClimatico.NivelRiesgo.ALTO
            factores.append(f"Lluvia moderada-alta ({lluvia:.1f} mm)")
        elif lluvia >= u["lluvia_mm"]["medio"] and not techada:
            nivel = RiesgoClimatico.NivelRiesgo.MEDIO
            factores.append(f"Lluvia leve ({lluvia:.1f} mm)")

        if viento >= u["viento_kmh"]["critico"]:
            nivel = RiesgoClimatico.NivelRiesgo.CRITICO
            factores.append(f"Viento muy fuerte ({viento:.0f} km/h)")
        elif viento >= u["viento_kmh"]["alto"]:
            if nivel == RiesgoClimatico.NivelRiesgo.BAJO:
                nivel = RiesgoClimatico.NivelRiesgo.ALTO
            factores.append(f"Viento fuerte ({viento:.0f} km/h)")

        if temp <= u["temp_c_baja"]["critico"]:
            factores.append(f"Temperatura extrema ({temp:.0f}°C)")
        elif temp <= u["temp_c_baja"]["alto"]:
            factores.append(f"Temperatura muy baja ({temp:.0f}°C)")

        if not factores:
            rec = "Condiciones favorables para el partido."
        elif nivel == RiesgoClimatico.NivelRiesgo.CRITICO:
            rec = "Se recomienda SUSPENDER o REPROGRAMAR el partido. " + "; ".join(factores)
        elif nivel == RiesgoClimatico.NivelRiesgo.ALTO:
            rec = "Considerar reprogramación. " + "; ".join(factores)
        else:
            rec = "Monitorear condiciones. " + "; ".join(factores)

        return nivel, rec

    def _riesgo_sin_datos(self, partido):
        obj, _ = RiesgoClimatico.objects.update_or_create(
            partido=partido,
            defaults={
                "nivel_riesgo":  RiesgoClimatico.NivelRiesgo.BAJO,
                "descripcion":   "Sin datos climáticos disponibles.",
                "recomendacion": "Verificar condiciones manualmente.",
                "fuente_api":    "N/A",
            },
        )
        return obj
