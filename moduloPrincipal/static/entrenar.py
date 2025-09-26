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
    """Crea la etiqueta de riesgo cardiometabólico (low/medium/high) usando puntos por cortes."""
    CUTS = {
        "BMI_obesity": 30.0,
        "SBP_high": 140.0,
        "DBP_high": 90.0,
        "GLU_high": 126.0,
        "HDL_low": 40.0,   # Hombres; si quieres más fino, ajusta por sexo
        "LDL_high": 160.0,
        "TG_high": 200.0
    }
    bio = pd.DataFrame({
        "SEQN": df["SEQN"],
        "BMI": df["BMI"],
        "SBP": df["SBP"],
        "DBP": df["DBP"],
        "GLU": df[colmap["glucose"]] if colmap["glucose"] else np.nan,
        "HDL": df[colmap["hdl"]] if colmap["hdl"] else np.nan,
        "LDL": df[colmap["ldl"]] if colmap["ldl"] else np.nan,
        "TG": df[colmap["tg"]] if colmap["tg"] else np.nan,
    })

    def pts(r):
        p = 0
        p += int(pd.notna(r["BMI"]) and r["BMI"] >= CUTS["BMI_obesity"])
        p += int(pd.notna(r["SBP"]) and r["SBP"] >= CUTS["SBP_high"])
        p += int(pd.notna(r["DBP"]) and r["DBP"] >= CUTS["DBP_high"])
        p += int(pd.notna(r["GLU"]) and r["GLU"] >= CUTS["GLU_high"])
        p += int(pd.notna(r["HDL"]) and r["HDL"] <= CUTS["HDL_low"])
        p += int(pd.notna(r["LDL"]) and r["LDL"] >= CUTS["LDL_high"])
        p += int(pd.notna(r["TG"]) and r["TG"] >= CUTS["TG_high"])
        return p

    bio["risk_pts"] = bio.apply(pts, axis=1)
    bio["risk_label"] = bio["risk_pts"].map(lambda p: "high" if p >= 3 else ("medium" if p == 2 else "low"))
    return bio[["SEQN", "risk_label"]], CUTS

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

def main(model_name: str = "mlp", test_size: float = 0.2, random_state: int = 42):
    # Paths relativos al archivo actual
    here = Path(__file__).resolve()
    base_static = here.parent                   # .../moduloPrincipal/static
    dataset_dir = base_static / "tesis" / "dataset"
    artifacts_dir = base_static / "tesis" / "model_artifacts"
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
    labels_df, cuts = build_label(work, colmap)
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
    with open(artifacts_dir / "feature_list.txt", "w", encoding="utf-8") as f:
        for c in feature_cols:
            f.write(str(c) + "\n")
    with open(artifacts_dir / "label_dist.json", "w", encoding="utf-8") as f:
        json.dump(data["risk_label"].value_counts(normalize=False).to_dict(), f, ensure_ascii=False, indent=2)

    print("\nArtefactos guardados en:", artifacts_dir.as_posix())
    print("- risk_profile_model.joblib")
    print("- preprocessor.joblib")
    print("- feature_list.txt")
    print("- label_dist.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrena el modelo de perfil nutricional (riesgo cardiometabólico).")
    parser.add_argument("--model", default="mlp", choices=["mlp","rf","logreg"],
                        help="Selecciona el modelo: mlp (default), rf (RandomForest), logreg (LogisticRegression).")
    parser.add_argument("--test_size", type=float, default=0.2, help="Proporción de test (default 0.2).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    args = parser.parse_args()
    main(model_name=args.model, test_size=args.test_size, random_state=args.seed)
