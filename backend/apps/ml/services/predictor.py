"""
apps/ml/services/predictor.py
CU16 — Modelo de Machine Learning para predicción de resultados.
Usa RandomForest entrenado con historial de partidos.
"""
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from django.conf import settings

from apps.fixture.models import Partido, Resultado, TablaPosiciones
from apps.ml.models import PrediccionPartido


MODEL_DIR  = Path(settings.BASE_DIR) / "apps" / "ml" / "models_trained"
MODEL_PATH = MODEL_DIR / "resultado_predictor.joblib"


class PredictorResultados:
    """
    Predice el resultado de un partido basándose en:
    - Puntos actuales de cada equipo en la tabla
    - Diferencia de goles
    - Partidos ganados/perdidos
    - Historial head-to-head (últimos 5 enfrentamientos)
    """

    def __init__(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        self.model   = None
        self.version = "v1.0"

    def _extraer_features(self, partido: Partido) -> np.ndarray:
        """Extrae el vector de características de un partido."""
        def stats_equipo(equipo, campeonato):
            try:
                tabla = TablaPosiciones.objects.get(
                    campeonato=campeonato, equipo=equipo)
                return {
                    "puntos": tabla.puntos,
                    "pg": tabla.pg, "pe": tabla.pe, "pp": tabla.pp,
                    "dg": tabla.diferencia_goles,
                    "gf": tabla.gf,
                }
            except TablaPosiciones.DoesNotExist:
                return {"puntos": 0, "pg": 0, "pe": 0, "pp": 0, "dg": 0, "gf": 0}

        def head_to_head(local, visitante, campeonato):
            """Resultados de los últimos 5 enfrentamientos directos."""
            partidos_prev = Partido.objects.filter(
                campeonato=campeonato,
                estado="FINALIZADO",
            ).filter(
                models.Q(equipo_local=local,     equipo_visitante=visitante) |
                models.Q(equipo_local=visitante, equipo_visitante=local)
            ).order_by("-fecha_hora")[:5]

            victorias_local = 0
            for p in partidos_prev:
                try:
                    r = p.resultado
                    if p.equipo_local == local and r.goles_local > r.goles_visitante:
                        victorias_local += 1
                    elif p.equipo_visitante == local and r.goles_visitante > r.goles_local:
                        victorias_local += 1
                except Resultado.DoesNotExist:
                    pass
            return victorias_local

        sl = stats_equipo(partido.equipo_local,    partido.campeonato)
        sv = stats_equipo(partido.equipo_visitante, partido.campeonato)
        h2h = head_to_head(partido.equipo_local,
                            partido.equipo_visitante,
                            partido.campeonato)

        return np.array([[
            sl["puntos"], sl["pg"], sl["pe"], sl["pp"], sl["dg"], sl["gf"],
            sv["puntos"], sv["pg"], sv["pe"], sv["pp"], sv["dg"], sv["gf"],
            h2h,
            # Ventaja de local (feature fijo = 1.0, puede expandirse)
            1.0,
        ]])

    def entrenar(self, campeonato_id: int) -> dict:
        """
        Entrena el modelo con el historial de partidos finalizados
        del campeonato dado.
        Retorna métricas básicas del entrenamiento.
        """
        from django.db.models import Q
        from apps.deportes.models import Campeonato

        partidos = Partido.objects.filter(
            campeonato_id=campeonato_id,
            estado="FINALIZADO",
        ).select_related("resultado", "equipo_local", "equipo_visitante",
                          "campeonato")

        if partidos.count() < 5:
            return {"error": "Se necesitan al menos 5 partidos finalizados para entrenar."}

        X, y = [], []
        for p in partidos:
            try:
                r = p.resultado
                features = self._extraer_features(p)[0]
                X.append(features)
                # Etiqueta: 0=local gana, 1=empate, 2=visitante gana
                if r.goles_local > r.goles_visitante:
                    y.append(0)
                elif r.goles_local == r.goles_visitante:
                    y.append(1)
                else:
                    y.append(2)
            except Resultado.DoesNotExist:
                continue

        X = np.array(X)
        y = np.array(y)

        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42,
            class_weight="balanced",
        )
        self.model.fit(X, y)
        joblib.dump(self.model, MODEL_PATH)

        # Métrica simple en training set
        accuracy = self.model.score(X, y)
        return {
            "partidos_entrenados": len(X),
            "accuracy_training":   round(accuracy, 4),
            "modelo_guardado":     str(MODEL_PATH),
        }

    def predecir(self, partido: Partido) -> PrediccionPartido:
        """
        Genera y guarda la predicción para un partido próximo.
        Si el modelo no existe, usa heurística de puntos.
        """
        if self.model is None:
            if MODEL_PATH.exists():
                self.model = joblib.load(MODEL_PATH)
            else:
                return self._prediccion_heuristica(partido)

        features = self._extraer_features(partido)
        probas   = self.model.predict_proba(features)[0]

        # probas[0]=local gana, [1]=empate, [2]=visitante gana
        prob_local = float(probas[0]) if len(probas) > 0 else 0.33
        prob_emp   = float(probas[1]) if len(probas) > 1 else 0.34
        prob_visit = float(probas[2]) if len(probas) > 2 else 0.33

        pred, _ = PrediccionPartido.objects.update_or_create(
            partido=partido,
            defaults={
                "prob_victoria_local": prob_local,
                "prob_empate":         prob_emp,
                "prob_victoria_visit": prob_visit,
                "goles_local_pred":    round(prob_local * 3, 1),
                "goles_visit_pred":    round(prob_visit * 3, 1),
                "confianza":           max(prob_local, prob_emp, prob_visit),
                "modelo_version":      self.version,
            },
        )
        return pred

    def _prediccion_heuristica(self, partido: Partido) -> PrediccionPartido:
        """Predicción simple basada en puntos cuando no hay modelo entrenado."""
        def pts(equipo):
            try:
                return TablaPosiciones.objects.get(
                    campeonato=partido.campeonato, equipo=equipo).puntos
            except TablaPosiciones.DoesNotExist:
                return 0

        pts_l = pts(partido.equipo_local)
        pts_v = pts(partido.equipo_visitante)
        total = pts_l + pts_v + 1  # +1 para evitar division por cero

        prob_l = (pts_l / total) * 0.6 + 0.2   # ventaja local
        prob_v = (pts_v / total) * 0.6
        prob_e = 1 - prob_l - prob_v
        if prob_e < 0:
            prob_e = 0.1
            prob_l, prob_v = (1 - prob_e) * prob_l / (prob_l + prob_v), \
                             (1 - prob_e) * prob_v / (prob_l + prob_v)

        pred, _ = PrediccionPartido.objects.update_or_create(
            partido=partido,
            defaults={
                "prob_victoria_local": round(prob_l, 3),
                "prob_empate":         round(prob_e, 3),
                "prob_victoria_visit": round(prob_v, 3),
                "goles_local_pred":    round(prob_l * 2.5, 1),
                "goles_visit_pred":    round(prob_v * 2.5, 1),
                "confianza":           0.5,
                "modelo_version":      "heuristica",
            },
        )
        return pred
