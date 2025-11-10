"""
Entrenamiento del modelo Random Forest para el cuestionario nutricional de 10 ítems.

Este script transforma los módulos dietarios y de cuestionario de NHANES 2017-2018
en los puntajes del asistente virtual, etiqueta cada registro con la lógica científica
documentada en `nutri_scorecard` y entrena un clasificador de Random Forest.
Los artefactos generados se guardan en `model_artifacts/`.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from moduloPrincipal.utils.nutri_scorecard import QUESTIONS, evaluar_cuestionario


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "dataset"
ARTIFACTS_DIR = ROOT / "model_artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_NAMES = [q.id for q in QUESTIONS]






def _load_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    questionnaire = pd.read_csv(DATA_DIR / "questionnaire.csv")
    diet = pd.read_csv(DATA_DIR / "diet.csv")
    medications = pd.read_csv(DATA_DIR / "medications.csv", encoding="latin-1", low_memory=False)
    return questionnaire, diet, medications


def _build_supplement_map(medications: pd.DataFrame) -> Dict[int, bool]:
    if medications.empty or "RXDDRUG" not in medications.columns:
        return {}

    keywords = (
        "VITAMIN",
        "VIT ",
        "OMEGA",
        "FISH OIL",
        "CALCIUM",
        "MAGNESIUM",
        "ZINC",
        "MULTI",
        "B12",
        "FOLIC",
        "SELENIUM",
        "IRON",
        "MINERAL",
    )
    mask = medications["RXDDRUG"].fillna("").str.upper().str.contains("|".join(keywords))
    grouped = medications.assign(supp=mask).groupby("SEQN")["supp"].any()
    return grouped.to_dict()


def _alcohol_score(row: pd.Series) -> float:
    if row.get("ALQ101") == 2:
        return 0.0

    value = row.get("ALQ120Q")
    unit = row.get("ALQ120U")
    freq_week = 0.0

    if pd.notna(value):
        value = float(value)
        if unit == 1:  
            freq_week = value
        elif unit == 2:  
            freq_week = value / 4.345
        elif unit == 3:  
            freq_week = value / 52.0
        else:
            freq_week = value / 52.0
    elif pd.notna(row.get("DR1TALCO")) and row["DR1TALCO"] > 0:
        
        freq_week = 1.0

    if freq_week <= 0:
        return 0.0
    if freq_week <= 0.75:  
        return 3.0
    if freq_week <= 3.5:  
        return 7.0
    return 10.0


def _fruit_score(row: pd.Series) -> float:
    servings = row.get("DBQ197")
    if pd.notna(servings):
        if servings >= 3:
            return 0.0
        if servings >= 2:
            return 3.0
        if servings >= 1:
            return 7.0
        return 10.0

    vitamin_c = row.get("DR1TVC")
    if pd.isna(vitamin_c):
        return np.nan
    if vitamin_c >= 120:
        return 0.0
    if vitamin_c >= 60:
        return 3.0
    if vitamin_c >= 30:
        return 7.0
    return 10.0


def _vegetable_score(row: pd.Series) -> float:
    servings = row.get("DBD381")
    if pd.notna(servings):
        if servings >= 3:
            return 0.0
        if servings >= 2:
            return 3.0
        if servings >= 1:
            return 7.0
        return 10.0

    fiber = row.get("DR1TFIBE")
    if pd.isna(fiber):
        return np.nan
    if fiber >= 25:
        return 0.0
    if fiber >= 18:
        return 3.0
    if fiber >= 12:
        return 7.0
    return 10.0


def _sugary_drinks_score(row: pd.Series) -> float:
    sugar = row.get("DR1TSUGR")
    if pd.isna(sugar):
        return np.nan
    if sugar <= 25:
        return 0.0
    if sugar <= 50:
        return 3.0
    if sugar <= 75:
        return 7.0
    return 10.0


def _fast_food_score(row: pd.Series) -> float:
    sat_fat = row.get("DR1TSFAT")
    if pd.isna(sat_fat):
        return np.nan
    if sat_fat <= 15:
        return 0.0
    if sat_fat <= 25:
        return 4.0
    if sat_fat <= 35:
        return 7.0
    return 10.0


def _water_score(row: pd.Series) -> float:
    water = row.get("DR1TWS")
    if pd.isna(water):
        return np.nan
    liters = water / 1000.0
    if liters >= 1.5:
        return 0.0
    if liters >= 1.0:
        return 3.0
    if liters >= 0.5:
        return 7.0
    return 10.0


def _whole_grain_score(row: pd.Series) -> float:
    fiber = row.get("DR1TFIBE")
    carbs = row.get("DR1TCARB")
    if pd.isna(fiber) or pd.isna(carbs) or carbs <= 0:
        return np.nan
    ratio = fiber / carbs
    if ratio >= 0.15:
        return 0.0
    if ratio >= 0.10:
        return 3.0
    if ratio >= 0.05:
        return 7.0
    return 10.0


def _salt_score(row: pd.Series) -> float:
    sodium = row.get("DR1TSODI")
    if pd.isna(sodium):
        return np.nan
    if sodium <= 1500:
        return 0.0
    if sodium <= 2300:
        return 3.0
    if sodium <= 3000:
        return 7.0
    return 10.0


def _supplement_score(row: pd.Series) -> float:
    return 0.0 if bool(row.get("takes_supplement")) else 5.0


def _breakfast_score(row: pd.Series) -> float:
    breakfast = row.get("DBQ010")
    calories = row.get("DR1TKCAL")

    if breakfast == 1:
        if pd.notna(calories) and calories < 1200:
            return 4.0
        return 0.0
    if breakfast == 2:
        return 10.0
    if breakfast == 9:
        return 7.0
    return np.nan


SCORERS = {
    "alcohol": _alcohol_score,
    "frutas": _fruit_score,
    "verduras": _vegetable_score,
    "bebidas_azucaradas": _sugary_drinks_score,
    "comida_rapida": _fast_food_score,
    "agua": _water_score,
    "granos_integrales": _whole_grain_score,
    "sal_mesa": _salt_score,
    "suplementos": _supplement_score,
    "desayuno": _breakfast_score,
}


def construir_dataset() -> pd.DataFrame:
    questionnaire, diet, medications = _load_sources()

    base = questionnaire[
        ["SEQN", "ALQ101", "ALQ120Q", "ALQ120U", "DBQ197", "DBD381", "DBQ010"]
    ].copy()

    diet_cols = [
        "SEQN",
        "DR1TKCAL",
        "DR1TVC",
        "DR1TFIBE",
        "DR1TCARB",
        "DR1TSUGR",
        "DR1TSFAT",
        "DR1TSODI",
        "DR1TWS",
        "DR1TALCO",
    ]
    base = base.merge(diet[diet_cols], on="SEQN", how="left")

    supplement_map = _build_supplement_map(medications)
    base["takes_supplement"] = base["SEQN"].map(supplement_map).fillna(False)

    feature_rows = []
    for _, row in base.iterrows():
        features = {name: scorer(row) for name, scorer in SCORERS.items()}
        feature_rows.append(features)

    features_df = pd.DataFrame(feature_rows)
    dataset = pd.concat([base[["SEQN"]], features_df], axis=1)

    
    dataset.dropna(
        subset=[
            "alcohol",
            "frutas",
            "verduras",
            "bebidas_azucaradas",
            "comida_rapida",
            "sal_mesa",
        ],
        inplace=True,
    )

    
    for col in ["agua", "granos_integrales", "suplementos", "desayuno"]:
        if dataset[col].isna().all():
            dataset[col] = 5.0 if col == "suplementos" else 7.0
        else:
            dataset[col] = dataset[col].fillna(dataset[col].median())

    resultados = dataset[FEATURE_NAMES].apply(
        lambda row: evaluar_cuestionario(row.to_dict()), axis=1
    )
    dataset["label"] = resultados.apply(lambda r: r["label"])
    dataset["score_raw"] = resultados.apply(lambda r: r["score_raw"])
    dataset["score_normalizado"] = resultados.apply(lambda r: r["score_normalizado"])

    return dataset






def entrenar_modelo(
    df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
) -> tuple[Pipeline, Dict[str, Dict[str, float]], pd.Series, np.ndarray]:
    X = df[FEATURE_NAMES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    numeric_pipeline = Pipeline(
        steps=[
            ("imp", SimpleImputer(strategy="median")),
            ("sc", StandardScaler()),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, FEATURE_NAMES),
        ]
    )
    clf = RandomForestClassifier(
        n_estimators=400,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )
    model = Pipeline(steps=[("pre", preprocessor), ("clf", clf)])
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    metrics = {
        etiqueta: {
            "precision": round(stats.get("precision", 0.0), 4),
            "recall": round(stats.get("recall", 0.0), 4),
            "f1": round(stats.get("f1-score", 0.0), 4),
        }
        for etiqueta, stats in report.items()
        if etiqueta in ("saludable", "moderado", "alto")
    }
    metrics["accuracy"] = round(report.get("accuracy", 0.0), 4)
    return model, metrics, y_test, y_pred



def _write_feature_list():
    lines = "\n".join(FEATURE_NAMES)
    (ARTIFACTS_DIR / "feature_list.txt").write_text(lines + "\n", encoding="utf-8")


def _write_label_distribution(df: pd.DataFrame, metrics: Dict[str, Dict[str, float]]):
    label_counts = df["label"].value_counts().to_dict()
    label_proportions = {
        label: round(count / len(df), 3) for label, count in label_counts.items()
    }

    stats_globales = {
        "media": float(df["score_normalizado"].mean()),
        "mediana": float(df["score_normalizado"].median()),
        "desviacion_std": float(df["score_normalizado"].std()),
        "minimo": float(df["score_normalizado"].min()),
        "maximo": float(df["score_normalizado"].max()),
        "percentiles": {
            "p25": float(df["score_normalizado"].quantile(0.25)),
            "p75": float(df["score_normalizado"].quantile(0.75)),
            "p90": float(df["score_normalizado"].quantile(0.90)),
            "p95": float(df["score_normalizado"].quantile(0.95)),
        },
    }

    stats_por_etiqueta = {}
    for label, group in df.groupby("label"):
        stats_por_etiqueta[label] = {
            "media": float(group["score_normalizado"].mean()),
            "std": float(group["score_normalizado"].std()),
            "min": float(group["score_normalizado"].min()),
            "max": float(group["score_normalizado"].max()),
        }

    payload = {
        "n_muestras": len(df),
        "distribucion_etiquetas": label_counts,
        "proporcion_etiquetas": label_proportions,
        "estadisticas_score": stats_globales,
        "score_por_etiqueta": stats_por_etiqueta,
        "metricas_modelo": metrics,
    }

    with open(ARTIFACTS_DIR / "label_dist.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def _write_scientific_metadata(df: pd.DataFrame, metrics: Dict[str, Dict[str, float]]):
    ahora = datetime.now(timezone.utc).isoformat()
    metadata = {
        "cuestionario": {
            "items": FEATURE_NAMES,
            "puntaje_maximo": sum(q.max_score for q in QUESTIONS),
            "referencia": "NHANES 2017-2018 (Dietary + Questionnaire Modules)",
        },
        "dataset": {
            "muestras_total": len(df),
            "muestras_saludable": int((df["label"] == "saludable").sum()),
            "muestras_moderado": int((df["label"] == "moderado").sum()),
            "muestras_alto": int((df["label"] == "alto").sum()),
        },
        "modelo": {
            "tipo": "RandomForestClassifier",
            "n_estimators": 400,
            "min_samples_leaf": 2,
            "class_weight": "balanced",
            "random_state": 42,
            "fecha_entrenamiento": ahora,
            "metricas": metrics,
        },
    }

    with open(ARTIFACTS_DIR / "scientific_metadata.json", "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, ensure_ascii=False, indent=2)


def guardar_artefactos(model: Pipeline, df: pd.DataFrame, metrics: Dict[str, Dict[str, float]]):
    joblib.dump(model, ARTIFACTS_DIR / "risk_profile_model.joblib")
    joblib.dump(model.named_steps["pre"], ARTIFACTS_DIR / "preprocessor.joblib")
    _write_feature_list()
    _write_label_distribution(df, metrics)
    _write_scientific_metadata(df, metrics)






def main(test_size: float = 0.2, random_state: int = 42):
    print("[INFO] Cargando y preparando dataset NHANES 2017-2018...")
    dataset = construir_dataset()
    print(f"[INFO] Muestras utilizables: {len(dataset)}")

    print("[INFO] Entrenando Random Forest...")
    model, metrics, y_test, y_pred = entrenar_modelo(
        dataset, test_size=test_size, random_state=random_state
    )

    print("\n=== METRICAS DE VALIDACION ===")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    for etiqueta in ("saludable", "moderado", "alto"):
        stats = metrics[etiqueta]
        print(
            f"{etiqueta.capitalize():>10} -> Precision: {stats['precision']:.4f} | "
            f"Recall: {stats['recall']:.4f} | F1: {stats['f1']:.4f}"
        )

    print("\nMatriz de confusion (saludable, moderado, alto):")
    labels_order = ["saludable", "moderado", "alto"]
    cm = confusion_matrix(y_test, y_pred, labels=labels_order)
    print(pd.DataFrame(cm, index=labels_order, columns=labels_order))

    print("\n[INFO] Guardando artefactos de modelo en:", ARTIFACTS_DIR)
    guardar_artefactos(model, dataset, metrics)
    print("[INFO] Entrenamiento completado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Entrena el Random Forest del asistente virtual nutricional usando NHANES 2017-2018."
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proporción del conjunto de prueba (default: 0.2).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semilla aleatoria para reproducibilidad (default: 42).",
    )
    args = parser.parse_args()
    main(test_size=args.test_size, random_state=args.seed)
