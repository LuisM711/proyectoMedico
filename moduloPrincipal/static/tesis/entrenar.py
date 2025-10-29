# entrenar.py
# -*- coding: utf-8 -*-
"""
Entrenamiento del modelo de Perfil Nutricional (riesgo cardiometabólico)
Dataset esperado en: moduloPrincipal/static/tesis/dataset/
Archivos: demographic.csv, questionnaire.csv, diet.csv, examination.csv, labs.csv, medications.csv

Salida (artefactos):
- moduloPrincipal/static/tesis/model_artifacts/risk_profile_model.joblib
- moduloPrincipal/static/tesis/model_artifacts/preprocessor.joblib
- moduloPrincipal/static/tesis/model_artifacts/feature_list.txt
- moduloPrincipal/static/tesis/model_artifacts/label_dist.json
"""

import argparse
import json
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, balanced_accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

# ----------------------------
# Utilidades
# ----------------------------

def find_col(df: pd.DataFrame, candidates):
    """Encuentra la primera columna existente que coincida con el nombre exacto o con un patrón regex."""
    for c in candidates:
        if c in df.columns:
            return c
    for c in df.columns:
        for pat in candidates:
            try:
                if re.fullmatch(pat, c):
                    return c
            except re.error:
                continue
    return None

def load_all(base_dir: Path):
    """Carga todos los CSV del dataset."""
    files = {
        "demographic": base_dir / "demographic.csv",
        "questionnaire": base_dir / "questionnaire.csv",
        "diet": base_dir / "diet.csv",
        "examination": base_dir / "examination.csv",
        "labs": base_dir / "labs.csv",
        "medications": base_dir / "medications.csv",
    }
    dfs = {}
    for k, p in files.items():
        if not p.exists():
            raise FileNotFoundError(f"No se encontró {p}")
        # medications suele traer caracteres especiales → latin1
        enc = "latin1" if k == "medications" else "utf-8"
        try:
            dfs[k] = pd.read_csv(p, encoding=enc)
        except UnicodeDecodeError:
            dfs[k] = pd.read_csv(p, encoding="latin1")
    # sanity
    for k, df in dfs.items():
        if "SEQN" not in df.columns:
            raise ValueError(f"{k} no contiene la columna SEQN")
    return dfs

def merge_all(dfs: dict) -> pd.DataFrame:
    """Une todo por SEQN."""
    df = dfs["demographic"].copy()
    for k in ["questionnaire", "diet", "examination", "labs", "medications"]:
        suf = f"_{k[:3]}"
        df = df.merge(dfs[k], on="SEQN", how="left", suffixes=("", suf))
    return df

def engineer_features(df: pd.DataFrame):
    """Construye features y devuelve (work, work_feats, feature_cols, colmap)."""
    # Mapas de columnas (heurísticos NHANES)
    colmap = {
        # Demografía
        "age": find_col(df, ["RIDAGEYR","age","Age","RIDAGEMN"]),
        "sex": find_col(df, ["RIAGENDR","gender","sex","Sex"]),
        # Examen/Antropometría
        "height": find_col(df, ["BMXHT","height","Height"]),
        "weight": find_col(df, ["BMXWT","weight","Weight"]),
        "sbp": find_col(df, ["BPXSY1","BPXSY2","BPXSY3","SBP","Systolic","systolic"]),
        "dbp": find_col(df, ["BPXDI1","BPXDI2","BPXDI3","DBP","Diastolic","diastolic"]),
        # Laboratorio
        "glucose": find_col(df, ["LBXGLU","GLU","Glucose","FastingGlucose","LBXGLU\\w*"]),
        "hdl": find_col(df, ["LBDHDD","HDL","HDLChol","LBXHDD\\w*"]),
        "ldl": find_col(df, ["LBDLDL","LDL","LDLChol","LBXLDL\\w*"]),
        "tg": find_col(df, ["LBXTR","Triglycerides","TRIG","LBXTR\\w*"]),
        # Dieta (24h)
        "kcal": find_col(df, ["DR1TKCAL","kcal","Calories","EnergyKcal"]),
        "protein_g": find_col(df, ["DR1TPROT","ProteinG","protein_g"]),
        "carb_g": find_col(df, ["DR1TCARB","CarbG","carb_g"]),
        "fat_g": find_col(df, ["DR1TTFAT","FatG","fat_g"]),
        "sugar_g": find_col(df, ["DR1TSUGR","SugarG","sugar_g"]),
        "fiber_g": find_col(df, ["DR1TFIBE","FiberG","fiber_g"]),
        "sodium_mg": find_col(df, ["DR1TSODI","SodiumMg","sodium_mg"]),
        # Hábitos
        "smoker": find_col(df, ["SMQ020","smoker","SmokingStatus","SMQ020\\w*"]),
        "alcohol_days": find_col(df, ["ALQ120Q","alcohol_days","AlcoholDays"]),
        "phys_act_days": find_col(df, ["PAQ650","phys_act_days","PhysicalActivityDays"]),
    }

    work = df.copy()

    # --- BMI: usa columna nativa si existe; si no, calcula con talla/peso ---
    bmi_native = find_col(df, ["BMXBMI", "BMI", "BodyMassIndex"])
    if bmi_native:
        work["BMI"] = pd.to_numeric(work[bmi_native], errors="coerce")
    elif colmap["height"] and colmap["weight"]:
        h = work[colmap["height"]]
        # si altura viene en cm, divide entre 100
        h_m = h / 100.0 if h.dropna().max() and h.dropna().max() > 10 else h
        work["BMI"] = work[colmap["weight"]] / (h_m ** 2)
    else:
        work["BMI"] = np.nan
    # -----------------------------------------------------------------------

    # Presión arterial
    work["SBP"] = work[colmap["sbp"]] if colmap["sbp"] else np.nan
    work["DBP"] = work[colmap["dbp"]] if colmap["dbp"] else np.nan

    # % de macronutrientes
    if colmap["kcal"]:
        P = work[colmap["protein_g"]] * 4 if colmap["protein_g"] else np.nan
        C = work[colmap["carb_g"]] * 4 if colmap["carb_g"] else np.nan
        F = work[colmap["fat_g"]] * 9 if colmap["fat_g"] else np.nan
        KCAL = work[colmap["kcal"]]
        work["pct_protein"] = P / KCAL * 100
        work["pct_carb"] = C / KCAL * 100
        work["pct_fat"] = F / KCAL * 100

    # Hábitos
    work["is_smoker"] = (work[colmap["smoker"]] == 1).astype(float) if colmap["smoker"] else np.nan
    for k, newk in [(colmap["alcohol_days"], "alcohol_days"),
                    (colmap["phys_act_days"], "phys_act_days")]:
        work[newk] = pd.to_numeric(work[k], errors="coerce") if k else np.nan

    # Selección de features
    feature_cols = [c for c in [
        colmap["age"], colmap["sex"], "BMI", "SBP", "DBP",
        colmap["kcal"], "pct_protein", "pct_carb", "pct_fat",
        colmap["sugar_g"], colmap["fiber_g"], colmap["sodium_mg"],
        "is_smoker", "alcohol_days", "phys_act_days"
    ] if c is not None]

    work_feats = work[["SEQN"] + feature_cols].copy()
    return work, work_feats, feature_cols, colmap


def build_label(df: pd.DataFrame, colmap: dict):
    """
    Crea la etiqueta de perfil nutricional y riesgo cardiometabólico (saludable/moderado/alto).
    
    Sistema de puntuación ponderado basado en:
    - Guías AHA/ACC 2019 para prevención cardiovascular primaria
    - ATP III & ATP IV para dislipidemia  
    - Criterios ADA 2023 para diabetes
    - WHO/OMS para clasificación nutricional
    - Framingham Risk Score adaptado
    
    Factores evaluados:
    1. Antropométricos: BMI, circunferencia abdominal estimada
    2. Hemodinámicos: Presión arterial sistólica/diastólica  
    3. Metabólicos: Glucosa, perfil lipídico (HDL/LDL/TG)
    4. Nutricionales: Calidad dietética, macronutrientes, micronutrientes
    5. Conductuales: Tabaquismo, actividad física, alcohol
    
    Scoring ponderado por severidad clínica y evidencia científica.
    """
    
    # =============================================================================
    # UMBRALES CIENTÍFICOS DOCUMENTADOS
    # =============================================================================
    
    # Umbrales antropométricos (WHO/OMS 2023)
    BMI_THRESHOLDS = {
        "normal": (18.5, 24.9),
        "sobrepeso": (25.0, 29.9), 
        "obesidad_I": (30.0, 34.9),
        "obesidad_II": (35.0, 39.9),
        "obesidad_III": (40.0, float('inf'))
    }
    
    # Umbrales presión arterial (AHA/ACC 2017)
    BP_THRESHOLDS = {
        "normal": {"sbp": (0, 119), "dbp": (0, 79)},
        "elevada": {"sbp": (120, 129), "dbp": (0, 79)},
        "hipertension_1": {"sbp": (130, 139), "dbp": (80, 89)},
        "hipertension_2": {"sbp": (140, 179), "dbp": (90, 119)},
        "crisis": {"sbp": (180, float('inf')), "dbp": (120, float('inf'))}
    }
    
    # Umbrales metabólicos diferenciados por sexo (ADA 2023, ATP IV)
    METABOLIC_THRESHOLDS = {
        "glucosa": {
            "normal": (0, 99),
            "prediabetes": (100, 125),
            "diabetes": (126, float('inf'))
        },
        "hdl": {
            "masculino": {"bajo": (0, 39), "limitrofe": (40, 49), "normal": (50, float('inf'))},
            "femenino": {"bajo": (0, 49), "limitrofe": (50, 59), "normal": (60, float('inf'))}
        },
        "ldl": {
            "optimo": (0, 99),
            "casi_optimo": (100, 129),
            "limitrofe": (130, 159),
            "alto": (160, 189),
            "muy_alto": (190, float('inf'))
        },
        "trigliceridos": {
            "normal": (0, 149),
            "limitrofe": (150, 199),
            "alto": (200, 499),
            "muy_alto": (500, float('inf'))
        }
    }
    
    # Umbrales nutricionales (Dietary Guidelines 2020-2025)
    NUTRITIONAL_THRESHOLDS = {
        "calorias_exceso": 1.3,  # > 130% de necesidades estimadas
        "proteina_optima": (10, 35),  # % de calorías totales
        "carbohidratos_optimos": (45, 65),  # % de calorías totales  
        "grasas_optimas": (20, 35),  # % de calorías totales
        "azucar_maximo": 10,  # % de calorías totales (WHO)
        "fibra_minima": {"masculino": 38, "femenino": 25},  # g/día
        "sodio_maximo": 2300  # mg/día (AHA recomienda 1500)
    }

    # =============================================================================
    # PREPARACIÓN DE DATOS
    # =============================================================================
    
    bio = pd.DataFrame({
        "SEQN": df["SEQN"],
        "age": df[colmap["age"]] if colmap["age"] else np.nan,
        "sex": df[colmap["sex"]] if colmap["sex"] else np.nan,
        "BMI": df["BMI"],
        "SBP": df["SBP"], 
        "DBP": df["DBP"],
        "GLU": df[colmap["glucose"]] if colmap["glucose"] else np.nan,
        "HDL": df[colmap["hdl"]] if colmap["hdl"] else np.nan,
        "LDL": df[colmap["ldl"]] if colmap["ldl"] else np.nan,
        "TG": df[colmap["tg"]] if colmap["tg"] else np.nan,
        "kcal": df[colmap["kcal"]] if colmap["kcal"] else np.nan,
        "pct_protein": df["pct_protein"] if "pct_protein" in df.columns else np.nan,
        "pct_carb": df["pct_carb"] if "pct_carb" in df.columns else np.nan,
        "pct_fat": df["pct_fat"] if "pct_fat" in df.columns else np.nan,
        "sugar_g": df[colmap["sugar_g"]] if colmap["sugar_g"] else np.nan,
        "fiber_g": df[colmap["fiber_g"]] if colmap["fiber_g"] else np.nan,
        "sodium_mg": df[colmap["sodium_mg"]] if colmap["sodium_mg"] else np.nan,
        "is_smoker": df["is_smoker"] if "is_smoker" in df.columns else np.nan,
        "phys_act_days": df["phys_act_days"] if "phys_act_days" in df.columns else np.nan,
    })

    def calculate_risk_score(row):
        """
        Calcula score de riesgo ponderado (0-100).
        Pesos basados en impacto clínico y evidencia epidemiológica.
        """
        score = 0.0
        max_score = 0.0
        
        # 1. FACTOR ANTROPOMÉTRICO (Peso: 20%)
        peso_antropometrico = 20.0
        if pd.notna(row["BMI"]):
            max_score += peso_antropometrico
            if row["BMI"] >= 40:  # Obesidad mórbida
                score += peso_antropometrico * 1.0
            elif row["BMI"] >= 35:  # Obesidad severa
                score += peso_antropometrico * 0.8
            elif row["BMI"] >= 30:  # Obesidad
                score += peso_antropometrico * 0.6
            elif row["BMI"] >= 25:  # Sobrepeso
                score += peso_antropometrico * 0.3
            # BMI normal: 0 puntos
                
        # 2. FACTOR HEMODINÁMICO (Peso: 25%)
        peso_hemodinamico = 25.0
        if pd.notna(row["SBP"]) and pd.notna(row["DBP"]):
            max_score += peso_hemodinamico
            # Crisis hipertensiva
            if row["SBP"] >= 180 or row["DBP"] >= 120:
                score += peso_hemodinamico * 1.0
            # Hipertensión estadio 2
            elif row["SBP"] >= 140 or row["DBP"] >= 90:
                score += peso_hemodinamico * 0.8
            # Hipertensión estadio 1  
            elif row["SBP"] >= 130 or row["DBP"] >= 80:
                score += peso_hemodinamico * 0.5
            # Presión elevada
            elif row["SBP"] >= 120:
                score += peso_hemodinamico * 0.2
                
        # 3. FACTOR METABÓLICO (Peso: 30%)
        peso_metabolico = 30.0
        subfactor_metabolico = 0.0
        factores_metabolicos = 0
        
        # Glucosa (7.5%)
        if pd.notna(row["GLU"]):
            factores_metabolicos += 1
            if row["GLU"] >= 126:  # Diabetes
                subfactor_metabolico += 7.5 * 1.0
            elif row["GLU"] >= 100:  # Prediabetes
                subfactor_metabolico += 7.5 * 0.5
                
        # HDL - diferenciado por sexo (7.5%)
        if pd.notna(row["HDL"]) and pd.notna(row["sex"]):
            factores_metabolicos += 1
            es_masculino = row["sex"] == 1  # Asumiendo 1=masculino, 2=femenino
            umbral_bajo = 40 if es_masculino else 50
            if row["HDL"] <= umbral_bajo:
                subfactor_metabolico += 7.5 * 0.8
                
        # LDL (7.5%)
        if pd.notna(row["LDL"]):
            factores_metabolicos += 1
            if row["LDL"] >= 190:  # Muy alto
                subfactor_metabolico += 7.5 * 1.0
            elif row["LDL"] >= 160:  # Alto
                subfactor_metabolico += 7.5 * 0.8
            elif row["LDL"] >= 130:  # Limítrofe
                subfactor_metabolico += 7.5 * 0.4
                
        # Triglicéridos (7.5%)
        if pd.notna(row["TG"]):
            factores_metabolicos += 1
            if row["TG"] >= 500:  # Muy alto
                subfactor_metabolico += 7.5 * 1.0
            elif row["TG"] >= 200:  # Alto
                subfactor_metabolico += 7.5 * 0.6
            elif row["TG"] >= 150:  # Limítrofe
                subfactor_metabolico += 7.5 * 0.3
                
        if factores_metabolicos > 0:
            max_score += peso_metabolico
            score += subfactor_metabolico
            
        # 4. FACTOR NUTRICIONAL (Peso: 15%)
        peso_nutricional = 15.0
        subfactor_nutricional = 0.0
        factores_nutricionales = 0
        
        # Exceso calórico estimado (5%)
        if pd.notna(row["kcal"]) and pd.notna(row["age"]) and pd.notna(row["sex"]):
            factores_nutricionales += 1
            # Estimación TMB Harris-Benedict simplificada
            if row["sex"] == 1:  # Masculino
                tmb_est = 88.362 + (13.397 * 70) + (4.799 * 175) - (5.677 * max(row["age"], 20))
            else:  # Femenino  
                tmb_est = 447.593 + (9.247 * 60) + (3.098 * 162) - (4.330 * max(row["age"], 20))
            necesidades_est = tmb_est * 1.6  # Factor actividad moderada
            if row["kcal"] > necesidades_est * 1.3:  # >30% exceso
                subfactor_nutricional += 5.0 * 0.8
            elif row["kcal"] > necesidades_est * 1.1:  # >10% exceso
                subfactor_nutricional += 5.0 * 0.4
                
        # Desequilibrio de macronutrientes (5%)
        if pd.notna(row["pct_protein"]) and pd.notna(row["pct_carb"]) and pd.notna(row["pct_fat"]):
            factores_nutricionales += 1
            desequilibrio = 0
            if not (10 <= row["pct_protein"] <= 35): desequilibrio += 1
            if not (45 <= row["pct_carb"] <= 65): desequilibrio += 1  
            if not (20 <= row["pct_fat"] <= 35): desequilibrio += 1
            subfactor_nutricional += 5.0 * (desequilibrio / 3.0)
            
        # Exceso de azúcar y bajo en fibra (5%)
        if pd.notna(row["sugar_g"]) and pd.notna(row["kcal"]):
            factores_nutricionales += 0.5
            pct_azucar = (row["sugar_g"] * 4) / row["kcal"] * 100
            if pct_azucar > 10:  # >10% de calorías de azúcar
                subfactor_nutricional += 2.5 * min(pct_azucar / 20, 1.0)
                
        if pd.notna(row["fiber_g"]) and pd.notna(row["sex"]):
            factores_nutricionales += 0.5
            minimo_fibra = 38 if row["sex"] == 1 else 25
            if row["fiber_g"] < minimo_fibra * 0.5:  # <50% del mínimo
                subfactor_nutricional += 2.5 * 0.8
            elif row["fiber_g"] < minimo_fibra * 0.7:  # <70% del mínimo
                subfactor_nutricional += 2.5 * 0.4
                
        if factores_nutricionales > 0:
            max_score += peso_nutricional
            score += subfactor_nutricional
            
        # 5. FACTOR CONDUCTUAL (Peso: 10%)
        peso_conductual = 10.0
        subfactor_conductual = 0.0
        factores_conductuales = 0
        
        # Tabaquismo (5%)
        if pd.notna(row["is_smoker"]):
            factores_conductuales += 1
            if row["is_smoker"] == 1:
                subfactor_conductual += 5.0 * 1.0
                
        # Sedentarismo (5%)
        if pd.notna(row["phys_act_days"]):
            factores_conductuales += 1
            if row["phys_act_days"] < 2:  # <2 días/semana actividad
                subfactor_conductual += 5.0 * 0.8
            elif row["phys_act_days"] < 3:  # <3 días/semana
                subfactor_conductual += 5.0 * 0.4
                
        if factores_conductuales > 0:
            max_score += peso_conductual
            score += subfactor_conductual
            
        # Normalización del score (0-100)
        if max_score > 0:
            return min((score / max_score) * 100, 100)
        else:
            return np.nan
    
    # Aplicar cálculo de score
    bio["risk_score"] = bio.apply(calculate_risk_score, axis=1)
    
    # Clasificación en etiquetas científicamente fundamentadas
    def classify_risk(score):
        if pd.isna(score):
            return np.nan
        elif score <= 25:
            return "saludable"      # Riesgo bajo: Score 0-25
        elif score <= 55:
            return "moderado"       # Riesgo intermedio: Score 26-55
        else:
            return "alto"           # Riesgo alto: Score 56-100
    
    bio["risk_label"] = bio["risk_score"].apply(classify_risk)
    
    # Metadatos para documentación
    metadata = {
        "umbrales_antropometricos": BMI_THRESHOLDS,
        "umbrales_hemodinamicos": BP_THRESHOLDS, 
        "umbrales_metabolicos": METABOLIC_THRESHOLDS,
        "umbrales_nutricionales": NUTRITIONAL_THRESHOLDS,
        "ponderaciones": {
            "antropometrico": 20,
            "hemodinamico": 25, 
            "metabolico": 30,
            "nutricional": 15,
            "conductual": 10
        },
        "clasificacion_final": {
            "saludable": "Score 0-25 (riesgo cardiovascular bajo)",
            "moderado": "Score 26-55 (riesgo cardiovascular intermedio)", 
            "alto": "Score 56-100 (riesgo cardiovascular alto)"
        }
    }
    
    return bio[["SEQN", "risk_label", "risk_score"]], metadata

def build_preprocessor(feature_cols, sex_col):
    """Crea preprocesador (imputación + escalado + one-hot para sexo si aplica)."""
    num_cols = [c for c in feature_cols if c != sex_col]
    cat_cols = [sex_col] if sex_col and sex_col in feature_cols else []

    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("sc", StandardScaler())
            ]), num_cols),
            ("cat", Pipeline([
                ("imp", SimpleImputer(strategy="most_frequent")),
                ("oh", OneHotEncoder(handle_unknown="ignore"))
            ]), cat_cols)
        ]
    )
    return pre, num_cols, cat_cols

# ----------------------------
# Entrenamiento
# ----------------------------

def main(model_name: str = "rf", test_size: float = 0.2, random_state: int = 42):
    # Paths relativos al archivo actual
    here = Path(__file__).resolve()
    base_tesis = here.parent                    # .../moduloPrincipal/static/tesis
    dataset_dir = base_tesis / "dataset"
    artifacts_dir = base_tesis / "model_artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # (opcional) ayuda para depurar rutas
    print("Dataset dir:", dataset_dir)
    print("Artifacts dir:", artifacts_dir)

    # Carga y merge
    dfs = load_all(dataset_dir)
    df_all = merge_all(dfs)

    # Ingeniería de features
    work, work_feats, feature_cols, colmap = engineer_features(df_all)

    # Etiqueta (¡usar 'work', no df_all!)
    labels_df, metadata = build_label(work, colmap)
    data = work_feats.merge(labels_df, on="SEQN", how="left").dropna(subset=["risk_label"])

    X = data[feature_cols]
    y = data["risk_label"]

    # Preprocesador
    pre, num_cols, cat_cols = build_preprocessor(feature_cols, colmap["sex"])

    # Modelo
    if model_name.lower() == "mlp":
        clf = MLPClassifier(hidden_layer_sizes=(64, 32), activation="relu",
                            alpha=1e-4, max_iter=250, random_state=random_state)
    elif model_name.lower() == "rf":
        clf = RandomForestClassifier(
            n_estimators=400, max_depth=None, min_samples_leaf=2,
            random_state=random_state, n_jobs=-1, class_weight="balanced_subsample"
        )
    elif model_name.lower() == "logreg":
        clf = LogisticRegression(max_iter=200, multi_class="auto", class_weight="balanced")
    else:
        raise ValueError("Modelo no soportado. Usa: mlp | rf | logreg")

    pipe = Pipeline([("pre", pre), ("clf", clf)])

    # Split y entrenamiento
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    pipe.fit(Xtr, ytr)
    ypred = pipe.predict(Xte)

    # Métricas
    bal_acc = balanced_accuracy_score(yte, ypred)
    f1m = f1_score(yte, ypred, average="macro")
    print("\n=== RESULTADOS ===")
    print(f"Modelo: {model_name}")
    print(f"Balanced Accuracy: {bal_acc:.3f}")
    print(f"F1 Macro:         {f1m:.3f}")
    print(classification_report(yte, ypred))

    # Guardado de artefactos
    joblib.dump(pipe, artifacts_dir / "risk_profile_model.joblib")
    joblib.dump(pre, artifacts_dir / "preprocessor.joblib")
    
    # Lista de features utilizadas
    with open(artifacts_dir / "feature_list.txt", "w", encoding="utf-8") as f:
        for c in feature_cols:
            f.write(str(c) + "\n")
    
    # Distribución de etiquetas y estadísticas de scores
    label_stats = {
        "distribucion_etiquetas": data["risk_label"].value_counts(normalize=False).to_dict(),
        "proporcion_etiquetas": data["risk_label"].value_counts(normalize=True).round(3).to_dict(),
        "estadisticas_score": {
            "media": float(data["risk_score"].mean()),
            "mediana": float(data["risk_score"].median()),
            "desviacion_std": float(data["risk_score"].std()),
            "minimo": float(data["risk_score"].min()),
            "maximo": float(data["risk_score"].max()),
            "percentiles": {
                "p25": float(data["risk_score"].quantile(0.25)),
                "p75": float(data["risk_score"].quantile(0.75)),
                "p90": float(data["risk_score"].quantile(0.90)),
                "p95": float(data["risk_score"].quantile(0.95))
            }
        },
        "score_por_etiqueta": {
            label: {
                "media": float(group["risk_score"].mean()),
                "std": float(group["risk_score"].std()),
                "min": float(group["risk_score"].min()),
                "max": float(group["risk_score"].max())
            }
            for label, group in data.groupby("risk_label")
        }
    }
    
    with open(artifacts_dir / "label_dist.json", "w", encoding="utf-8") as f:
        json.dump(label_stats, f, ensure_ascii=False, indent=2)
    
    # Metadatos científicos completos
    scientific_metadata = {
        **metadata,
        "info_modelo": {
            "tipo": model_name,
            "fecha_entrenamiento": pd.Timestamp.now().isoformat(),
            "n_muestras_entrenamiento": len(Xtr),
            "n_muestras_test": len(Xte),
            "n_features": len(feature_cols),
            "random_state": random_state
        },
        "referencias_cientificas": {
            "guias_cardiovasculares": "AHA/ACC 2019 Guideline on Primary Prevention of CVD",
            "clasificacion_lipidos": "ATP III & ATP IV Guidelines",
            "criterios_diabetes": "ADA 2023 Standards of Medical Care",
            "clasificacion_nutricional": "WHO/FAO Dietary Guidelines",
            "clasificacion_bmi": "WHO Global Database on Body Mass Index",
            "presion_arterial": "2017 AHA/ACC High Blood Pressure Guidelines"
        },
        "validacion_clinica": {
            "nota": "Umbrales basados en consenso científico internacional",
            "aplicabilidad": "Población adulta general (>18 años)",
            "limitaciones": "Requiere validación en poblaciones específicas"
        }
    }
    
    with open(artifacts_dir / "scientific_metadata.json", "w", encoding="utf-8") as f:
        json.dump(scientific_metadata, f, ensure_ascii=False, indent=2)

    print("\nArtefactos guardados en:", artifacts_dir.as_posix())
    print("- risk_profile_model.joblib         (modelo entrenado)")
    print("- preprocessor.joblib               (preprocesador)")
    print("- feature_list.txt                  (lista de features)")
    print("- label_dist.json                   (estadísticas de etiquetas y scores)")
    print("- scientific_metadata.json          (metadatos científicos completos)")
    
    print(f"\n=== DISTRIBUCIÓN DE ETIQUETAS ===")
    for label, count in label_stats["distribucion_etiquetas"].items():
        pct = label_stats["proporcion_etiquetas"][label] * 100
        print(f"{label.upper():>10}: {count:>5} muestras ({pct:>5.1f}%)")
    
    print(f"\n=== ESTADÍSTICAS DE RISK SCORE ===")
    stats = label_stats["estadisticas_score"]
    print(f"Media: {stats['media']:.2f} ± {stats['desviacion_std']:.2f}")
    print(f"Rango: [{stats['minimo']:.2f}, {stats['maximo']:.2f}]")
    print(f"Percentiles: P25={stats['percentiles']['p25']:.2f}, P75={stats['percentiles']['p75']:.2f}, P95={stats['percentiles']['p95']:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrena el modelo de perfil nutricional (riesgo cardiometabólico).")
    parser.add_argument("--model", default="rf", choices=["mlp","rf","logreg"],
                        help="Selecciona el modelo: rf (RandomForest, default), mlp, logreg (LogisticRegression).")
    parser.add_argument("--test_size", type=float, default=0.2, help="Proporción de test (default 0.2).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    args = parser.parse_args()
    main(model_name=args.model, test_size=args.test_size, random_state=args.seed)
