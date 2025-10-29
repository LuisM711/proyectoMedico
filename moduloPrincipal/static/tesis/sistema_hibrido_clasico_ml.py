#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Híbrido: Clásico + Machine Learning
Combina validación teórica con precisión empírica.

Este módulo implementa un sistema de clasificación híbrido que:
1. Usa sistema clásico basado en reglas (transparencia + validación teórica)
2. Usa Random Forest aprendido de datos reales (precisión + interacciones complejas)
3. Combina ambos para mayor confianza y robustez
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, Tuple, List

# ============================================================================
# SISTEMA CLÁSICO (Reglas Explícitas Basadas en Literatura)
# ============================================================================

class SistemaClasico:
    """
    Sistema de clasificación basado en reglas explícitas.
    Umbrales basados en: AHA/ACC 2019, ADA 2023, ATP IV, WHO 2023
    """
    
    def __init__(self):
        self.peso_factores = {
            'antropometrico': 20,
            'hemodinamico': 25,
            'metabolico': 30,
            'nutricional': 15,
            'conductual': 10
        }
    
    def calcular_score(self, datos: Dict) -> Tuple[float, str, Dict]:
        """
        Calcula score clásico basado en reglas explícitas.
        
        Returns:
            (score_total, etiqueta, desglose)
        """
        score = 0.0
        desglose = {}
        
        # 1. Factor Antropométrico (20%)
        if 'BMI' in datos and not pd.isna(datos['BMI']):
            bmi = datos['BMI']
            max_bmi = self.peso_factores['antropometrico']
            
            if bmi >= 40:
                pts = max_bmi * 1.0
            elif bmi >= 35:
                pts = max_bmi * 0.8
            elif bmi >= 30:
                pts = max_bmi * 0.6
            elif bmi >= 25:
                pts = max_bmi * 0.3
            else:
                pts = 0
                
            score += pts
            desglose['antropometrico'] = {
                'BMI': bmi,
                'puntos': pts,
                'max_posibles': max_bmi
            }
        
        # 2. Factor Hemodinámico (25%)
        if 'SBP' in datos and 'DBP' in datos:
            sbp = datos['SBP']
            dbp = datos.get('DBP', 0)
            max_bp = self.peso_factores['hemodinamico']
            
            # Verificar crisis
            if sbp >= 180 or dbp >= 120:
                pts = max_bp * 1.0
                clasif = 'Crisis'
            elif sbp >= 140 or dbp >= 90:
                pts = max_bp * 0.8
                clasif = 'Hipertensión II'
            elif sbp >= 130 or dbp >= 80:
                pts = max_bp * 0.5
                clasif = 'Hipertensión I'
            elif sbp >= 120:
                pts = max_bp * 0.2
                clasif = 'Elevada'
            else:
                pts = 0
                clasif = 'Normal'
            
            score += pts
            desglose['hemodinamico'] = {
                'SBP': sbp,
                'DBP': dbp,
                'clasificacion': clasif,
                'puntos': pts,
                'max_posibles': max_bp
            }
        
        # 3. Factor Metabólico (30%)
        score_metabolico = 0.0
        factores_metabolicos = 0
        desglose['metabolico'] = {}
        
        # Glucosa (7.5% del total = 25% del factor metabólico)
        if 'GLU' in datos and not pd.isna(datos['GLU']):
            glu = datos['GLU']
            if glu >= 126:
                score_metabolico += 7.5
                clasif = 'Diabetes'
            elif glu >= 100:
                score_metabolico += 3.75
                clasif = 'Prediabetes'
            else:
                clasif = 'Normal'
            desglose['metabolico']['GLU'] = {'valor': glu, 'clasificacion': clasif}
            factores_metabolicos += 1
        
        # HDL diferenciado por sexo (7.5%)
        if 'HDL' in datos and 'sex' in datos:
            hdl = datos['HDL']
            sex = datos['sex']
            es_masculino = (sex == 1)
            
            umbral_bajo = 40 if es_masculino else 50
            if hdl <= umbral_bajo:
                score_metabolico += 6
                clasif = 'Bajo'
            else:
                clasif = 'Normal'
            desglose['metabolico']['HDL'] = {'valor': hdl, 'clasificacion': clasif}
            factores_metabolicos += 1
        
        # LDL (7.5%)
        if 'LDL' in datos and not pd.isna(datos['LDL']):
            ldl = datos['LDL']
            if ldl >= 190:
                score_metabolico += 7.5
                clasif = 'Muy alto'
            elif ldl >= 160:
                score_metabolico += 6
                clasif = 'Alto'
            elif ldl >= 130:
                score_metabolico += 3
                clasif = 'Limítrofe'
            else:
                clasif = 'Normal'
            desglose['metabolico']['LDL'] = {'valor': ldl, 'clasificacion': clasif}
            factores_metabolicos += 1
        
        # Triglicéridos (7.5%)
        if 'TG' in datos and not pd.isna(datos['TG']):
            tg = datos['TG']
            if tg >= 500:
                score_metabolico += 7.5
                clasif = 'Muy alto'
            elif tg >= 200:
                score_metabolico += 4.5
                clasif = 'Alto'
            elif tg >= 150:
                score_metabolico += 2.25
                clasif = 'Limítrofe'
            else:
                clasif = 'Normal'
            desglose['metabolico']['TG'] = {'valor': tg, 'clasificacion': clasif}
            factores_metabolicos += 1
        
        if factores_metabolicos > 0:
            score += score_metabolico
            desglose['metabolico']['puntos'] = score_metabolico
            desglose['metabolico']['max_posibles'] = self.peso_factores['metabolico']
        
        # 4. Factor Nutricional (15%)
        score_nutricional = 0.0
        factores_nutricionales = 0
        desglose['nutricional'] = {}
        
        # Exceso calórico (simplificado)
        if 'kcal' in datos and not pd.isna(datos['kcal']):
            # Estimación TMB simplificada
            edad = datos.get('age', 40)
            sex = datos.get('sex', 1)
            
            if sex == 1:  # Masculino
                tmb = 88.362 + (13.397 * 70) + (4.799 * 175) - (5.677 * max(edad, 20))
            else:  # Femenino
                tmb = 447.593 + (9.247 * 60) + (3.098 * 162) - (4.330 * max(edad, 20))
            
            necesidades = tmb * 1.6
            
            if datos['kcal'] > necesidades * 1.3:
                score_nutricional += 4
                clasif = 'Excesivo'
            elif datos['kcal'] > necesidades * 1.1:
                score_nutricional += 2
                clasif = 'Moderado'
            else:
                clasif = 'Adecuado'
            
            desglose['nutricional']['calorias'] = {'valor': datos['kcal'], 'clasificacion': clasif}
            factores_nutricionales += 1
        
        # Desequilibrio macronutrientes
        if all(k in datos for k in ['pct_protein', 'pct_carb', 'pct_fat']):
            desequilibrio = 0
            for macro, (nombre, rango) in [
                ('pct_protein', ('proteína', (10, 35))),
                ('pct_carb', ('carbohidratos', (45, 65))),
                ('pct_fat', ('grasas', (20, 35)))
            ]:
                valor = datos[macro]
                if valor < rango[0] or valor > rango[1]:
                    desequilibrio += 1
            
            if desequilibrio > 0:
                score_nutricional += 5.0 * (desequilibrio / 3.0)
            
            desglose['nutricional']['macronutrientes'] = {'desequilibrios': desequilibrio}
            factores_nutricionales += 1
        
        if factores_nutricionales > 0:
            score += score_nutricional
            desglose['nutricional']['puntos'] = score_nutricional
            desglose['nutricional']['max_posibles'] = self.peso_factores['nutricional']
        
        # 5. Factor Conductual (10%)
        score_conductual = 0.0
        desglose['conductual'] = {}
        
        # Tabaquismo (5%)
        if 'is_smoker' in datos and not pd.isna(datos['is_smoker']):
            if datos['is_smoker'] == 1:
                score_conductual += 5
                clasif = 'Fumador'
            else:
                clasif = 'No fumador'
            desglose['conductual']['tabaquismo'] = clasif
        
        # Actividad física (5%)
        if 'phys_act_days' in datos and not pd.isna(datos['phys_act_days']):
            act = datos['phys_act_days']
            if act < 2:
                score_conductual += 4
                clasif = 'Sedentario'
            elif act < 3:
                score_conductual += 2
                clasif = 'Insuficiente'
            else:
                clasif = 'Adecuado'
            desglose['conductual']['actividad_fisica'] = clasif
        
        if any('tabaquismo' in desglose.get('conductual', {}) or 
               'actividad_fisica' in desglose.get('conductual', {}) 
               for _ in [None]):
            score += score_conductual
            desglose['conductual']['puntos'] = score_conductual
            desglose['conductual']['max_posibles'] = self.peso_factores['conductual']
        
        # Normalizar score (0-100)
        score_total_pesado = sum([
            desglose.get('antropometrico', {}).get('max_posibles', 0),
            desglose.get('hemodinamico', {}).get('max_posibles', 0),
            desglose.get('metabolico', {}).get('max_posibles', 0),
            desglose.get('nutricional', {}).get('max_posibles', 0),
            desglose.get('conductual', {}).get('max_posibles', 0),
        ])
        
        if score_total_pesado > 0:
            score_normalizado = min((score / score_total_pesado) * 100, 100)
        else:
            score_normalizado = np.nan
        
        # Clasificación
        if pd.isna(score_normalizado):
            etiqueta = "No determinado"
        elif score_normalizado <= 25:
            etiqueta = "saludable"
        elif score_normalizado <= 55:
            etiqueta = "moderado"
        else:
            etiqueta = "alto"
        
        desglose['summary'] = {
            'score_raw': score,
            'score_max': score_total_pesado,
            'score_normalized': score_normalizado,
            'label': etiqueta
        }
        
        return score_normalizado, etiqueta, desglose


# ============================================================================
# SISTEMA MACHINE LEARNING (Random Forest)
# ============================================================================

class SistemaML:
    """
    Sistema de clasificación basado en Random Forest.
    Modelo entrenado con datos NHANES.
    """
    
    def __init__(self, modelo_path: Path = None):
        if modelo_path is None:
            base_dir = Path(__file__).parent
            modelo_path = base_dir / "model_artifacts" / "risk_profile_model.joblib"
        
        try:
            self.modelo = joblib.load(modelo_path)
            self.cargado = True
        except Exception as e:
            print(f"⚠️ No se pudo cargar modelo ML: {e}")
            self.modelo = None
            self.cargado = False
    
    def predecir(self, datos: Dict) -> Tuple[str, float, Dict]:
        """
        Hace predicción con Random Forest.
        
        Returns:
            (etiqueta, confianza, probabilidades)
        """
        if not self.cargado:
            return None, 0.0, {}
        
        try:
            # Preparar datos en formato correcto para el modelo
            # (Esto requiere mapear los campos según lo que el modelo espera)
            # Por simplicidad, asumimos que datos ya están en formato correcto
            prediccion = self.modelo.predict(pd.DataFrame([datos]))[0]
            probabilidades = self.modelo.predict_proba(pd.DataFrame([datos]))[0]
            clases = self.modelo.classes_
            
            probas_dict = {clase: float(prob) for clase, prob in zip(clases, probabilidades)}
            confianza = float(max(probabilidades))
            
            return prediccion, confianza, probas_dict
            
        except Exception as e:
            print(f"⚠️ Error en predicción ML: {e}")
            return None, 0.0, {}


# ============================================================================
# SISTEMA HÍBRIDO (Combina Ambos)
# ============================================================================

class SistemaHibrido:
    """
    Sistema híbrido que combina enfoque clásico y machine learning.
    
    Ventajas:
    - Validación teórica (clásico)
    - Precisión empírica (ML)
    - Mayor robustez y confianza
    """
    
    def __init__(self):
        self.clasico = SistemaClasico()
        self.ml = SistemaML()
    
    def clasificar(self, datos: Dict) -> Dict:
        """
        Clasificación híbrida combinando ambos sistemas.
        
        Returns:
            {
                'etiqueta_final': str,
                'confianza': str,
                'score_clasico': float,
                'label_clasico': str,
                'label_ml': str,
                'probas_ml': dict,
                'desglose_clasico': dict,
                'concordancia': bool,
                'recomendacion': str
            }
        """
        # Clasificación clásica
        score_clasico, label_clasico, desglose = self.clasico.calcular_score(datos)
        
        # Clasificación ML
        if self.ml.cargado:
            label_ml, confianza_ml, probas_ml = self.ml.predecir(datos)
        else:
            label_ml = None
            confianza_ml = 0.0
            probas_ml = {}
        
        # Análisis de concordancia
        if label_ml:
            concordancia = (label_clasico == label_ml)
            
            if concordancia:
                confianza = "Alta"
                recomendacion = f"Ambos sistemas concuerdan: {label_clasico}. Confianza alta."
                etiqueta_final = label_clasico
            else:
                confianza = "Media"
                etiqueta_final = label_ml  # Priorizar ML
                recomendacion = f"Discrepancia. Sistema clásico: {label_clasico}, ML: {label_ml}. " \
                               f"Se prioriza ML por análisis empírico."
        else:
            concordancia = None
            confianza = "Alta"
            recomendacion = "Solo sistema clásico disponible. Validación teórica."
            etiqueta_final = label_clasico
        
        # Análisis adicional
        confianza_percentil = "Baja" if score_clasico < 30 else "Media" if score_clasico < 60 else "Alta"
        
        return {
            'etiqueta_final': etiqueta_final,
            'confianza': confianza,
            'confianza_detallada': {
                'conceptual': 'Alta',  # Clásico siempre tiene base teórica
                'empirica': 'Alta' if label_ml else 'No disponible',
                'concordancia': concordancia,
                'percentil_riesgo': confianza_percentil
            },
            'score_clasico': float(score_clasico),
            'label_clasico': label_clasico,
            'label_ml': label_ml if label_ml else 'No disponible',
            'probas_ml': probas_ml,
            'desglose_clasico': desglose,
            'concordancia': concordancia,
            'recomendacion': recomendacion,
            'interpretacion': self._interpretar_resultado(etiqueta_final, score_clasico, probas_ml)
        }
    
    def _interpretar_resultado(self, etiqueta: str, score: float, probas: dict) -> str:
        """Genera interpretación clínica del resultado."""
        if etiqueta == "saludable":
            return f"Perfil de riesgo bajo (score={score:.1f}). Mantener hábitos actuales."
        elif etiqueta == "moderado":
            return f"Riesgo intermedio (score={score:.1f}). Modificaciones preventivas recomendadas."
        else:  # alto
            return f"Alto riesgo cardiometabólico (score={score:.1f}). Intervención médica prioritaria."


# ============================================================================
# USO
# ============================================================================

if __name__ == "__main__":
    # Ejemplo de uso
    print("🔬 SISTEMA HÍBRIDO: Clásico + Machine Learning\n")
    
    # Datos de ejemplo
    datos_paciente = {
        'age': 35,
        'sex': 2,  # Femenino
        'BMI': 37.0,
        'SBP': 170,
        'DBP': 105,
        'GLU': None,  # No disponible
        'HDL': None,
        'LDL': None,
        'TG': None,
        'kcal': 2400,
        'pct_protein': 27.5,
        'pct_carb': 75,
        'pct_fat': 0,
        'is_smoker': 1,
        'phys_act_days': 4.5
    }
    
    # Clasificación híbrida
    sistema = SistemaHibrido()
    resultado = sistema.clasificar(datos_paciente)
    
    print(f"📊 RESULTADO HÍBRIDO:")
    print(f"   Etiqueta final: {resultado['etiqueta_final'].upper()}")
    print(f"   Confianza: {resultado['confianza']}")
    print(f"   Score clásico: {resultado['score_clasico']:.1f}/100")
    print(f"   Sistema clásico: {resultado['label_clasico']}")
    print(f"   ML: {resultado['label_ml']}")
    print(f"   Concordancia: {resultado['concordancia']}")
    print(f"\n   Recomendación: {resultado['recomendacion']}")
    print(f"\n   Interpretación: {resultado['interpretacion']}")
