from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
import numpy as np
from moduloPrincipal.utils.nutri_scorecard import QUESTIONS, evaluar_cuestionario


# ============================================================
# Utilidades
# ============================================================
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


# ============================================================
# Vista principal del asistente
# ============================================================
@csrf_exempt
def perfil_nutricional(request):
    """
    Analiza el cuestionario nutricional de 10 ítems y devuelve:
        - Etiqueta final (saludable/moderado/alto)
        - Score normalizado 0-100
        - Detalle por pregunta (puntos obtenidos y máximos)
        - Recomendaciones personalizadas
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Usa POST")

    try:
        if request.content_type and "application/json" in request.content_type:
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST.dict()
    except Exception:
        data = request.POST.dict()

    scores = _extract_scores(data or {})
    resultado = evaluar_cuestionario(scores)

    risk = resultado["label"]
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
    }

    return JsonResponse(_sanear(respuesta), status=200, json_dumps_params={"ensure_ascii": False})
