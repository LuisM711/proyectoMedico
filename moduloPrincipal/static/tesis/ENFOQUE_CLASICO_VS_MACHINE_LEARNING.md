# enfoque clásico vs machine learning

## contexto del proyecto

La primera iteración del asistente combinaba reglas fijas (IMC, presión arterial, lípidos) con un modelo `RandomForest`. Durante la validación bibliográfica se decidió sustituir ese esquema por un **cuestionario nutricional de 10 ítems** respaldado por NHANES 2017‑2018 y guías internacionales. La versión actual utiliza únicamente reglas explícitas:

- Cada respuesta se convierte en puntos (0‑10 máximo, 5 para suplementos).
- La suma se normaliza a 0‑100 y se clasifica en saludable / moderado / alto.
- El detalle por pregunta permite auditar la recomendación.

## ventajas del enfoque basado en reglas

| criterio | reglas explícitas | modelos de machine learning |
| --- | --- | --- |
| transparencia | ✅ 100 % explicable | ⚠️ depende del algoritmo |
| evidencia | ✅ citas directas por pregunta | ⚠️ requiere justificar dataset |
| mantenimiento | ✅ cambios editando tablas | ⚠️ reentrenamiento / replicación |
| requisitos de datos | ✅ no necesita datos sensibles | ⚠️ exige dataset balanceado |
| trazabilidad | ✅ mismo resultado para misma entrada | ⚠️ posible deriva del modelo |

## cuándo considerar un modelo de aprendizaje

- Si se incorporan **biomarcadores** (glucosa, HDL, triglicéridos) y se cuenta con registros etiquetados.
- Si se desea **personalizar pesos** según sexo, edad o comorbilidades.
- Cuando la institución disponga de un dataset propio ≥5 000 observaciones para entrenar y validar.

En ese escenario se recomienda:

1. Mantener el score clásico como capa base (explicabilidad).
2. Entrenar un modelo supervisado que prediga la misma etiqueta.
3. Comparar métricas (F1 macro, balanced accuracy) y realizar validación cruzada.
4. Documentar el pipeline, el conjunto de entrenamiento y el control de versiones del modelo.

## resumen para la tesis

- **Estado actual:** sistema 100 % determinístico basado en guías (ver `nutri_scorecard.py`).
- **Beneficio clave:** evita alucinaciones, facilita auditorías y ahorra mantenimiento.
- **Trabajo a futuro:** incorporar un módulo ML opcional para investigación o benchmarking, manteniendo el score científico como referencia.
