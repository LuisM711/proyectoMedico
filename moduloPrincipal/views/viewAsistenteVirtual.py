from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib

# ============================================================
# Carga de artefactos del modelo (una sola vez por proceso)
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent     # .../moduloPrincipal
STATIC_DIR = BASE_DIR / "static" / "tesis"
ART_DIR = STATIC_DIR / "model_artifacts"

MODEL_PATH = ART_DIR / "risk_profile_model.joblib"
FEATS_PATH = ART_DIR / "feature_list.txt"

try:
    PIPE = joblib.load(MODEL_PATH)
    FEATURES = [l.strip() for l in open(FEATS_PATH, encoding="utf-8").read().splitlines() if l.strip()]
    MODEL_READY = True
except Exception as e:
    print("[perfil_nutricional] Error cargando artefactos:", e)
    PIPE, FEATURES, MODEL_READY = None, [], False


# ============================================================
# Utilidades de parseo / mapeo
# ============================================================
def _to_float(x, default=np.nan):
    try:
        if x is None or x == "":
            return default
        if isinstance(x, str):
            x = x.replace(",", ".").strip()
        return float(x)
    except Exception:
        return default

def _map_bool(val):
    s = str(val).lower().strip()
    if s in ("1", "true", "si", "sí", "y", "yes"):
        return 1.0
    if s in ("0", "false", "no"):
        return 0.0
    try:
        return float(s)
    except Exception:
        return np.nan

def _map_sex(value):
    """ NHANES RIAGENDR: 1=Hombre, 2=Mujer. """
    if value is None or value == "":
        return np.nan
    s = str(value).lower().strip()
    if s in ("1", "m", "hombre", "male", "masculino"):
        return 1
    if s in ("2", "f", "mujer", "female", "femenino"):
        return 2
    try:
        v = int(float(s))
        if v in (1, 2):
            return v
    except Exception:
        pass
    return np.nan

def _build_payload_from_data(data: dict, features_expected: list) -> dict:
    """
    Construye el dict de features que el modelo espera.
    Soporta:
      A) JSON plano: {"kcal": 2200, "pct_protein": 20, ...}
      B) 'respuestas': [ { "clave"/"pregunta": "...", "respuesta": "..." }, ... ]
    """
    payload = {feat: np.nan for feat in features_expected}

    # 1) Recolectar entradas en índice normalizado
    pool = {}
    for k, v in (data or {}).items():
        if k == "respuestas":
            continue
        pool[k.strip().lower()] = v

    if isinstance(data.get("respuestas"), list):
        for item in data["respuestas"]:
            name = (item.get("clave") or item.get("campo") or item.get("pregunta") or "").strip().lower()
            val = item.get("respuesta", "")
            if name:
                pool[name] = val

    # 2) Aliases (ajusta si tu front usa otros nombres)
    aliases = {
        # Demografía (opcionales)
        "RIDAGEYR": ["ridageyr", "edad", "age"],
        "RIAGENDR": ["riagendr", "sexo", "genero", "gender", "sex"],

        # Antropometría / PA (opcionales)
        "BMI": ["bmi", "imc"],
        "SBP": ["sbp", "sistolica", "ta_sis", "presion_sistolica"],
        "DBP": ["dbp", "diastolica", "ta_dia", "presion_diastolica"],

        # Dieta y macros
        "DR1TKCAL": ["dr1tkcal", "kcal", "calorias"],
        "pct_protein": ["pct_protein", "porc_proteina", "%proteina"],
        "pct_carb": ["pct_carb", "porc_carbos", "%carbohidratos"],
        "pct_fat": ["pct_fat", "porc_grasa", "%grasa"],
        "DR1TSUGR": ["dr1tsugr", "azucar_g", "azucares_g", "azucar"],
        "DR1TFIBE": ["dr1tfibe", "fibra_g", "fibra"],
        "DR1TSODI": ["dr1tsodi", "sodio_mg", "sodio"],

        # Hábitos
        "is_smoker": ["is_smoker", "fuma", "fumador"],
        "alcohol_days": ["alcohol_days", "alcohol_dias", "d_alcohol"],
        "phys_act_days": ["phys_act_days", "act_fisica_dias", "actividad_dias"],

        # Si recolectas peso/talla:
        "_peso": ["peso", "weight", "kg"],
        "_talla_cm": ["talla_cm", "altura_cm", "estatura_cm", "cm"],
        "_talla_m": ["talla_m", "altura_m", "estatura_m", "m"],
    }

    tmp_store = {}

    for feat, keys in aliases.items():
        if feat not in payload and not feat.startswith("_"):
            continue
        val = None
        for k in keys:
            if k in pool:
                val = pool[k]
                break
        if val is None:
            continue

        if feat == "RIAGENDR":
            payload[feat] = _map_sex(val)
        elif feat == "is_smoker":
            payload[feat] = _map_bool(val)
        elif feat.startswith("_"):
            tmp_store[feat] = _to_float(val)
        else:
            payload[feat] = _to_float(val)

    # 3) Si falta BMI pero hay peso/talla → calcular
    if "BMI" in payload and (np.isnan(payload["BMI"]) or payload["BMI"] is None):
        peso = tmp_store.get("_peso", np.nan)
        h_m = tmp_store.get("_talla_m", np.nan)
        if np.isnan(h_m) and not np.isnan(tmp_store.get("_talla_cm", np.nan)):
            h_m = tmp_store["_talla_cm"] / 100.0
        if not (np.isnan(peso) or np.isnan(h_m) or h_m == 0):
            payload["BMI"] = peso / (h_m ** 2)

    return payload


def _predict(payload: dict):
    if not MODEL_READY:
        return None, "Modelo no cargado. Verifica risk_profile_model.joblib/feature_list.txt"
    X = pd.DataFrame([{k: payload.get(k, np.nan) for k in FEATURES}], columns=FEATURES)
    pred = PIPE.predict(X)[0]
    proba = None
    try:
        pv = PIPE.predict_proba(X)[0]
        proba = {cls: float(p) for cls, p in zip(PIPE.classes_, pv)}
    except Exception:
        pass
    return {"risk_label": pred, "proba": proba}, None

def _recomendaciones(risk_label: str):
    if risk_label == "high":
        return [
            "Prioriza verduras, frutas y granos integrales en cada comida.",
            "Reduce bebidas azucaradas y ultraprocesados; limita sodio.",
            "Incrementa actividad física semanal de forma progresiva.",
            "Considera valoración profesional para un plan personalizado."
        ]
    if risk_label == "medium":
        return [
            "Aumenta fibra (legumbres, integrales) y reduce azúcares añadidos.",
            "Apunta a 150–300 min/semana de actividad moderada.",
            "Hidrátate y cuida porciones."
        ]
    return [
        "Buen perfil actual; mantén hábitos y monitoreo periódico.",
        "Varía fuentes de proteína y prioriza integrales."
    ]


# ============================================================
# View principal del asistente nutricional
# ============================================================
@csrf_exempt
def perfil_nutricional(request):
    """
    POST → devuelve perfil de riesgo (low/medium/high) y recomendaciones.
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

    payload = _build_payload_from_data(data, FEATURES)
    result, err = _predict(payload)
    if err:
        return HttpResponseBadRequest(err)

    risk = result["risk_label"]
    recs = _recomendaciones(risk)

    if risk == "high":
        mensaje = "Tu perfil sugiere un riesgo cardiometabólico ALTO. Te comparto consejos generales y considera valoración profesional."
    elif risk == "medium":
        mensaje = "Tu perfil sugiere un riesgo cardiometabólico MEDIO. Aquí van recomendaciones para mejorarlo."
    else:
        mensaje = "Tu perfil sugiere un riesgo cardiometabólico BAJO. Mantén tus hábitos y monitorea periódicamente."

    resp = {
        "ok": True,
        "risk_label": risk,
        "probabilities": result.get("proba"),
        "recommendations": recs,
        "mensaje": mensaje,
        "used_features": {k: payload.get(k) for k in FEATURES}
    }

    # Sanea NaN/Inf → None
    resp = _sanitize_json(resp)

    return JsonResponse(resp, status=200, json_dumps_params={"ensure_ascii": False})


def _sanitize_json(obj):
    import numpy as _np
    if isinstance(obj, dict):
        return {k: _sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_json(v) for v in obj]
    # numpy escalares
    if isinstance(obj, (_np.floating,)):
        val = float(obj)
        if _np.isnan(val) or _np.isinf(val):
            return None
        return val
    if isinstance(obj, (_np.integer,)):
        return int(obj)
    # floats nativos
    if isinstance(obj, float):
        if _np.isnan(obj) or _np.isinf(obj):
            return None
        return obj
    return obj
