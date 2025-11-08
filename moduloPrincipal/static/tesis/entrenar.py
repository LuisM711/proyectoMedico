"""
Generador de estadísticas para el cuestionario nutricional de 10 ítems.

El algoritmo científico se basa únicamente en los puntajes del cuestionario,
por lo que ya no se entrena un modelo de machine learning. En su lugar,
simulamos respuestas poblacionales (Monte Carlo) para documentar la
distribución esperada de etiquetas y scores.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from moduloPrincipal.utils.nutri_scorecard import QUESTIONS, evaluar_cuestionario


HERE = Path(__file__).resolve()
ARTIFACTS_DIR = HERE.parent / "model_artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


# Probabilidades heurísticas (pueden ajustarse con datos reales)
SAMPLE_SPACE = {
    "alcohol": ([0, 3, 7, 10], [0.45, 0.25, 0.2, 0.1]),
    "frutas": ([0, 3, 7, 10], [0.2, 0.35, 0.3, 0.15]),
    "verduras": ([0, 3, 7, 10], [0.18, 0.32, 0.34, 0.16]),
    "bebidas_azucaradas": ([0, 3, 7, 10], [0.25, 0.4, 0.25, 0.1]),
    "comida_rapida": ([0, 4, 7, 10], [0.2, 0.45, 0.25, 0.1]),
    "agua": ([0, 3, 7, 10], [0.35, 0.3, 0.25, 0.1]),
    "granos_integrales": ([0, 3, 7, 10], [0.22, 0.33, 0.3, 0.15]),
    "sal_mesa": ([0, 3, 7, 10], [0.4, 0.3, 0.2, 0.1]),
    "suplementos": ([0, 2, 5], [0.35, 0.3, 0.35]),
    "desayuno": ([0, 4, 7, 10], [0.45, 0.25, 0.2, 0.1]),
}


def generar_muestra(n: int, seed: int = 42):
    rng = np.random.default_rng(seed)
    resultados = []
    for _ in range(n):
        respuestas = {
            q.id: float(rng.choice(SAMPLE_SPACE[q.id][0], p=SAMPLE_SPACE[q.id][1]))
            for q in QUESTIONS
        }
        resultados.append(evaluar_cuestionario(respuestas))
    return resultados


def resumir(resultados):
    scores = np.array([res["score_normalizado"] for res in resultados])
    etiquetas = [res["label"] for res in resultados]

    resumen = {
        "n": len(resultados),
        "estadisticas_score": {
            "media": float(np.mean(scores)),
            "mediana": float(np.median(scores)),
            "desviacion_std": float(np.std(scores)),
            "minimo": float(np.min(scores)),
            "maximo": float(np.max(scores)),
            "p25": float(np.percentile(scores, 25)),
            "p75": float(np.percentile(scores, 75)),
            "p90": float(np.percentile(scores, 90)),
            "p95": float(np.percentile(scores, 95)),
        },
        "distribucion_etiquetas": {},
    }

    total = len(etiquetas)
    for etiqueta in ("saludable", "moderado", "alto"):
        conteo = etiquetas.count(etiqueta)
        resumen["distribucion_etiquetas"][etiqueta] = {
            "conteo": conteo,
            "proporcion": round(conteo / total, 3),
        }

    return resumen


def guardar(resumen, muestras):
    with open(ARTIFACTS_DIR / "score_distribution.json", "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, ensure_ascii=False, indent=2)

    with open(ARTIFACTS_DIR / "simulated_samples.json", "w", encoding="utf-8") as fh:
        json.dump(
            [
                {
                    "score_normalizado": round(m["score_normalizado"], 2),
                    "label": m["label"],
                    "detalle": m["detalle"],
                }
                for m in muestras[:200]
            ],
            fh,
            ensure_ascii=False,
            indent=2,
        )


def main(n: int = 10000, seed: int = 42):
    print("📊 Generando muestras sintéticas del cuestionario (n=%d)..." % n)
    muestras = generar_muestra(n, seed)
    resumen = resumir(muestras)
    guardar(resumen, muestras)

    print("\n=== DISTRIBUCIÓN DE SCORES (0-100) ===")
    stats = resumen["estadisticas_score"]
    print(f"Media ± DE : {stats['media']:.2f} ± {stats['desviacion_std']:.2f}")
    print(f"Mediana    : {stats['mediana']:.2f}")
    print(f"Rango      : [{stats['minimo']:.2f}, {stats['maximo']:.2f}]")
    print(f"P25 / P75  : {stats['p25']:.2f} / {stats['p75']:.2f}")
    print(f"P90 / P95  : {stats['p90']:.2f} / {stats['p95']:.2f}")

    print("\n=== ETIQUETAS ESPERADAS ===")
    for etiqueta, datos in resumen["distribucion_etiquetas"].items():
        print(f"{etiqueta.upper():>10}: {datos['conteo']:>5} muestras ({datos['proporcion']*100:5.1f}%)")

    print(f"\nArtefactos guardados en {ARTIFACTS_DIR.as_posix()}")
    print(" - score_distribution.json  (estadísticas agregadas)")
    print(" - simulated_samples.json   (primeras 200 simulaciones para auditoría)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simula respuestas para el cuestionario nutricional y documenta la distribución de scores.")
    parser.add_argument("--n", type=int, default=10000, help="Número de simulaciones (default: 10000).")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria (default: 42).")
    args = parser.parse_args()
    main(n=args.n, seed=args.seed)
