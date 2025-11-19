# enfoque clásico vs machine learning

## contexto del proyecto

La iteración actual del asistente implementa un **enfoque híbrido**:

- El cuestionario nutricional de 10 ítems (NHANES 2017‑2018 + guías científicas) se transforma en un score explicable mediante `nutri_scorecard`.
- El mismo vector de puntajes alimenta un `RandomForestClassifier` entrenado con registros NHANES para obtener la etiqueta final y probabilidades por clase.
- La respuesta JSON expone ambos niveles (score científico + predicción ML) para maximizar transparencia y capacidad de generalización.

## reglas + random forest: fortalezas complementarias

| criterio | score científico | random forest |
| --- | --- | --- |
| transparencia | ✅ tablas y referencias por pregunta | ⚠️ modelo de caja gris (requiere métricas) |
| evidencia | ✅ citas DOI/ISBN por ítem | ✅ dataset público documentado (NHANES) |
| personalización | ⚠️ pesos fijos (10 % c/u) | ✅ aprende patrones multivariados |
| robustez ante ruido | ⚠️ sensible a respuestas extremas | ✅ promedia con 400 árboles balanceados |
| entrega al usuario | ✅ detalle por pregunta | ✅ probabilidad por clase para priorizar seguimiento |

## cuándo ampliar el componente ml

- Al incorporar **nuevas señales** (biomarcadores, actividad física, calidad del sueño) que exceden el score original.
- Si se recolectan **datasets propios** que permitan reentrenar con distribución local o equilibrar clases minoritarias.
- Cuando se requiera **personalizar recomendaciones** por grupos (por ejemplo adultos mayores vs. jóvenes) sin perder interpretabilidad.

Buenas prácticas para futuras iteraciones:

1. Mantener `nutri_scorecard` como baseline auditable.
2. Versionar datasets y artefactos (`model_artifacts/`) con metadatos completos.
3. Monitorear métricas de desempeño (F1 macro, balanced accuracy) y recalibrar con nuevos datos.
4. Documentar cualquier ajuste de ingeniería de características o tuning del Random Forest.

## resumen para la tesis

- **Estado actual:** enfoque híbrido (score científico + Random Forest entrenado en NHANES).
- **Valor diferencial:** combina evidencia nutricional explícita con capacidad de aprendizaje sobre patrones reales de la población.
- **Camino a futuro:** extender el pipeline al integrar variables clínicas, validar en datasets propios y explorar interpretabilidad (SHAP, feature importance) manteniendo la trazabilidad del score base.
