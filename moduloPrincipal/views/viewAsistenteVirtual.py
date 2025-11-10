from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from moduloPrincipal.utils.nutri_scorecard import QUESTIONS, evaluar_cuestionario


ARTIFACTS_DIR = (
    Path(__file__).resolve().parents[1] / "static" / "tesis" / "model_artifacts"
)
_MODEL_CACHE: Pipeline | None = None
_FEATURES_CACHE: list[str] | None = None
_METADATA_CACHE: dict | None = None


def _debug_print(label: str, payload):
    try:
        printable = json.dumps(payload, ensure_ascii=True, default=str)
    except TypeError:
        printable = str(payload)
    print(f"[perfil_nutricional] {label}: {printable}")





def _to_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        if isinstance(value, str):
            value = value.replace(",", ".").strip()
        return float(value)
    except (ValueError, TypeError):
        return default


def _extract_scores(data: dict):
    """
    Normaliza las respuestas recibidas desde el front para el cuestionario.
    Acepta formatos:
        {"scores": {"alcohol": 0, ...}}
        {"respuestas": [{"id": "alcohol", "respuesta": 0}, ...]}
        {"alcohol": 0, "frutas": 3, ...}
    """
    scores = {}
    valid_ids = {q.id for q in QUESTIONS}

    if isinstance(data.get("scores"), dict):
        for k, v in data["scores"].items():
            if k in valid_ids:
                scores[k] = _to_float(v)

    if isinstance(data.get("respuestas"), list):
        for item in data["respuestas"]:
            qid = item.get("id") or item.get("clave") or item.get("pregunta") or item.get("type")
            if qid and qid in valid_ids:
                scores[qid] = _to_float(item.get("respuesta"))

    if not scores:
        for key, value in data.items():
            if key in valid_ids:
                scores[key] = _to_float(value)

    for q in QUESTIONS:
        scores.setdefault(q.id, 0.0)

    return scores


def _load_model_artifacts():
    global _MODEL_CACHE, _FEATURES_CACHE, _METADATA_CACHE

    if _MODEL_CACHE is None:
        _MODEL_CACHE = joblib.load(ARTIFACTS_DIR / "risk_profile_model.joblib")
        model_info = {
            "pipeline_steps": list(_MODEL_CACHE.named_steps.keys()),
        }
        clf = _MODEL_CACHE.named_steps.get("clf")
        if clf is not None:
            model_info["estimator"] = {
                "type": clf.__class__.__name__,
                "n_estimators": getattr(clf, "n_estimators", None),
                "min_samples_leaf": getattr(clf, "min_samples_leaf", None),
                "class_weight": getattr(clf, "class_weight", None),
                "classes": getattr(clf, "classes_", []),
            }
        _debug_print("modelo_cargado", model_info)

    if _FEATURES_CACHE is None:
        feature_file = ARTIFACTS_DIR / "feature_list.txt"
        _FEATURES_CACHE = [
            line.strip() for line in feature_file.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        _debug_print(
            "caracteristicas_cargadas",
            {"orden": _FEATURES_CACHE, "total": len(_FEATURES_CACHE)},
        )

    if _METADATA_CACHE is None:
        metadata_file = ARTIFACTS_DIR / "scientific_metadata.json"
        try:
            _METADATA_CACHE = json.loads(metadata_file.read_text(encoding="utf-8"))
            _debug_print("metadata_modelo", _METADATA_CACHE)
        except FileNotFoundError:
            _METADATA_CACHE = {}
            _debug_print("metadata_modelo", "Archivo scientific_metadata.json no encontrado")

    return _MODEL_CACHE, _FEATURES_CACHE, _METADATA_CACHE


def _recomendaciones(risk_label: str):
    """Mensajes personalizados por nivel de alerta nutricional."""
    if risk_label == "alto":
        return [
            "🚨 PRIORIDAD ALTA: Tu perfil nutricional requiere atención inmediata.",
            "🥗 Prioriza verduras, frutas y granos integrales en cada comida.",
            "🚫 Reduce drásticamente bebidas azucaradas, ultraprocesados y sodio (<2300mg/día).",
            "🏃‍♂️ Incrementa actividad física: mínimo 150 min/semana de actividad moderada.",
            "👨‍⚕️ IMPORTANTE: Busca acompañamiento profesional para diseñar un plan personalizado.",
        ]
    if risk_label == "moderado":
        return [
            "⚠️ ALERTA INTERMEDIA: Ajusta hábitos para recuperar el equilibrio nutricional.",
            "🌾 Aumenta fibra diaria (legumbres, cereales integrales) y reduce azúcares añadidos.",
            "🏋️‍♀️ Objetivo: 150-300 min/semana de actividad física moderada.",
            "💧 Hidrátate adecuadamente y controla porciones en las comidas.",
            "🧘‍♂️ Gestiona el estrés y cuida tu descanso.",
        ]
    return [
        "✅ EXCELENTE: Perfil nutricional equilibrado.",
        "🎯 Mantén tus hábitos saludables actuales con monitoreo periódico.",
        "🌈 Varía frutas, verduras y granos integrales cada semana.",
        "⚖️ Vigila el balance energético y mantén actividad física regular.",
    ]


def _sanear(obj):
    """Convierte NaN/inf en None para JSON."""
    if isinstance(obj, dict):
        return {k: _sanear(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanear(v) for v in obj]
    if isinstance(obj, float):
        if not np.isfinite(obj):
            return None
        return obj
    if isinstance(obj, np.floating):
        val = float(obj)
        return None if not np.isfinite(val) else val
    if isinstance(obj, np.integer):
        return int(obj)
    return obj




"""
    Analiza el cuestionario nutricional de 10 ítems y devuelve:
        - Etiqueta final (saludable/moderado/alto)
        - Score normalizado 0-100
        - Detalle por pregunta (puntos obtenidos y máximos)
        - Recomendaciones personalizadas
    """
@csrf_exempt
def perfil_nutricional(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Usa POST")
    try:
        if request.content_type and "application/json" in request.content_type:
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST.dict()
    except Exception:
        data = request.POST.dict()
    _debug_print("payload_recibido", data)
    scores = _extract_scores(data or {})
    _debug_print("puntajes_normalizados", scores)
    resultado = evaluar_cuestionario(scores)
    _debug_print(
        "score_cientifico",
        {
            "label": resultado["label"],
            "score_normalizado": resultado["score_normalizado"],
            "score_raw": resultado["score_raw"],
        },
    )
    model, feature_names, metadata = _load_model_artifacts()
    feature_vector = {name: _to_float(scores.get(name, 0.0)) for name in feature_names}
    _debug_print("vector_caracteristicas", feature_vector)
    X = pd.DataFrame([feature_vector])
    try:
        pred = model.predict(X)
        risk = pred[0]
        if hasattr(model, "predict_proba"):
            classes = list(getattr(model, "classes_", []))
            probabilities = model.predict_proba(X)[0] if classes else []
            proba_map = {
                label: float(prob) for label, prob in zip(classes, probabilities)
            }
        else:
            proba_map = {}
        _debug_print(
            "salida_modelo",
            {
                "prediccion": risk,
                "probabilidades": proba_map,
            },
        )
    except Exception:
        risk = resultado["label"]
        proba_map = {}
        _debug_print("salida_modelo_error", {"label_fallback": risk})

    mensaje = {
        "alto": "🚨 Alerta nutricional ALTA. Busca apoyo profesional y realiza cambios inmediatos.",
        "moderado": "⚠️ Alerta nutricional MODERADA. Ajusta hábitos para recuperar el equilibrio.",
        "saludable": "✅ Alerta nutricional BAJA. Mantén tus hábitos y monitorea periódicamente.",
    }[risk]

    respuesta = {
        "ok": True,
        "risk_label": risk,
        "score": resultado["score_normalizado"],
        "raw_score": resultado["score_raw"],
        "score_max": resultado["score_max"],
        "detalle": resultado["detalle"],
        "recommendations": _recomendaciones(risk),
        "mensaje": mensaje,
        "model_features": feature_vector,
        "model_probabilities": proba_map,
        "model_metadata": metadata.get("modelo", {}) if metadata else {},
    }

    return JsonResponse(_sanear(respuesta), status=200, json_dumps_params={"ensure_ascii": False})
