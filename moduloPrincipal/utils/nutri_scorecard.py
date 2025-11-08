"""
Utilidades para el cuestionario nutricional de 10 ítems.

Cada pregunta aporta hasta 10 puntos (salvo suplementos con 5) y el puntaje
total se normaliza a una escala de 0 a 100 para clasificar:
    - 0  – 25  → saludable
    - 26 – 55  → moderado
    - 56 – 100 → alto

El módulo se usa tanto por la vista del asistente virtual como por los scripts
de análisis/entrenamiento.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Question:
    """Metadatos de cada pregunta del cuestionario."""

    id: str
    codigo_nhanes: str
    descripcion: str
    max_score: float


QUESTIONS: List[Question] = [
    Question(
        id="alcohol",
        codigo_nhanes="ALQ120Q",
        descripcion="Frecuencia de bebidas alcohólicas en los últimos 12 meses",
        max_score=10.0,
    ),
    Question(
        id="frutas",
        codigo_nhanes="DBQ223A",
        descripcion="Raciones diarias de fruta fresca",
        max_score=10.0,
    ),
    Question(
        id="verduras",
        codigo_nhanes="DBQ223B",
        descripcion="Raciones diarias de verduras",
        max_score=10.0,
    ),
    Question(
        id="bebidas_azucaradas",
        codigo_nhanes="DBQ223D",
        descripcion="Frecuencia semanal de bebidas azucaradas",
        max_score=10.0,
    ),
    Question(
        id="comida_rapida",
        codigo_nhanes="DBQ330",
        descripcion="Comidas rápidas/ultraprocesadas por semana",
        max_score=10.0,
    ),
    Question(
        id="agua",
        codigo_nhanes="DBQ223H",
        descripcion="Vasos de agua natural al día",
        max_score=10.0,
    ),
    Question(
        id="granos_integrales",
        codigo_nhanes="DBQ235C",
        descripcion="Consumo semanal de granos integrales",
        max_score=10.0,
    ),
    Question(
        id="sal_mesa",
        codigo_nhanes="CSQ240",
        descripcion="Frecuencia con la que se añade sal en la mesa",
        max_score=10.0,
    ),
    Question(
        id="suplementos",
        codigo_nhanes="DSQ010",
        descripcion="Uso habitual de suplementos vitamínicos/minerales",
        max_score=5.0,
    ),
    Question(
        id="desayuno",
        codigo_nhanes="DBQ010",
        descripcion="Días por semana que se desayuna",
        max_score=10.0,
    ),
]

TOTAL_RAW_MAX = sum(q.max_score for q in QUESTIONS)


def normalizar_scores(usuario_scores: Dict[str, float]) -> Tuple[float, Dict[str, Dict[str, float]]]:
    """
    Recibe un diccionario con los puntajes asignados por pregunta y devuelve
    el total bruto junto con un desglose por ítem (puntos y máximo).
    """
    detail: Dict[str, Dict[str, float]] = {}
    total = 0.0

    for question in QUESTIONS:
        value = usuario_scores.get(question.id, 0)
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0

        # Limitar al rango válido
        if value < 0:
            value = 0.0
        if value > question.max_score:
            value = question.max_score

        detail[question.id] = {"puntos": value, "maximo": question.max_score}
        total += value

    return total, detail


def clasificar(score_normalizado: float) -> str:
    """Asigna la etiqueta final según los umbrales científicos."""
    if score_normalizado <= 25:
        return "saludable"
    if score_normalizado <= 55:
        return "moderado"
    return "alto"


def evaluar_cuestionario(usuario_scores: Dict[str, float]) -> Dict[str, object]:
    """
    Calcula score normalizado, etiqueta y desglose a partir de los puntos
    proporcionados por el usuario (cada valor ya es el puntaje de la pregunta).

    Parameters
    ----------
    usuario_scores : dict
        Diccionario con los IDs de pregunta definidos en QUESTIONS.

    Returns
    -------
    dict
        {
            "score_raw": suma de puntos,
            "score_max": TOTAL_RAW_MAX,
            "score_normalizado": 0-100,
            "label": saludable/moderado/alto,
            "detalle": {pregunta: {"puntos": .., "maximo": ..}}
        }
    """
    total_raw, detail = normalizar_scores(usuario_scores)
    score_normalizado = (total_raw / TOTAL_RAW_MAX) * 100 if TOTAL_RAW_MAX else 0.0
    etiqueta = clasificar(score_normalizado)

    return {
        "score_raw": total_raw,
        "score_max": TOTAL_RAW_MAX,
        "score_normalizado": score_normalizado,
        "label": etiqueta,
        "detalle": detail,
    }


# ---------------------------------------------------------------------------
# Funciones auxiliares para documentación o análisis (no obligatorias)
# ---------------------------------------------------------------------------

def generar_resumen(respuestas: Dict[str, float]) -> Dict[str, object]:
    """
    Versión ligera que devuelve puntaje y etiqueta. Alias de evaluar_cuestionario.
    Se deja por compatibilidad con scripts antiguos.
    """
    return evaluar_cuestionario(respuestas)


__all__ = [
    "Question",
    "QUESTIONS",
    "TOTAL_RAW_MAX",
    "evaluar_cuestionario",
    "generar_resumen",
    "clasificar",
]

