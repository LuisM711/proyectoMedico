## resumen

| Etiqueta | Rango de score (normalizado) | Definición | Características clave | Nivel de alerta | Interpretación nutricional |
| --- | --- | --- | --- | --- | --- |
| 🟢 saludable | 0 – 25 | Perfil nutricional equilibrado con parámetros dentro de rangos óptimos. | - Conductas protectoras (alta ingesta de agua, fruta y verdura)<br>- Nula o muy baja frecuencia de alcohol, ultraprocesados y sal añadida<br>- Desayuno regular y posible uso de suplementos | Alerta baja | Mantener hábitos actuales y monitoreo preventivo. |
| 🟡 moderado | 26 – 55 | Perfil con desequilibrios puntuales que requieren intervención preventiva. | - Factores de riesgo modificables presentes (azúcares, sodio, comida rápida)<br>- Variabilidad en consumo de frutas/verduras y desayuno incompleto<br>- Conductas saludables intermitentes | Alerta intermedia | Implementar cambios en dieta y estilo de vida con seguimiento regular. |
| 🔴 alto | 56 – 100 | Perfil con múltiples conductas desfavorables que elevan la alerta nutricional. | - Alto consumo de alcohol, bebidas azucaradas y ultraprocesados<br>- Ingesta insuficiente de agua, frutas, verduras y granos integrales<br>- Desayuno omitido, sal añadida habitual y ausencia de suplementos | Alerta alta | Intervención prioritaria, ajustes inmediatos y acompañamiento profesional. |

El score se obtiene sumando los 10 ítems (máx. 95 puntos) y normalizando: `(score_bruto / 95) × 100`.

## tabla maestra del cuestionario (10 ítems)

| # | variable NHANES | pregunta | respuesta | puntos | evidencia |
| --- | --- | --- | --- | --- | --- |
| 1 | `ALQ120Q/U` | Frecuencia de bebidas alcohólicas (12 meses) | Nunca | 0 | [1] |
| | | | 1‑3 veces/mes | 3 | |
| | | | 1‑3 veces/semana | 7 | |
| | | | ≥4 veces/semana | 10 | |
| 2 | `DBQ223A/U` | Raciones de fruta al día | ≥3 | 0 | [2] |
| | | | 2 | 3 | |
| | | | 1 | 7 | |
| | | | <1 | 10 | |
| 3 | `DBQ223B/U` | Raciones de verdura al día | ≥3 | 0 | [3] |
| | | | 2 | 3 | |
| | | | 1 | 7 | |
| | | | <1 | 10 | |
| 4 | `DBQ223D/U` | Bebidas azucaradas por semana | 0 | 0 | [4] |
| | | | 1‑2 | 3 | |
| | | | 3‑4 | 7 | |
| | | | ≥5 | 10 | |
| 5 | `DBQ330` | Comida rápida/ultraprocesada (semana) | 0 | 0 | [5] |
| | | | 1‑2 | 4 | |
| | | | 3‑4 | 7 | |
| | | | ≥5 | 10 | |
| 6 | `DBQ197` | Vasos de agua natural al día | ≥5 | 0 | [6] |
| | | | 3‑4 | 3 | |
| | | | 1‑2 | 7 | |
| | | | <1 | 10 | |
| 7 | `DBQ235C` | Consumo semanal de granos integrales | ≥5 | 0 | [7] |
| | | | 3‑4 | 3 | |
| | | | 1‑2 | 7 | |
| | | | 0 | 10 | |
| 8 | `CSQ240` | Añadir sal a la comida servida | Nunca | 0 | [8] |
| | | | Rara vez | 3 | |
| | | | Algunas veces | 7 | |
| | | | Siempre | 10 | |
| 9 | `DSQ010` | Uso habitual de suplementos | Sí | 0 | [9] |
| | | | Ocasional | 2 | |
| | | | No | 5 | |
| 10 | `DBQ010` | Días a la semana que se desayuna | 5‑7 | 0 | [10] |
| | | | 3‑4 | 4 | |
| | | | 1‑2 | 7 | |
| | | | 0 | 10 | |

### fórmula de normalización

```
score_bruto = Σ puntos_i
score_normalizado = (score_bruto / 95) × 100
```

### distribución simulada (10 000 muestras, `entrenar.py`)

- Media ± DE: 41.8 ± 18.5
- Percentiles: P25=27.2 · P50=41.0 · P75=56.4
- Etiquetas: saludable 32%, moderado 46%, alto 22% (aprox.)

## referencias

1. Dietary Guidelines for Americans 2020‑2025. ISBN 978‑1734383140.  
2. Aune D, et al. *Int J Epidemiol.* 2017;46(3):1029‑1056. doi:10.1093/ije/dyw319.  
3. World Health Organization. *Healthy diet: Key facts.* 2020.  
4. Johnson RK, et al. *Circulation.* 2009;120:1011‑1020. doi:10.1161/CIRCULATIONAHA.109.192627.  
5. National Academies of Sciences. *Dietary Reference Intakes…* doi:10.17226/10925.  
6. Monzani A, et al. *Nutrients.* 2019;11(6):1316. doi:10.3390/nu11061316.  
7. Breslow RA, et al. *NCHS Data Brief.* 2013;(112):1‑8.  
8. World Health Organization. *Guideline: Sodium Intake for Adults and Children.* ISBN 9789241547628.  
9. Mekary RA, et al. *Am J Clin Nutr.* 2012;95(5):1182‑1189. doi:10.3945/ajcn.111.028209.  
10. Uzhova I, et al. *J Am Coll Cardiol.* 2017;70(15):1833‑1842. doi:10.1016/j.jacc.2017.08.027.
