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
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import learning_curve, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Para balanceo de datos
try:
    from imblearn.over_sampling import RandomOverSampler, SMOTE
    IMBALANCED_LEARN_AVAILABLE = True
except ImportError:
    IMBALANCED_LEARN_AVAILABLE = False
    print("[WARNING] imbalanced-learn no está instalado. Usando oversampling manual.")

from moduloPrincipal.utils.nutri_scorecard import QUESTIONS, evaluar_cuestionario

# Configuración de matplotlib para español
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (12, 8)


ROOT = Path(__file__).resolve().parent.parent  # Subir un nivel desde scripts/ a tesis/
DATA_DIR = ROOT / "dataset"
ARTIFACTS_DIR = ROOT / "model_artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
GRAPHS_DIR = ROOT / "graficas_resultados"
GRAPHS_DIR.mkdir(exist_ok=True)

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






def _balancear_datos(X_train, y_train, random_state: int = 42):
    """Balancea los datos de entrenamiento usando oversampling."""
    if IMBALANCED_LEARN_AVAILABLE:
        # Usar SMOTE para balancear (mejor que RandomOverSampler)
        try:
            smote = SMOTE(random_state=random_state, k_neighbors=1)
            X_balanced, y_balanced = smote.fit_resample(X_train, y_train)
            # Convertir a DataFrame/Series si vienen como arrays
            if isinstance(X_balanced, np.ndarray):
                X_balanced = pd.DataFrame(X_balanced, columns=X_train.columns)
            if isinstance(y_balanced, np.ndarray):
                y_balanced = pd.Series(y_balanced, name=y_train.name)
            return X_balanced, y_balanced
        except Exception:
            # Si SMOTE falla (pocos vecinos), usar RandomOverSampler
            ros = RandomOverSampler(random_state=random_state)
            X_balanced, y_balanced = ros.fit_resample(X_train, y_train)
            # Convertir a DataFrame/Series si vienen como arrays
            if isinstance(X_balanced, np.ndarray):
                X_balanced = pd.DataFrame(X_balanced, columns=X_train.columns)
            if isinstance(y_balanced, np.ndarray):
                y_balanced = pd.Series(y_balanced, name=y_train.name)
            return X_balanced, y_balanced
    else:
        # Oversampling manual simple
        from collections import Counter
        counter = Counter(y_train)
        max_count = max(counter.values())
        
        X_resampled_list = []
        y_resampled_list = []
        
        for label in counter.keys():
            X_class = X_train[y_train == label]
            y_class = y_train[y_train == label]
            n_samples = len(X_class)
            n_repeats = max_count // n_samples
            n_extra = max_count % n_samples
            
            # Repetir muestras
            for _ in range(n_repeats):
                X_resampled_list.append(X_class)
                y_resampled_list.append(y_class)
            
            # Agregar muestras extra si es necesario
            if n_extra > 0:
                X_resampled_list.append(X_class.iloc[:n_extra])
                y_resampled_list.append(y_class.iloc[:n_extra])
        
        X_balanced = pd.concat(X_resampled_list, ignore_index=True)
        y_balanced = pd.concat(y_resampled_list, ignore_index=True)
        
        return X_balanced, y_balanced


def entrenar_modelo(
    df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42, balancear: bool = True
) -> tuple[Pipeline, Dict[str, Dict[str, float]], pd.Series, np.ndarray, pd.DataFrame, pd.DataFrame, pd.Series]:
    X = df[FEATURE_NAMES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Balancear datos de entrenamiento
    if balancear:
        print("[INFO] Balanceando datos de entrenamiento...")
        X_train_balanced, y_train_balanced = _balancear_datos(X_train, y_train, random_state)
        print(f"[INFO] Muestras después del balanceo: {len(X_train_balanced)} (original: {len(X_train)})")
        print(f"[INFO] Distribución balanceada: {y_train_balanced.value_counts().to_dict()}")
        # Usar datos balanceados para entrenar
        X_train = X_train_balanced
        y_train = y_train_balanced
    else:
        X_train_balanced = None
        y_train_balanced = None
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
    return model, metrics, y_test, y_pred, X_test, X_train_balanced, y_train_balanced



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


def _write_tablas_latex(df: pd.DataFrame, metrics: Dict[str, Dict[str, float]]):
    """Genera tablas en formato LaTeX para la tesis."""
    from datetime import datetime
    
    # Calcular métricas promedio (macro-average)
    precision_avg = (metrics['alto']['precision'] + metrics['moderado']['precision'] + metrics['saludable']['precision']) / 3
    recall_avg = (metrics['alto']['recall'] + metrics['moderado']['recall'] + metrics['saludable']['recall']) / 3
    f1_avg = (metrics['alto']['f1'] + metrics['moderado']['f1'] + metrics['saludable']['f1']) / 3
    
    # Tabla 1: Resultados en Entrenamiento
    tabla1_latex = """
\\begin{{table}}[h]
\\centering
\\caption{{Resultados en Entrenamiento del Modelo Random Forest}}
\\label{{tab:resultados_entrenamiento}}
\\begin{{tabular}}{{|l|c|c|c|c|}}
\\hline
\\textbf{{Métrica}} & \\textbf{{Alto}} & \\textbf{{Moderado}} & \\textbf{{Saludable}} & \\textbf{{Promedio}} \\\\
\\hline
\\textbf{{Precisión}} & {:.2f}\\% & {:.2f}\\% & {:.2f}\\% & {:.2f}\\% \\\\
\\hline
\\textbf{{Recall}} & {:.2f}\\% & {:.2f}\\% & {:.2f}\\% & {:.2f}\\% \\\\
\\hline
\\textbf{{F1-Score}} & {:.2f}\\% & {:.2f}\\% & {:.2f}\\% & {:.2f}\\% \\\\
\\hline
\\textbf{{Accuracy Global}} & \\multicolumn{{4}}{{c|}}{{{:.2f}\\%}} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
""".format(
        metrics['alto']['precision'] * 100,
        metrics['moderado']['precision'] * 100,
        metrics['saludable']['precision'] * 100,
        precision_avg * 100,
        metrics['alto']['recall'] * 100,
        metrics['moderado']['recall'] * 100,
        metrics['saludable']['recall'] * 100,
        recall_avg * 100,
        metrics['alto']['f1'] * 100,
        metrics['moderado']['f1'] * 100,
        metrics['saludable']['f1'] * 100,
        f1_avg * 100,
        metrics['accuracy'] * 100
    )
    
    # Tabla 2: Configuración del Modelo
    modelo_info = {
        'n_estimators': 400,
        'min_samples_leaf': 2,
        'random_state': 42
    }
    
    alto_count = int((df["label"] == "alto").sum())
    moderado_count = int((df["label"] == "moderado").sum())
    saludable_count = int((df["label"] == "saludable").sum())
    total = len(df)
    
    tabla2_latex = """
\\begin{{table}}[h]
\\centering
\\caption{{Configuración del Modelo y Características del Dataset}}
\\label{{tab:configuracion_modelo}}
\\begin{{tabular}}{{|l|c|}}
\\hline
\\textbf{{Parámetro}} & \\textbf{{Valor}} \\\\
\\hline
\\textbf{{Tipo de Modelo}} & RandomForestClassifier \\\\
\\hline
\\textbf{{Número de Estimadores}} & {} \\\\
\\hline
\\textbf{{min\\_samples\\_leaf}} & {} \\\\
\\hline
\\textbf{{class\\_weight}} & balanced \\\\
\\hline
\\textbf{{random\\_state}} & {} \\\\
\\hline
\\textbf{{Total de Muestras}} & {:,} \\\\
\\hline
\\textbf{{Muestras - Alto}} & {:,} ({:.1f}\\%%) \\\\
\\hline
\\textbf{{Muestras - Moderado}} & {:,} ({:.1f}\\%%) \\\\
\\hline
\\textbf{{Muestras - Saludable}} & {} ({:.2f}\\%%) \\\\
\\hline
\\textbf{{División Train/Test}} & 80\\% / 20\\% \\\\
\\hline
\\textbf{{Fuente de Datos}} & NHANES 2017-2018 \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
""".format(
        modelo_info['n_estimators'],
        modelo_info['min_samples_leaf'],
        modelo_info['random_state'],
        total,
        alto_count,
        (alto_count / total) * 100,
        moderado_count,
        (moderado_count / total) * 100,
        saludable_count,
        (saludable_count / total) * 100
    )
    
    # Tabla 3: Resultados con código en Python
    tabla3_latex = """
\\begin{{table}}[h]
\\centering
\\caption{{Resultados de Métricas por Clase del Modelo Random Forest}}
\\label{{tab:metricas_python}}
\\begin{{tabular}}{{|l|c|c|c|}}
\\hline
\\textbf{{Clase}} & \\textbf{{Precisión}} & \\textbf{{Recall}} & \\textbf{{F1-Score}} \\\\
\\hline
Alto & {:.2f}\\% & {:.2f}\\% & {:.2f}\\% \\\\
\\hline
Moderado & {:.2f}\\% & {:.2f}\\% & {:.2f}\\% \\\\
\\hline
Saludable & {:.2f}\\% & {:.2f}\\% & {:.2f}\\% \\\\
\\hline
\\textbf{{Promedio (Macro)}} & \\textbf{{{:.2f}\\%}} & \\textbf{{{:.2f}\\%}} & \\textbf{{{:.2f}\\%}} \\\\
\\hline
\\textbf{{Accuracy Global}} & \\multicolumn{{3}}{{c|}}{{{:.2f}\\%}} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
""".format(
        metrics['alto']['precision'] * 100,
        metrics['alto']['recall'] * 100,
        metrics['alto']['f1'] * 100,
        metrics['moderado']['precision'] * 100,
        metrics['moderado']['recall'] * 100,
        metrics['moderado']['f1'] * 100,
        metrics['saludable']['precision'] * 100,
        metrics['saludable']['recall'] * 100,
        metrics['saludable']['f1'] * 100,
        precision_avg * 100,
        recall_avg * 100,
        f1_avg * 100,
        metrics['accuracy'] * 100
    )
    
    # Guardar en markdowns/
    MARKDOWNS_DIR = ROOT / "markdowns"
    MARKDOWNS_DIR.mkdir(exist_ok=True)
    output_file = MARKDOWNS_DIR / "tablas_resultados_latex.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("TABLAS DE RESULTADOS - MODELO RANDOM FOREST\n")
        f.write("Generado: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n\n")
        f.write("TABLA 1: RESULTADOS EN ENTRENAMIENTO\n")
        f.write("-" * 80 + "\n")
        f.write(tabla1_latex)
        f.write("\n\n" + "=" * 80 + "\n\n")
        f.write("TABLA 2: CONFIGURACIÓN DEL MODELO Y DATASET\n")
        f.write("-" * 80 + "\n")
        f.write(tabla2_latex)
        f.write("\n\n" + "=" * 80 + "\n\n")
        f.write("TABLA 3: RESULTADOS CON CÓDIGO EN PYTHON\n")
        f.write("-" * 80 + "\n")
        f.write(tabla3_latex)
    
    print(f"[INFO] Tablas LaTeX guardadas en: {output_file}")


def _generar_graficas(model: Pipeline, df: pd.DataFrame, metrics: Dict[str, Dict[str, float]], 
                     X_test, y_test, y_pred, X_train_balanced=None, y_train_balanced=None):
    """Genera todas las gráficas de resultados del modelo."""
    print("\n[INFO] Generando gráficas de resultados...")
    
    # GRAFICA 1: Distribución del Dataset
    print("  [1/5] Distribución del dataset...")
    
    # Si hay datos balanceados, usarlos; si no, usar distribución original
    if X_train_balanced is not None and y_train_balanced is not None:
        # Usar distribución balanceada
        train_dist = y_train_balanced.value_counts()
        alto_train = train_dist.get("alto", 0)
        moderado_train = train_dist.get("moderado", 0)
        saludable_train = train_dist.get("saludable", 0)
        train_size = len(y_train_balanced)
    else:
        # Usar distribución original
        total = len(df)
        train_size = int(total * 0.8)
        alto_train = int((df["label"] == "alto").sum() * 0.8)
        moderado_train = int((df["label"] == "moderado").sum() * 0.8)
        saludable_train = int((df["label"] == "saludable").sum() * 0.8)
    
    # Distribución de prueba (siempre original, no se balancea)
    test_dist = y_test.value_counts()
    alto_test = test_dist.get("alto", 0)
    moderado_test = test_dist.get("moderado", 0)
    saludable_test = test_dist.get("saludable", 0)
    test_size = len(y_test)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    clases = ['Alto', 'Moderado', 'Saludable']
    train_counts = [alto_train, moderado_train, saludable_train]
    test_counts = [alto_test, moderado_test, saludable_test]
    colors = ['#dc3545', '#ffc107', '#28a745']
    
    # Izquierda: Distribución en pruebas (desbalanceada)
    bars1 = ax1.bar(clases, test_counts, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax1.set_title('Distribución en pruebas', fontsize=14, fontweight='bold', pad=20)
    ax1.set_ylabel('Número de muestras', fontsize=12)
    ax1.set_xlabel('Clase', fontsize=12)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, count in zip(bars1, test_counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}\n({count/test_size*100:.1f}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Derecha: Distribución en entrenamiento (balanceada)
    bars2 = ax2.bar(clases, train_counts, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.set_title('Distribución en entrenamiento', fontsize=14, fontweight='bold', pad=20)
    ax2.set_ylabel('Número de muestras', fontsize=12)
    ax2.set_xlabel('Clase', fontsize=12)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, count in zip(bars2, train_counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}\n({count/train_size*100:.1f}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / '01_distribucion_dataset.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # GRAFICA 2: Matriz de Confusión
    print("  [2/5] Matriz de confusión...")
    labels = ['saludable', 'moderado', 'alto']
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           xticklabels=labels, yticklabels=labels,
           title='Matriz de confusión',
           ylabel='Etiqueta real',
           xlabel='Etiqueta predicha')
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                   ha="center", va="center",
                   color="white" if cm[i, j] > thresh else "black",
                   fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / '02_matriz_confusion.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # GRAFICA 3: Métricas por Clase
    print("  [3/5] Métricas por clase...")
    precision = [metrics['alto']['precision']*100, metrics['moderado']['precision']*100, metrics['saludable']['precision']*100]
    recall = [metrics['alto']['recall']*100, metrics['moderado']['recall']*100, metrics['saludable']['recall']*100]
    f1 = [metrics['alto']['f1']*100, metrics['moderado']['f1']*100, metrics['saludable']['f1']*100]
    
    x = np.arange(len(clases))
    width = 0.25
    fig, ax = plt.subplots(figsize=(12, 7))
    bars1 = ax.bar(x - width, precision, width, label='Precisión', color='#3498db', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x, recall, width, label='Recall', color='#2ecc71', alpha=0.8, edgecolor='black')
    bars3 = ax.bar(x + width, f1, width, label='F1-Score', color='#e74c3c', alpha=0.8, edgecolor='black')
    ax.set_xlabel('Clase', fontsize=12, fontweight='bold')
    ax.set_ylabel('Porcentaje (%)', fontsize=12, fontweight='bold')
    ax.set_title('Métricas de evaluación por clase', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(clases)
    ax.legend(loc='upper left', fontsize=11)
    ax.set_ylim([0, 105])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / '03_metricas_por_clase.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # GRAFICA 4: Importancia de Características
    print("  [4/5] Importancia de características...")
    rf_model = model.named_steps['clf']
    importances = rf_model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'feature': FEATURE_NAMES,
        'importance': importances
    }).sort_values('importance', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    y_pos = np.arange(len(feature_importance_df))
    bars = ax.barh(y_pos, feature_importance_df['importance'], 
                   color='#9b59b6', alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(feature_importance_df['feature'])
    ax.set_xlabel('Importancia', fontsize=12, fontweight='bold')
    ax.set_title('Importancia de características (Random Forest)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    for bar, imp in zip(bars, feature_importance_df['importance']):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
               f'{imp:.3f}',
               ha='left', va='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / '04_importancia_caracteristicas.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # GRAFICA 5: Curvas de Aprendizaje
    print("  [5/5] Curvas de aprendizaje...")
    X = df[FEATURE_NAMES]
    y = df["label"]
    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y, cv=5, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='accuracy'
    )
    train_mean = np.mean(train_scores, axis=1) * 100
    train_std = np.std(train_scores, axis=1) * 100
    val_mean = np.mean(val_scores, axis=1) * 100
    val_std = np.std(val_scores, axis=1) * 100
    
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(train_sizes, train_mean, 'o-', color='#3498db', label='Accuracy entrenamiento', 
           linewidth=2, markersize=8)
    ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, 
                   alpha=0.2, color='#3498db')
    ax.plot(train_sizes, val_mean, 's-', color='#e74c3c', label='Accuracy validación', 
           linewidth=2, markersize=8)
    ax.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, 
                   alpha=0.2, color='#e74c3c')
    ax.set_xlabel('Tamaño del conjunto de entrenamiento', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Curvas de aprendizaje', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='lower right', fontsize=11)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_ylim([85, 100])
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / '05_curvas_aprendizaje.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[INFO] Gráficas guardadas en: {GRAPHS_DIR}")


def guardar_artefactos(model: Pipeline, df: pd.DataFrame, metrics: Dict[str, Dict[str, float]],
                      X_test, y_test, y_pred, X_train_balanced=None, y_train_balanced=None):
    joblib.dump(model, ARTIFACTS_DIR / "risk_profile_model.joblib")
    joblib.dump(model.named_steps["pre"], ARTIFACTS_DIR / "preprocessor.joblib")
    _write_feature_list()
    _write_label_distribution(df, metrics)
    _write_scientific_metadata(df, metrics)
    _write_tablas_latex(df, metrics)
    _generar_graficas(model, df, metrics, X_test, y_test, y_pred, X_train_balanced, y_train_balanced)






def main(test_size: float = 0.2, random_state: int = 42):
    print("[INFO] Cargando y preparando dataset NHANES 2017-2018...")
    dataset = construir_dataset()
    print(f"[INFO] Muestras utilizables: {len(dataset)}")

    print("[INFO] Entrenando Random Forest...")
    model, metrics, y_test, y_pred, X_test, X_train_balanced, y_train_balanced = entrenar_modelo(
        dataset, test_size=test_size, random_state=random_state, balancear=True
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
    guardar_artefactos(model, dataset, metrics, X_test, y_test, y_pred, X_train_balanced, y_train_balanced)
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
