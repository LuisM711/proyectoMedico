#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluador del cuestionario nutricional (10 ítems).

Se mantiene el nombre histórico del archivo, pero ahora el sistema se basa
exclusivamente en el score documentado en `nutri_scorecard`.
"""
from __future__ import annotations

from typing import Dict

from moduloPrincipal.utils.nutri_scorecard import evaluar_cuestionario


class SistemaCuestionario:
    """Envuelve `evaluar_cuestionario` y añade mensajes interpretativos."""

    def clasificar(self, respuestas: Dict[str, float]) -> Dict[str, object]:
        resumen = evaluar_cuestionario(respuestas)
        label = resumen["label"]

        mensajes = {
            "saludable": "Perfil de riesgo bajo. Mantén tus hábitos y monitoreo preventivo.",
            "moderado": "Riesgo intermedio. Ajusta hábitos nutricionales para revertir la tendencia.",
            "alto": "Riesgo alto. Busca acompañamiento profesional y realiza cambios inmediatos.",
        }
        
        return {
            "resumen": resumen,
            "interpretacion": mensajes[label],
        }


if __name__ == "__main__":
    ejemplo = {
        "alcohol": 7,
        "frutas": 3,
        "verduras": 7,
        "bebidas_azucaradas": 0,
        "comida_rapida": 4,
        "agua": 0,
        "granos_integrales": 3,
        "sal_mesa": 7,
        "suplementos": 5,
        "desayuno": 4,
    }

    sistema = SistemaCuestionario()
    resultado = sistema.clasificar(ejemplo)

    print("📊 Score normalizado:", f"{resultado['resumen']['score_normalizado']:.1f}/100")
    print("🏷️ Etiqueta:", resultado["resumen"]["label"])
    print("📝 Interpretación:", resultado["interpretacion"])
