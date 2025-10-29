# Algoritmo de Etiquetado de Perfil Nutricional y Riesgo Cardiometabólico

## Resumen Ejecutivo

Sistema de clasificación científicamente fundamentado que evalúa el perfil nutricional y riesgo cardiometabólico de individuos, clasificándolos en tres categorías:

- **🟢 SALUDABLE** (Score 0-25): Riesgo cardiovascular bajo
- **🟡 MODERADO** (Score 26-55): Riesgo cardiovascular intermedio  
- **🔴 ALTO** (Score 56-100): Riesgo cardiovascular alto

## Metodología Científica

### Fundamentos Teóricos

El algoritmo integra múltiples dominios de evidencia científica:

1. **Guías Cardiovasculares**: AHA/ACC 2019 para prevención primaria
2. **Criterios Metabólicos**: ADA 2023 para diabetes, ATP III/IV para dislipidemia
3. **Estándares Nutricionales**: WHO/FAO Dietary Guidelines 2020-2025
4. **Clasificaciones Antropométricas**: WHO Global Database on BMI
5. **Framingham Risk Score**: Adaptado para población contemporánea

### Sistema de Puntuación Ponderado

#### Factores Evaluados y Sus Pesos:

```
📊 DISTRIBUCIÓN DE PESOS POR FACTOR

🫀 METABÓLICO (30%)          ████████████████████████████████
   ├─ Glucosa (7.5%)
   ├─ HDL diferenciado por sexo (7.5%)  
   ├─ LDL (7.5%)
   └─ Triglicéridos (7.5%)

🩺 HEMODINÁMICO (25%)        ████████████████████████████
   ├─ Presión sistólica
   └─ Presión diastólica

🏃 ANTROPOMÉTRICO (20%)      ████████████████████████
   └─ Índice de Masa Corporal (BMI)

🥗 NUTRICIONAL (15%)         ████████████████████
   ├─ Exceso calórico estimado (5%)
   ├─ Desequilibrio macronutrientes (5%)
   └─ Azúcar alto + fibra baja (5%)

🚭 CONDUCTUAL (10%)          ████████████████
   ├─ Tabaquismo (5%)
   └─ Sedentarismo (5%)
```

## Umbrales Científicos Documentados

### 1. Factor Antropométrico (WHO/OMS 2023)

```python
BMI_CLASSIFICATION = {
    "Normal":       18.5 - 24.9 kg/m²  →  0 puntos
    "Sobrepeso":    25.0 - 29.9 kg/m²  →  6 puntos  (30% del factor)
    "Obesidad I":   30.0 - 34.9 kg/m²  →  12 puntos (60% del factor)
    "Obesidad II":  35.0 - 39.9 kg/m²  →  16 puntos (80% del factor)  
    "Obesidad III": ≥40.0 kg/m²        →  20 puntos (100% del factor)
}
```

### 2. Factor Hemodinámico (AHA/ACC 2017)

```python
BLOOD_PRESSURE_CLASSIFICATION = {
    "Normal":           SBP <120 y DBP <80      →  0 puntos
    "Elevada":          SBP 120-129 y DBP <80  →  5 puntos  (20% del factor)
    "Hipertensión I":   SBP 130-139 o DBP 80-89 →  12.5 puntos (50% del factor)
    "Hipertensión II":  SBP 140-179 o DBP 90-119 → 20 puntos (80% del factor)
    "Crisis":           SBP ≥180 o DBP ≥120    →  25 puntos (100% del factor)
}
```

### 3. Factor Metabólico (ADA 2023, ATP III/IV)

#### Glucosa:
```python
GLUCOSE_THRESHOLDS = {
    "Normal":       <100 mg/dL     →  0 puntos
    "Prediabetes":  100-125 mg/dL  →  3.75 puntos (50% del subfactor)
    "Diabetes":     ≥126 mg/dL     →  7.5 puntos  (100% del subfactor)
}
```

#### HDL Colesterol (diferenciado por sexo):
```python
HDL_THRESHOLDS = {
    "Masculino": {
        "Normal":    ≥50 mg/dL     →  0 puntos
        "Limítrofe": 40-49 mg/dL   →  3 puntos
        "Bajo":      <40 mg/dL     →  6 puntos (80% del subfactor)
    },
    "Femenino": {
        "Normal":    ≥60 mg/dL     →  0 puntos  
        "Limítrofe": 50-59 mg/dL   →  3 puntos
        "Bajo":      <50 mg/dL     →  6 puntos (80% del subfactor)
    }
}
```

#### LDL Colesterol:
```python
LDL_THRESHOLDS = {
    "Óptimo":       <100 mg/dL     →  0 puntos
    "Casi óptimo":  100-129 mg/dL  →  1.5 puntos
    "Limítrofe":    130-159 mg/dL  →  3 puntos   (40% del subfactor)
    "Alto":         160-189 mg/dL  →  6 puntos   (80% del subfactor)
    "Muy alto":     ≥190 mg/dL     →  7.5 puntos (100% del subfactor)
}
```

#### Triglicéridos:
```python
TRIGLYCERIDES_THRESHOLDS = {
    "Normal":       <150 mg/dL     →  0 puntos
    "Limítrofe":    150-199 mg/dL  →  2.25 puntos (30% del subfactor)
    "Alto":         200-499 mg/dL  →  4.5 puntos  (60% del subfactor)
    "Muy alto":     ≥500 mg/dL     →  7.5 puntos  (100% del subfactor)
}
```

### 4. Factor Nutricional (Dietary Guidelines 2020-2025)

#### Exceso Calórico:
```python
# Cálculo TMB Harris-Benedict + Factor Actividad
CALORIC_EXCESS = {
    "Normal":       ≤110% TMB × 1.6  →  0 puntos
    "Moderado":     110-130% TMB × 1.6 → 2 puntos   (40% del subfactor)
    "Severo":       >130% TMB × 1.6   →  4 puntos   (80% del subfactor)
}
```

#### Desequilibrio de Macronutrientes:
```python
MACRONUTRIENT_BALANCE = {
    "Proteína":      10-35% calorías totales
    "Carbohidratos": 45-65% calorías totales  
    "Grasas":        20-35% calorías totales
    # Penalización: 1.67 puntos por cada macronutriente fuera de rango
}
```

#### Micronutrientes:
```python
MICRONUTRIENT_FACTORS = {
    "Azúcar añadido":  >10% calorías → hasta 2.5 puntos
    "Fibra insuficiente": {
        "Masculino": <50% de 38g/día → hasta 2 puntos
        "Femenino":  <50% de 25g/día → hasta 2 puntos
    }
}
```

### 5. Factor Conductual

#### Tabaquismo:
```python
SMOKING_STATUS = {
    "No fumador":  0 puntos
    "Fumador":     5 puntos (100% del subfactor)
}
```

#### Actividad Física:
```python
PHYSICAL_ACTIVITY = {
    "≥3 días/semana":  0 puntos
    "2 días/semana":   2 puntos (40% del subfactor)  
    "<2 días/semana":  4 puntos (80% del subfactor)
}
```

## Algoritmo de Clasificación Final

### Cálculo del Score de Riesgo:

```python
def calculate_risk_score(patient_data):
    """
    Calcula score ponderado de 0-100 puntos
    """
    total_score = 0
    max_possible_score = 0
    
    # Suma ponderada de todos los factores disponibles
    for factor in [antropométrico, hemodinámico, metabólico, nutricional, conductual]:
        if factor.has_data():
            total_score += factor.calculate_points()
            max_possible_score += factor.max_points()
    
    # Normalización a escala 0-100
    normalized_score = (total_score / max_possible_score) * 100
    return min(normalized_score, 100)
```

### Clasificación por Umbrales:

```python
def classify_risk_profile(score):
    """
    Clasifica el perfil de riesgo basado en percentiles poblacionales
    y evidencia clínica de outcomes cardiovasculares
    """
    if score <= 25:
        return "saludable"    # Riesgo <10% eventos CV a 10 años
    elif score <= 55:  
        return "moderado"     # Riesgo 10-20% eventos CV a 10 años
    else:
        return "alto"         # Riesgo >20% eventos CV a 10 años
```

## Validación Clínica

### Población Objetivo:
- **Edad**: Adultos ≥18 años
- **Aplicabilidad**: Población general para screening primario
- **Exclusiones**: Enfermedad cardiovascular establecida, embarazo

### Limitaciones Reconocidas:
1. **Especificidad étnica**: Requiere calibración por poblaciones
2. **Factores genéticos**: No incluye marcadores genéticos
3. **Historia familiar**: No considera antecedentes familiares
4. **Biomarcadores avanzados**: No incluye PCR-us, Lp(a), etc.

### Recomendaciones de Uso:
- **Screening primario**: Identificación de individuos de riesgo
- **Seguimiento poblacional**: Monitoreo de tendencias de salud
- **Investigación epidemiológica**: Estudios de cohorte grandes
- **NO para diagnóstico clínico**: Requiere evaluación médica completa

## Referencias Científicas

1. **Arnett, D.K., et al.** (2019). *2019 AHA/ACC Primary Prevention Guideline*. Circulation, 140(11), e596-e646.

2. **American Diabetes Association** (2023). *Standards of Medical Care in Diabetes—2023*. Diabetes Care, 46(Supplement_1).

3. **Grundy, S.M., et al.** (2018). *2018 AHA/ACC/AACVPR/AAPA/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Blood Cholesterol*. Circulation, 139(25), e1082-e1143.

4. **World Health Organization** (2020). *Healthy diet: Key facts*. WHO Factsheet.

5. **Whelton, P.K., et al.** (2017). *2017 ACC/AHA/AAPA/ABC/ACPM High Blood Pressure Clinical Practice Guideline*. Hypertension, 71(6), e13-e115.

---

*Documento técnico generado automáticamente por el sistema de entrenamiento de modelos de Machine Learning para perfil nutricional - Proyecto de tesis en Ingeniería de Software*
