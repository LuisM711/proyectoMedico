# Tabla Resumen de Umbrales para Perfil Nutricional

## 📊 Resumen Ejecutivo de Clasificación

| **Etiqueta** | **Score** | **Definición** | **Riesgo CV 10 años** | **Acción Recomendada** |
|:------------:|:---------:|:---------------|:---------------------:|:----------------------:|
| 🟢 **Saludable** | 0-25 | Perfil óptimo con factores de riesgo mínimos | <10% | Mantener hábitos + monitoreo |
| 🟡 **Moderado** | 26-55 | Factores de riesgo presentes, prevención efectiva | 10-20% | Modificar estilo de vida |
| 🔴 **Alto** | 56-100 | Múltiples factores, intervención inmediata | >20% | Atención médica prioritaria |

---

## 🎯 Tabla Maestra de Umbrales y Puntuación

### **FACTOR ANTROPOMÉTRICO** (20% del score total)
| **BMI (kg/m²)** | **Clasificación** | **Puntos** | **Peso Relativo** |
|:---------------:|:------------------|:----------:|:-----------------:|
| 18.5-24.9 | Normal | 0 | 0% |
| 25.0-29.9 | Sobrepeso | 6 | 30% |
| 30.0-34.9 | Obesidad I | 12 | 60% |
| 35.0-39.9 | Obesidad II | 16 | 80% |
| ≥40.0 | Obesidad III | 20 | 100% |

### **FACTOR HEMODINÁMICO** (25% del score total)
| **PA Sistólica** | **PA Diastólica** | **Clasificación** | **Puntos** | **Peso Relativo** |
|:----------------:|:-----------------:|:------------------|:----------:|:-----------------:|
| <120 | <80 | Normal | 0 | 0% |
| 120-129 | <80 | Elevada | 5 | 20% |
| 130-139 | 80-89 | Hipertensión I | 12.5 | 50% |
| 140-179 | 90-119 | Hipertensión II | 20 | 80% |
| ≥180 | ≥120 | Crisis | 25 | 100% |

### **FACTOR METABÓLICO** (30% del score total = 7.5% cada subfactor)

#### **Glucosa en Ayuno**
| **mg/dL** | **Clasificación** | **Puntos** | **Peso Relativo** |
|:---------:|:------------------|:----------:|:-----------------:|
| <100 | Normal | 0 | 0% |
| 100-125 | Prediabetes | 3.75 | 50% |
| ≥126 | Diabetes | 7.5 | 100% |

#### **HDL Colesterol (Diferenciado por Sexo)**
| **Masculino (mg/dL)** | **Femenino (mg/dL)** | **Clasificación** | **Puntos** |
|:---------------------:|:--------------------:|:------------------|:----------:|
| ≥50 | ≥60 | Normal | 0 |
| 40-49 | 50-59 | Limítrofe | 3 |
| <40 | <50 | Bajo | 6 |

#### **LDL Colesterol**
| **mg/dL** | **Clasificación** | **Puntos** | **Peso Relativo** |
|:---------:|:------------------|:----------:|:-----------------:|
| <100 | Óptimo | 0 | 0% |
| 100-129 | Casi óptimo | 1.5 | 20% |
| 130-159 | Limítrofe | 3 | 40% |
| 160-189 | Alto | 6 | 80% |
| ≥190 | Muy alto | 7.5 | 100% |

#### **Triglicéridos**
| **mg/dL** | **Clasificación** | **Puntos** | **Peso Relativo** |
|:---------:|:------------------|:----------:|:-----------------:|
| <150 | Normal | 0 | 0% |
| 150-199 | Limítrofe | 2.25 | 30% |
| 200-499 | Alto | 4.5 | 60% |
| ≥500 | Muy alto | 7.5 | 100% |

### **FACTOR NUTRICIONAL** (15% del score total)

#### **Exceso Calórico** (5% del total)
| **% de Necesidades TMB** | **Clasificación** | **Puntos** |
|:------------------------:|:------------------|:----------:|
| ≤110% | Adecuado | 0 |
| 110-130% | Moderado | 2 |
| >130% | Excesivo | 4 |

#### **Desequilibrio Macronutrientes** (5% del total)
| **Macronutriente** | **Rango Óptimo** | **Penalización por Desvío** |
|:-------------------|:----------------:|:---------------------------:|
| Proteínas | 10-35% kcal | 1.67 puntos |
| Carbohidratos | 45-65% kcal | 1.67 puntos |
| Grasas | 20-35% kcal | 1.67 puntos |

#### **Micronutrientes Críticos** (5% del total)
| **Componente** | **Umbral Riesgo** | **Puntos Máximos** |
|:---------------|:------------------:|:------------------:|
| Azúcar añadido | >10% kcal totales | 2.5 |
| Fibra (Hombre) | <19g/día (50% de 38g) | 2.0 |
| Fibra (Mujer) | <12.5g/día (50% de 25g) | 2.0 |

### **FACTOR CONDUCTUAL** (10% del score total)

#### **Tabaquismo** (5% del total)
| **Estado** | **Puntos** |
|:-----------|:----------:|
| No fumador | 0 |
| Fumador activo | 5 |

#### **Actividad Física** (5% del total)
| **Días/Semana** | **Clasificación** | **Puntos** |
|:---------------:|:------------------|:----------:|
| ≥3 | Adecuado | 0 |
| 2 | Insuficiente | 2 |
| <2 | Sedentario | 4 |

---

## 🔢 Fórmula de Cálculo Final

```
Score Final = (Puntos Antropométrico + Puntos Hemodinámico + 
               Puntos Metabólico + Puntos Nutricional + 
               Puntos Conductual) / (Puntos Máximos Posibles) × 100

Donde:
- Puntos Máximos Posibles = Suma de factores con datos disponibles
- Normalización asegura score 0-100 independiente de datos faltantes
```

### **Ejemplo de Cálculo**
**Paciente:** Mujer, 35 años, BMI=37, PA=170/105, Fumadora
```
Factor Antropométrico: BMI 37 → Obesidad II → 16/20 puntos
Factor Hemodinámico: 170/105 → Hipertensión II → 20/25 puntos  
Factor Conductual: Fumadora → 5/5 puntos (tabaquismo)

Total: 41 puntos de 50 posibles = (41/50) × 100 = 82/100
Clasificación: ALTO (>55)
```

---

## 📈 Distribución Esperada de Scores

**Basado en datos NHANES y validación clínica:**

| **Rango Score** | **Etiqueta** | **% Población Esperado** | **Interpretación** |
|:---------------:|:------------:|:------------------------:|:-------------------|
| 0-15 | Saludable Óptimo | 15-20% | Excelente estado de salud |
| 16-25 | Saludable | 25-30% | Buen estado general |
| 26-40 | Moderado Bajo | 20-25% | Algunos factores a mejorar |
| 41-55 | Moderado Alto | 15-20% | Varios factores de riesgo |
| 56-70 | Alto | 10-15% | Múltiples factores |
| 71-100 | Alto Crítico | 5-10% | Intervención urgente |

---

## 🎨 Código de Colores para Visualización

```css
/* Saludable */
.score-saludable {
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    color: white;
}

/* Moderado */
.score-moderado {
    background: linear-gradient(135deg, #FFC107 0%, #FF9800 100%);
    color: white;
}

/* Alto */
.score-alto {
    background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%);
    color: white;
}
```

---

## 📋 Lista de Verificación para Implementación

### ✅ **Para Desarrolladores**
- [ ] Validar que todos los umbrales estén implementados correctamente
- [ ] Verificar cálculo de ponderaciones (suma debe ser 100%)
- [ ] Probar casos extremos (todos los factores máximos/mínimos)
- [ ] Validar manejo de datos faltantes

### ✅ **Para Clínicos**
- [ ] Revisar umbrales con literatura médica actualizada
- [ ] Validar aplicabilidad a población objetivo
- [ ] Considerar ajustes por edad/etnia si necesario
- [ ] Establecer protocolos de seguimiento por categoría

### ✅ **Para Investigación**
- [ ] Documentar fuentes de todos los umbrales
- [ ] Calcular sensibilidad/especificidad vs gold standard
- [ ] Analizar distribución de scores en población de estudio
- [ ] Validar predictibilidad de outcomes cardiovasculares

---

*Documento técnico para implementación y validación del algoritmo de perfil nutricional - Proyecto de tesis en Ingeniería de Software*
