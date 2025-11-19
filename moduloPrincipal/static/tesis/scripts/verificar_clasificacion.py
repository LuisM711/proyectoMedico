#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación rápida del cuestionario nutricional de 10 ítems.
"""

from moduloPrincipal.utils.nutri_scorecard import evaluar_cuestionario


def mostrar_detalle(titulo, caso):
    print("\n", titulo)
    print("-" * len(titulo))
    resultado = evaluar_cuestionario(caso)
    print(f"Score normalizado : {resultado['score_normalizado']:.1f}/100")
    print(f"Etiqueta          : {resultado['label']}")
    for clave, info in resultado["detalle"].items():
        print(f"  · {clave:18s} → {info['puntos']:.1f} / {info['maximo']}")
    return resultado


if __name__ == "__main__":
    caso_saludable = {
        "alcohol": 0,
        "frutas": 0,
        "verduras": 0,
        "bebidas_azucaradas": 0,
        "comida_rapida": 0,
        "agua": 0,
        "granos_integrales": 0,
        "sal_mesa": 0,
        "suplementos": 0,
        "desayuno": 0,
    }

    caso_riesgo = {
        "alcohol": 10,
        "frutas": 10,
        "verduras": 7,
        "bebidas_azucaradas": 10,
        "comida_rapida": 10,
        "agua": 10,
        "granos_integrales": 10,
        "sal_mesa": 10,
        "suplementos": 5,
        "desayuno": 10,
    }

    print("🔬 Verificación del cuestionario nutricional\n")
    resultado_saludable = mostrar_detalle("Caso A: Perfil saludable", caso_saludable)
    resultado_riesgo = mostrar_detalle("Caso B: Perfil en alto riesgo", caso_riesgo)

    assert resultado_saludable["label"] == "saludable", "El caso A debe ser saludable"
    assert resultado_riesgo["label"] == "alto", "El caso B debe ser alto"

    print("\n✅ Clasificaciones verificadas correctamente.")
