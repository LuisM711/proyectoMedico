# Definición de Etiquetas y Umbrales del Perfil Nutricional

Este documento resume la nueva lógica de puntuación construida a partir del cuestionario nutricional de 10 ítems que deriva de los módulos dietarios y de comportamiento alimentario de NHANES 2017-2018. Cada pregunta aporta hasta 10 puntos (100 puntos en total) y refleja el grado de adherencia a las guías alimentarias vigentes. A menor puntaje, mejor patrón nutricional.

## 📊 Etiquetas de adherencia dietaria

| Score final | Etiqueta | Descripción | Recomendación principal |
|:-----------:|:--------:|:------------|:------------------------|
| **0 – 25**  | 🟢 Saludable | Cumple de forma consistente con las guías dietarias. | Mantener hábitos y monitorear anualmente. |
| **26 – 55** | 🟡 En transición | Presenta desvíos puntuales en la calidad de la dieta. | Ajustes graduales, educación nutricional y seguimiento trimestral. |
| **56 – 100**| 🔴 En riesgo | Patrón alimentario alejado de las guías, con alta carga de factores adversos. | Intervención nutricional estructurada y reevaluación mensual. |

## 📝 Cuestionario nutricional y puntajes

Las preguntas se basan en los códigos originales de NHANES (2017-2018) y se califican con un esquema de riesgo (0 sin riesgo / 10 riesgo máximo).

### 1. Consumo de alcohol (ALQ101)
**Pregunta:** En los últimos 12 meses, ¿con qué frecuencia consumiste bebidas alcohólicas?

| Respuesta | Puntaje | Soporte |
|-----------|:-------:|---------|
| Nunca | 0 | |
| Mensualmente | 3 | |
| Semanalmente | 7 | |
| Diariamente | 10 | Dietary Guidelines for Americans 2020-2025 [1] |

> El exceso de alcohol incrementa la mortalidad total y el riesgo de varios tipos de cáncer.

### 2. Ingesta diaria de frutas (DBQ197)

| Raciones al día | Puntaje | Referencia |
|-----------------|:-------:|------------|
| ≥3 | 0 | Aune et al., 2017 [2] |
| 2 | 3 | |
| 1 | 7 | |
| 0 | 10 | |

### 3. Ingesta diaria de verduras (DBQ223A)

| Raciones al día | Puntaje | Referencia |
|-----------------|:-------:|------------|
| ≥3 | 0 | Aune et al., 2017 [2] |
| 2 | 3 | |
| 1 | 7 | |
| 0 | 10 | |

### 4. Bebidas azucaradas (DBQ223D)

| Frecuencia semanal | Puntaje | Referencia |
|--------------------|:-------:|------------|
| 0 | 0 | AHA 2009 [4] |
| 1 – 2 | 3 | |
| 3 – 4 | 7 | |
| ≥5 | 10 | |

### 5. Comida rápida o comida preparada fuera (DBQ330)

| Frecuencia semanal | Puntaje | Evidencia |
|--------------------|:-------:|-----------|
| 0 | 0 | Dietary Guidelines for Americans promueven comida casera sobre ultraprocesada [1] |
| 1 – 2 | 4 | |
| 3 – 4 | 7 | |
| ≥5 | 10 | |

### 6. Consumo de agua pura (DBQ223H)

| Vasos/botellas diarias | Puntaje | Referencia |
|------------------------|:-------:|------------|
| ≥5 | 0 | National Academies of Sciences – Adequate Intake (AI) [5] |
| 3 – 4 | 3 | |
| 1 – 2 | 7 | |
| 0 | 10 | |

### 7. Consumo de granos integrales (DBQ235C)

| Frecuencia semanal | Puntaje | Referencia |
|--------------------|:-------:|------------|
| ≥5 | 0 | Dietary Guidelines for Americans: mitad de granos integrales [1] |
| 3 – 4 | 3 | |
| 1 – 2 | 7 | |
| 0 | 10 | |

### 8. Adición de sal en la mesa (CSQ240)

| Frecuencia | Puntaje | Referencia |
|------------|:-------:|------------|
| Nunca | 0 | WHO – ingesta máxima de sodio 2000 mg/día [8] |
| Rara vez | 3 | |
| Algunas veces | 7 | |
| Siempre | 10 | |

### 9. Uso habitual de suplementos vitamínicos/minerales (DSQ010)

| Respuesta | Puntaje | Consideraciones |
|-----------|:-------:|-----------------|
| Sí | 0 | Útil para cubrir brechas cuando hay deficiencias documentadas [7]. |
| No | 5 | Se penaliza moderadamente porque la recomendación primaria es vía alimentos; no es un factor crítico. |

### 10. Frecuencia de desayuno (DBQ010)

| Días por semana | Puntaje | Evidencia |
|-----------------|:-------:|-----------|
| 5 – 7 | 0 | Omitir desayuno se asocia con obesidad, DM2 y dislipidemia [6,9,10] |
| 3 – 4 | 4 | |
| 1 – 2 | 7 | |
| 0 | 10 | |

## 🧮 Sistema de puntuación

- **Puntaje total**: suma de los 10 ítems (0-100).  
- **Fórmula**:
  ```
  Score final = Σ puntos pregunta_i
  ```
- **Interpretación**: usar tabla de etiquetas al inicio para definir el nivel de adherencia dietaria.

## 📈 Visualización de peso relativo

Cada pregunta vale 10 puntos (10 % del total), por lo que la ponderación es uniforme:

```
🥗 Cuestionario dietario (100%)  ███████████████████████████████████████████████████████
   ├─ Alcohol                     ██████
   ├─ Frutas                      ██████
   ├─ Verduras                    ██████
   ├─ Bebidas azucaradas          ██████
   ├─ Comida rápida               ██████
   ├─ Agua                        ██████
   ├─ Granos integrales           ██████
   ├─ Sal añadida                 ██████
   ├─ Suplementos                 ██████
   └─ Desayuno                    ██████
```

## 📚 Referencias clave

1. U.S. Department of Agriculture; U.S. Department of Health and Human Services. *Dietary Guidelines for Americans, 2020–2025*. 9th ed. Washington, DC: U.S. Government Publishing Office; 2020. ISBN 978-1734383140. Disponible en: https://www.dietaryguidelines.gov/  
2. Aune D, Giovannucci E, Boffetta P, et al. Fruit and vegetable intake and the risk of chronic disease, total cancer and all-cause mortality—a systematic review and dose-response meta-analysis of prospective studies. *Int J Epidemiol*. 2017;46(3):1029‑1056. doi:10.1093/ije/dyw319  
3. World Health Organization. *Guideline: Sugars Intake for Adults and Children*. Geneva: WHO; 2015. ISBN 9789241549028. Disponible en: https://www.who.int/publications/i/item/9789241549028  
4. Johnson RK, Appel LJ, Brands M, et al. Dietary sugars intake and metabolic health: a scientific statement from the American Heart Association. *Circulation*. 2009;120(11):1011‑1020. doi:10.1161/CIRCULATIONAHA.109.192627  
5. National Academies of Sciences, Engineering, and Medicine. *Dietary Reference Intakes for Water, Potassium, Sodium, Chloride, and Sulfate*. Washington, DC: National Academies Press; 2005. doi:10.17226/10925  
6. Wang K, Niu Y, Lu Z, et al. The effect of breakfast on childhood obesity: a systematic review and meta-analysis. *Front Nutr*. 2023;10:1222536. doi:10.3389/fnut.2023.1222536  
7. Breslow RA, Chen CM, Graubard BI, Jacobovits T. *Dietary supplement use among U.S. adults has increased since NHANES III (1988–1994)*. NCHS Data Brief. 2013;(61):1‑8. Disponible en: https://www.cdc.gov/nchs/products/databriefs/db61.htm  
8. World Health Organization. *Guideline: Sodium Intake for Adults and Children*. Geneva: WHO; 2012. ISBN 9789241504836. Disponible en: https://www.who.int/publications/i/item/9789241504836  
9. Mekary RA, Giovannucci E, Cahill L, et al. Eating patterns and type 2 diabetes risk in men: breakfast omission, eating frequency, and snacking. *Am J Clin Nutr*. 2012;95(5):1182‑1189. doi:10.3945/ajcn.111.028209  
10. Uzhova I, Fuster V, Fernández-Ortiz A, et al. The importance of breakfast in atherosclerosis disease: insights from the PESA study. *J Am Coll Cardiol*. 2017;70(15):1833‑1842. doi:10.1016/j.jacc.2017.08.027  

## ⚠️ Limitaciones

1. El cuestionario no captura porciones exactas ni el total calórico; se centra en frecuencia y patrones.
2. No incorpora condiciones clínicas (glucosa, lípidos, presión arterial) ni medidas antropométricas; estos deben integrarse en análisis complementarios.
3. Estudios longitudinales son necesarios para confirmar la capacidad predictiva del score en diferentes poblaciones.
4. La pregunta de suplementos se penaliza moderadamente, dado que las guías priorizan la ingesta por medios alimentarios.

## ✅ Recomendaciones de uso

- **Aplicación**: adultos ≥18 años en entornos de promoción de salud, investigación y cribado rápido.  
- **Frecuencia**: repetir cada 3-6 meses para monitorear cambios.  
- **Integración**: combinar con biomarcadores (labs), antropometría y actividad física para un perfil integral de salud.

---

*Documento técnico generado para el proyecto de tesis "Sistema de Evaluación de Perfil Nutricional con Machine Learning" - Ingeniería de Software*
