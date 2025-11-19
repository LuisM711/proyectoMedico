# Descripción de Gráficas Generadas

Este documento describe las gráficas generadas para la sección de resultados de la tesis.

## Ubicación de las Gráficas

Todas las gráficas se guardan en: `moduloPrincipal/static/tesis/graficas_resultados/`

## Gráficas Generadas

### 1. `01_distribucion_dataset.png`
**Título sugerido**: "Distribución del Dataset en Entrenamiento y Pruebas"

**Descripción**: 
- Muestra la distribución de clases (Alto, Moderado, Saludable) en los conjuntos de entrenamiento y prueba
- Dos gráficas de barras lado a lado
- Incluye el número de muestras y porcentajes por clase
- Similar a la sección de "División Estratificada" en el ejemplo de CNN

**Uso en tesis**: 
- Colocar después de la descripción del dataset
- Muestra que la división 80/20 se mantuvo estratificada por clase

---

### 2. `02_matriz_confusion.png`
**Título sugerido**: "Matriz de Confusión del Modelo Random Forest"

**Descripción**:
- Matriz de confusión con valores numéricos en cada celda
- Muestra cuántas muestras fueron clasificadas correctamente e incorrectamente
- Colores: azul (más intenso = más muestras)

**Uso en tesis**:
- Colocar después de las métricas de evaluación
- Permite visualizar los errores del modelo por clase
- Útil para explicar por qué ciertas clases tienen mejor rendimiento

---

### 3. `03_metricas_por_clase.png`
**Título sugerido**: "Métricas de Evaluación por Clase"

**Descripción**:
- Gráfica de barras agrupadas mostrando Precisión, Recall y F1-Score por clase
- Tres barras por clase (una para cada métrica)
- Colores diferenciados: azul (Precisión), verde (Recall), rojo (F1-Score)

**Uso en tesis**:
- Colocar junto a la Tabla 3 (Resultados con código en Python)
- Facilita la comparación visual de métricas entre clases
- Muestra que todas las clases tienen excelente rendimiento (>97%)

---

### 4. `04_importancia_caracteristicas.png`
**Título sugerido**: "Importancia de Características del Modelo Random Forest"

**Descripción**:
- Gráfica de barras horizontales mostrando la importancia de cada característica
- Ordenada de menor a mayor importancia
- Muestra qué preguntas del cuestionario son más relevantes para la clasificación

**Uso en tesis**:
- Útil para explicar qué factores nutricionales son más determinantes
- Puede usarse en la sección de análisis de resultados
- Ayuda a justificar la relevancia de cada pregunta del cuestionario

---

### 5. `05_curvas_aprendizaje.png`
**Título sugerido**: "Curvas de Aprendizaje del Modelo"

**Descripción**:
- Similar a las gráficas de "Accuracy durante el Entrenamiento" del ejemplo CNN
- Muestra cómo varía el accuracy con diferentes tamaños de conjunto de entrenamiento
- Dos líneas: Accuracy de Entrenamiento (azul) y Accuracy de Validación (rojo)
- Incluye bandas de desviación estándar (áreas sombreadas)

**Uso en tesis**:
- Colocar en la sección de análisis de resultados
- Demuestra que el modelo generaliza bien (no hay sobreajuste)
- Muestra estabilidad del modelo con diferentes tamaños de datos

---

## Cómo Generar las Gráficas

Las gráficas se generan automáticamente al ejecutar el entrenamiento del modelo:

```powershell
cd moduloPrincipal\static\tesis\scripts
.\ejecutar_entrenar.ps1
```

O desde el directorio raíz del proyecto:

```powershell
python -m moduloPrincipal.static.tesis.scripts.entrenar
```

Las gráficas se guardan automáticamente en `graficas_resultados/` junto con los artefactos del modelo.

---

## Notas para la Tesis

1. **Formato**: Todas las gráficas están en alta resolución (300 DPI) y listas para incluir en el documento
2. **Títulos**: Ajusta los títulos según el estilo de tu universidad
3. **Referencias**: Asegúrate de referenciar cada gráfica en el texto (ej: "Como se muestra en la Figura X...")
4. **Leyendas**: Las gráficas incluyen leyendas y etiquetas, pero puedes ajustarlas si es necesario
5. **Colores**: Los colores están optimizados para impresión en blanco y negro (usando diferentes tonos de gris)

---

## Comparación con el Ejemplo de CNN

| Aspecto | CNN (Compañero) | Random Forest (Tu modelo) |
|---------|------------------|---------------------------|
| Gráfica de Loss | Sí (épocas) | No aplica (no hay épocas) |
| Gráfica de Accuracy | Sí (épocas) | Sí (curvas de aprendizaje) |
| Tiempo por época | Sí | No aplica |
| Distribución dataset | Sí | Sí |
| Matriz de confusión | Implícita | Sí (explícita) |
| Importancia características | No | Sí (ventaja del RF) |

**Ventaja**: El Random Forest proporciona información adicional (importancia de características) que las CNN no ofrecen directamente.

---

## Sugerencias de Mejora

Si quieres agregar más gráficas, puedes considerar:

1. **Gráfica de distribución de scores**: Mostrar la distribución de scores normalizados por clase
2. **Gráfica de correlación**: Matriz de correlación entre características
3. **Gráfica de comparación de modelos**: Si entrenaste múltiples modelos con diferentes hiperparámetros

