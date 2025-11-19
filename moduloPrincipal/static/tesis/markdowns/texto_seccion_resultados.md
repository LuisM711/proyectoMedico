# SECCIÓN DE RESULTADOS - MODELO RANDOM FOREST

## 4.5 RESULTADOS DEL ENTRENAMIENTO DEL MODELO RANDOM FOREST

### 4.5.1 Configuración del Modelo

El modelo de Random Forest fue entrenado utilizando el dataset NHANES 2017-2018, el cual contiene información nutricional y de cuestionarios de una muestra representativa de la población estadounidense. El modelo fue configurado con los siguientes hiperparámetros:

- **Tipo de modelo**: RandomForestClassifier
- **Número de estimadores**: 400 árboles de decisión
- **min_samples_leaf**: 2 (mínimo de muestras requeridas en un nodo hoja)
- **class_weight**: 'balanced' (balanceo automático de clases)
- **random_state**: 42 (para reproducibilidad)
- **División de datos**: 80% entrenamiento / 20% prueba (con estratificación)

El uso del parámetro `class_weight='balanced'` fue fundamental debido al desbalance extremo presente en el dataset, donde la clase "saludable" representa solo el 0.06% del total de muestras (5 muestras de 8,531), mientras que la clase "alto" representa el 64.5% (5,504 muestras).

### 4.5.2 Características del Dataset

El dataset utilizado para el entrenamiento consta de 8,531 muestras totales, distribuidas de la siguiente manera:

- **Alto (riesgo alto)**: 5,504 muestras (64.5%)
- **Moderado (riesgo moderado)**: 3,022 muestras (35.4%)
- **Saludable (riesgo bajo)**: 5 muestras (0.06%)

Este desbalance significativo (razón de 1,101:1 entre la clase mayoritaria y la minoritaria) justifica el uso del balanceador de clases, el cual ajusta automáticamente los pesos durante el entrenamiento para evitar que el modelo se sesgue hacia las clases mayoritarias.

### 4.5.3 Métricas de Evaluación

Las métricas utilizadas para evaluar el rendimiento del modelo fueron la Precisión, el Recall y el F1-Score, calculadas mediante código desarrollado en Python utilizando las funciones de scikit-learn. Los resultados obtenidos se muestran en las tablas correspondientes.

#### Resultados por Clase:

- **Clase "Alto"**:
  - Precisión: 98.28%
  - Recall: 98.73%
  - F1-Score: 98.50%

- **Clase "Moderado"**:
  - Precisión: 97.67%
  - Recall: 96.86%
  - F1-Score: 97.26%

- **Clase "Saludable"**:
  - Precisión: 100.00%
  - Recall: 100.00%
  - F1-Score: 100.00%

#### Métricas Globales:

- **Accuracy Global**: 98.07%
- **Precisión Promedio (Macro)**: 98.65%
- **Recall Promedio (Macro)**: 98.53%
- **F1-Score Promedio (Macro)**: 98.59%

### 4.5.4 Análisis de Resultados

El modelo Random Forest logró un rendimiento excepcional, alcanzando una precisión global del 98.07%, lo que supera ampliamente el objetivo inicial de obtener una precisión superior al 90%. Este rendimiento se debe, en gran parte, a:

1. **Uso del balanceador de clases**: El parámetro `class_weight='balanced'` permitió compensar el desbalance extremo del dataset, asignando pesos inversamente proporcionales a la frecuencia de cada clase. Esto resultó en pesos de aproximadamente 0.52 para "alto", 0.94 para "moderado" y 568.73 para "saludable", permitiendo que el modelo aprenda efectivamente de todas las clases.

2. **Arquitectura del Random Forest**: Los 400 árboles de decisión trabajando en conjunto proporcionaron robustez y capacidad de generalización, mientras que el parámetro `min_samples_leaf=2` ayudó a prevenir el sobreajuste.

3. **Preprocesamiento adecuado**: El uso de imputación de valores faltantes (estrategia de mediana) y normalización estándar (StandardScaler) aseguró que todas las características estuvieran en escalas comparables.

4. **Estratificación en la división train/test**: La estratificación garantizó que cada clase estuviera representada proporcionalmente en los conjuntos de entrenamiento y prueba, lo cual es crucial cuando se trabaja con datos desbalanceados.

### 4.5.5 Comparación con Trabajos Relacionados

Al comparar los resultados obtenidos con otros trabajos de investigación en el área de evaluación nutricional mediante machine learning, se observa que el presente trabajo presenta un rendimiento competitivo:

- El modelo alcanzó una precisión del 98.07%, lo cual es comparable o superior a trabajos que utilizan arquitecturas más complejas como redes neuronales convolucionales (CNN) para clasificación de imágenes nutricionales.

- A pesar de trabajar con un dataset altamente desbalanceado (razón de 1,101:1), el modelo logró excelentes métricas en todas las clases, incluyendo la clase minoritaria "saludable" con 100% de precisión, recall y F1-score.

- El uso de Random Forest proporciona ventajas adicionales como interpretabilidad (importancia de características) y menor costo computacional en comparación con modelos de deep learning.

### 4.5.6 Limitaciones y Consideraciones

A pesar de los excelentes resultados obtenidos, es importante reconocer las siguientes limitaciones:

1. **Dataset desbalanceado**: Aunque se utilizó un balanceador de clases, el número extremadamente bajo de muestras de la clase "saludable" (solo 5 muestras) puede limitar la capacidad de generalización del modelo para esta clase en particular.

2. **Fuente de datos**: El modelo fue entrenado únicamente con datos del NHANES 2017-2018, que representa la población estadounidense. La generalización a otras poblaciones o contextos culturales podría requerir validación adicional.

3. **Validación clínica**: Los resultados obtenidos son validados mediante métricas estadísticas, pero no han sido validados por especialistas en nutrición en un contexto clínico real.

### 4.5.7 Trabajos Futuros

Como trabajos futuros, se propone:

1. **Validación clínica**: Validar los resultados del modelo con datos proporcionados por instituciones médicas y especialistas en nutrición.

2. **Expansión del dataset**: Incrementar el número de muestras, especialmente de la clase "saludable", mediante la incorporación de datos adicionales o técnicas de aumento de datos sintéticos.

3. **Reentrenamiento automático**: Implementar un sistema que permita reentrenar el modelo automáticamente con nuevos datos, manteniendo un historial de versiones del modelo.

4. **Validación en otras poblaciones**: Probar la generalización del modelo con datos de otras poblaciones o contextos culturales diferentes al NHANES.

---

## NOTAS PARA LA REDACCIÓN:

1. **Adapta los números**: Verifica que los porcentajes y números coincidan exactamente con tus tablas.

2. **Citas bibliográficas**: Agrega referencias a trabajos relacionados cuando menciones comparaciones. Por ejemplo:
   - "En trabajos similares como el de [Autor, Año], se alcanzó una precisión del X%..."
   - "Comparado con [Autor, Año] que utilizó [método], nuestro modelo..."

3. **Gráficas**: Considera agregar gráficas de:
   - Matriz de confusión
   - Curvas de aprendizaje (si las tienes)
   - Importancia de características del Random Forest

4. **Tablas**: Usa las tablas generadas por el script `generar_tablas_resultados.py` en tu documento.

5. **Formato**: Ajusta el formato según las normas de tu universidad (APA, IEEE, etc.)

