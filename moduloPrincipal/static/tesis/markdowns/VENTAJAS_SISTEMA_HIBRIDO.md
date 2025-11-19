# ventajas del sistema actual

## resumen ejecutivo

El asistente combina **score científico + Random Forest**. El cuestionario de 10 ítems asegura trazabilidad y el modelo entrenado con NHANES aporta aprendizaje sobre conductas reales. Esto consolida la propuesta de “sistema híbrido” porque:

- el score clásico explica cada recomendación con citas verificables;
- el modelo aprende patrones conjuntos (por ejemplo, alto sodio + poco desayuno);
- las probabilidades del Random Forest priorizan casos que requieren intervención inmediata.

## beneficios de la capa clásica

| aspecto | resultado |
| --- | --- |
| Transparencia | Cada pregunta tiene una referencia (DOI/ISBN) y un rango de puntuación documentado. |
| Auditoría | El backend devuelve el detalle de puntos por ítem, permitiendo justificar la recomendación. |
| Implementación | No requiere datasets sensibles ni entrenamiento periódico. |
| Cumplimiento | Facilita revisiones éticas y regulatorias porque todo el cálculo es determinístico. |

## por qué mantener la arquitectura híbrida

1. **Explicabilidad garantizada**  
   `nutri_scorecard` sigue siendo la fuente de verdad auditada: cada valor está respaldado por DOI/ISBN y se normaliza a 0‑100. El modelo nunca sobrescribe el detalle por pregunta.

2. **Aprendizaje sobre patrones reales**  
   El Random Forest absorbe relaciones que la tabla de puntuaciones no modela (interacciones entre azúcar, fibra y suplementos, por ejemplo) y entrega probabilidades calibradas para priorizar seguimiento.

3. **Evidencia completa para la tesis**  
   Se documenta el pipeline de entrenamiento (NHANES → feature engineering → Random Forest) y se muestran métricas de validación. Esto demuestra dominio tanto de reglas como de machine learning.

## pasos propuestos para futuras ampliaciones

1. Incorporar biomarcadores o datos propios e incluirlos en `entrenar.py` como nuevas características.  
2. Evaluar técnicas de interpretabilidad (feature importance, SHAP) para profundizar en la contribución de cada hábito.  
3. Implementar monitorización periódica de métricas y reentrenamiento cuando existan suficientes datos locales.  
4. Definir políticas de conciliación si se agregan nuevas capas: por ejemplo, priorizar la etiqueta más conservadora cuando el modelo tenga baja confianza (<0.6).

## conclusión

- El sistema productivo opera con dos capas sincronizadas: puntuación científica + Random Forest entrenado con NHANES.  
- La separación por capas (`nutri_scorecard` vs. artefactos en `model_artifacts/`) facilita mantenimiento, auditoría y futuras extensiones.  
- La tesis puede argumentar que el enfoque híbrido maximiza transparencia y aprendizaje, cumpliendo con el objetivo de recomendaciones nutricionales basadas en Random Forest.
