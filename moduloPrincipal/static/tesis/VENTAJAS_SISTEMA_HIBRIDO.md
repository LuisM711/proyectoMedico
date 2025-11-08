# ventajas del sistema actual

## resumen ejecutivo

La nueva versión del asistente se apoya en un cuestionario nutricional con respaldo científico. El componente de machine learning quedó como **línea de investigación futura**. Mantener la noción de “sistema híbrido” sigue siendo útil porque:

- el score clásico garantiza trazabilidad y está listo para producción;
- se puede acoplar un modelo estadístico en caso de contar con datos adicionales;
- la comparación entre ambos enfoques fortalece la tesis.

## beneficios de la capa clásica

| aspecto | resultado |
| --- | --- |
| Transparencia | Cada pregunta tiene una referencia (DOI/ISBN) y un rango de puntuación documentado. |
| Auditoría | El backend devuelve el detalle de puntos por ítem, permitiendo justificar la recomendación. |
| Implementación | No requiere datasets sensibles ni entrenamiento periódico. |
| Cumplimiento | Facilita revisiones éticas y regulatorias porque todo el cálculo es determinístico. |

## por qué conservar la idea de híbrido

1. **Flexibilidad futura**  
   El módulo `nutri_scorecard` funciona como capa base. Si se desean incluir biomarcadores o señales clínicas, basta con entrenar un modelo supervisado y comparar su salida contra el score clásico.

2. **Metodología clara para la tesis**  
   En la memoria se puede explicar que se evaluaron dos rutas (reglas vs. ML) y se eligió la que garantiza evidencia y reproducibilidad. Documentar esta decisión es valioso académicamente.

3. **Proceso de validación dual (opcional)**  
   - El script `entrenar.py` genera estadísticas sintéticas para el score clásico.  
   - Si en el futuro se entrena un modelo, bastaría con añadir un bloque que compare la etiqueta del modelo con la etiqueta científica y reporte discrepancias.

## pasos propuestos si se reactiva la capa ML

1. Recolectar un dataset propio con respuestas al cuestionario y etiquetas clínicas.  
2. Entrenar un modelo (por ejemplo, `RandomForest` o `LogisticRegression`) usando el mismo pipeline de normalización.  
3. Validar con métricas (`balanced_accuracy`, `f1_macro`) y comparar contra el score clásico.  
4. Decidir reglas de conciliación: priorizar la etiqueta más conservadora o usar thresholds de confianza.  
5. Documentar los casos de discrepancia y las acciones recomendadas.

## conclusión

- El sistema actual es totalmente funcional con el score científico.  
- La arquitectura sigue preparada para un enfoque híbrido gracias a la separación entre la capa de puntuación (`nutri_scorecard`) y los scripts auxiliares (`entrenar.py`, `sistema_hibrido_clasico_ml.py`).  
- La tesis puede argumentar que se evaluaron ambas estrategias y que la versión estable prioriza la transparencia, sin descartar futuros experimentos con machine learning.
