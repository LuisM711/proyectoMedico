# algoritmo de etiquetado del cuestionario nutricional

## resumen

El asistente nutricional clasifica a cada persona en tres niveles de alerta nutricional según el puntaje total obtenido en un cuestionario de 10 preguntas respaldado por literatura científica:

- 🟢 **saludable**   0 – 25 puntos (riesgo bajo)
- 🟡 **moderado**   26 – 55 puntos (riesgo intermedio)
- 🔴 **alto**     56 – 100 puntos (riesgo elevado)

El puntaje bruto máximo es 95 (algunas preguntas valen 5 o 10). Se normaliza a 0‑100 para mantener los umbrales tradicionales, tal como se documenta en `DEFINICION_ETIQUETAS_Y_UMBRALES.md`.

## fundamentos científicos

Cada pregunta se mapea a variables observadas en NHANES 2017‑2018 (recordatorio dietario + cuestionario) y se respalda con literatura científica vigente:

| Ítem | Variables NHANES aprovechadas | Referencias clave |
| --- | --- | --- |
| 1. Frecuencia de alcohol | `ALQ120Q`, `ALQ120U`, `DR1TALCO` | Dietary Guidelines 2020‑2025 [1] |
| 2. Raciones de fruta | `DBQ197`, vitamina C (`DR1TVC`) | Aune et al., 2017 [2] |
| 3. Raciones de verdura | `DBD381`, fibra total (`DR1TFIBE`) | WHO “5-a-day” [3] |
| 4. Bebidas azucaradas | Azúcares totales (`DR1TSUGR`) | Johnson et al., 2009 [4] |
| 5. Comida rápida / ultraprocesada | Grasa saturada (`DR1TSFAT`) | Dietary Guidelines 2020‑2025 [1] |
| 6. Agua natural | Agua simple (`DR1TWS`) | National Academies, 2005 [5] |
| 7. Granos integrales | Ratio fibra/carbohidratos (`DR1TFIBE` / `DR1TCARB`) | Dietary Guidelines 2020‑2025 [1] |
| 8. Sal añadida | Sodio ingerido (`DR1TSODI`) | WHO Sodium Guidelines, 2012 [8] |
| 9. Suplementos | Registro farmacológico (`RXDDRUG`) con palabras clave vitamínicas | Breslow et al., 2013 [7] |
| 10. Desayuno | `DBQ010` + energía diaria (`DR1TKCAL`) | Mekary et al., 2012 [9]; Uzhova et al., 2017 [10] |

## sistema de puntuación

Cada pregunta se puntúa de 0 (conducta óptima) a 10 (conducta de mayor riesgo). El ítem de suplementos tiene un máximo de 5 puntos porque se penaliza moderadamente la omisión de micronutrientes. La suma se normaliza:

```
score_normalizado = (score_bruto / 95) × 100
etiqueta = {
    score ≤ 25 → "saludable"
    25 < score ≤ 55 → "moderado"
    score > 55 → "alto"
}
```

### detalle por pregunta

| Pregunta | Puntos | Evidencia |
| --- | --- | --- |
| Alcohol diario (≥5 días/semana) | 10 | Límites de ingesta responsable [1] |
| Frutas <1 ración/día | 10 | Meta-análisis sobre consumo de fruta [2] |
| Verduras <1 ración/día | 10 | OMS “5‑a‑day” [3] |
| Bebidas azucaradas ≥5 veces/semana | 10 | Alerta nutricional [4] |
| Comida rápida ≥5 veces/semana | 10 | Exceso calórico ultraprocesado [5] |
| Agua <1 vaso/día | 10 | Regulación de apetito/hidratación [6] |
| Granos integrales nulos | 10 | Consumo y salud metabólica [7] |
| Sal siempre en la mesa | 10 | Guía OMS sodio <2 g/día [8] |
| No uso de suplementos | 5 | Deficiencias y DM2 [9] |
| Saltar desayuno toda la semana | 10 | Obesidad/aterosclerosis [10] |

## flujo de cálculo

1. El front captura las 10 respuestas y envía los puntajes asociados (0‑10/5).
2. El back-end construye un vector ordenado con esas 10 características, calcula la puntuación normalizada con `nutri_scorecard` para transparencia y lo procesa con el modelo Random Forest entrenado sobre NHANES.
3. La respuesta expone:
   - etiqueta final (`saludable`, `moderado`, `alto`) predicha por el Random Forest
   - score bruto y normalizado calculados con la regla científica
   - detalle por pregunta (puntos obtenidos vs. máximo)
   - probabilidades de cada clase y metadatos del modelo
   - recomendaciones específicas según el nivel de alerta

## validación y entrenamiento con nhanes

El script `entrenar.py` fusiona los módulos `questionnaire.csv`, `diet.csv` y `medications.csv` de NHANES 2017‑2018, transforma cada registro a los 10 puntajes científicos y etiqueta los ejemplos con `nutri_scorecard`. Con ese dataset realiza:

- división entrenamiento/prueba estratificada (80/20),
- entrenamiento de un `RandomForestClassifier` (400 árboles, `class_weight="balanced"`),
- reporte de métricas (accuracy, precision, recall, F1 por clase),
- almacenamiento de artefactos (`risk_profile_model.joblib`, `preprocessor.joblib`, `feature_list.txt`, `label_dist.json`, `scientific_metadata.json`).

El script `verificar_clasificacion.py` y las pruebas unitarias en `moduloPrincipal/tests.py` validan casos extremos para asegurar coherencia entre la puntuación científica y la predicción del modelo.

## referencias

1. **U.S. Department of Agriculture & Department of Health and Human Services.** *Dietary Guidelines for Americans 2020‑2025.* ISBN 978‑1734383140.  
2. **Aune D, Giovannucci E, et al.** *Int J Epidemiol.* 2017;46(3):1029‑1056. doi:10.1093/ije/dyw319.  
3. **World Health Organization.** *Healthy diet: Key facts.* WHA65.6, 2020.  
4. **Johnson RK, et al.** *Circulation.* 2009;120:1011‑1020. doi:10.1161/CIRCULATIONAHA.109.192627.  
5. **National Academies of Sciences.** *Dietary Reference Intakes for Water, Potassium, Sodium, Chloride, and Sulfate.* doi:10.17226/10925.  
6. **Monzani A, et al.** *Nutrients.* 2019;11(6):1316. doi:10.3390/nu11061316.  
7. **Breslow RA, et al.** *NCHS Data Brief.* 2013;(112):1‑8.  
8. **World Health Organization.** *Guideline: Sodium Intake for Adults and Children.* ISBN 9789241547628.  
9. **Mekary RA, et al.** *Am J Clin Nutr.* 2012;95(5):1182‑1189. doi:10.3945/ajcn.111.028209.  
10. **Uzhova I, et al.** *J Am Coll Cardiol.* 2017;70(15):1833‑1842. doi:10.1016/j.jacc.2017.08.027.
