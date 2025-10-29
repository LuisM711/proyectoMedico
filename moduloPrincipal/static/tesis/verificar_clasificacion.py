#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación del algoritmo de clasificación científico.
Verifica que los datos del usuario se clasifiquen correctamente.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Agregar el directorio del script de entrenamiento al path
sys.path.append(str(Path(__file__).parent))

# Importar las funciones del script de entrenamiento
from entrenar import build_label

def test_user_data():
    """
    Verifica la clasificación con los datos reales del usuario.
    Estos datos deberían resultar en riesgo "alto".
    """
    print("🔬 VERIFICACIÓN DEL ALGORITMO CIENTÍFICO")
    print("="*50)
    
    # Datos del usuario (deberían ser riesgo ALTO)
    user_data = {
        "SEQN": [1],
        "RIDAGEYR": [35],  # Edad estimada
        "RIAGENDR": [2],   # Mujer
        "BMI": [37.0],     # Obesidad severa (≥35)
        "SBP": [170.0],    # Hipertensión severa (≥140)  
        "DBP": [105.0],    # Hipertensión severa (≥90)
        "DR1TKCAL": [2400.0],
        "pct_protein": [27.5],
        "pct_carb": [75.0],   # Desequilibrio (>65%)
        "pct_fat": [0.0],     # Desequilibrio (<20%)
        "DR1TSUGR": [87.5],   # Azúcar alto
        "DR1TFIBE": [27.5],   # Fibra adecuada para mujer
        "DR1TSODI": [3500.0], # Sodio muy alto (>2300mg)
        "is_smoker": [1.0],   # Fumador
        "alcohol_days": [4.5],
        "phys_act_days": [4.5]
    }
    
    # Crear DataFrame
    df = pd.DataFrame(user_data)
    
    # Mapeo de columnas (simulando lo que hace engineer_features)
    colmap = {
        "age": "RIDAGEYR",
        "sex": "RIAGENDR", 
        "glucose": None,  # No disponible
        "hdl": None,      # No disponible
        "ldl": None,      # No disponible
        "tg": None,       # No disponible
        "kcal": "DR1TKCAL",
        "sugar_g": "DR1TSUGR",
        "fiber_g": "DR1TFIBE", 
        "sodium_mg": "DR1TSODI"
    }
    
    print("📊 DATOS DE ENTRADA:")
    print(f"   BMI: {user_data['BMI'][0]} (Obesidad severa - Umbral: ≥35)")
    print(f"   SBP: {user_data['SBP'][0]} mmHg (Hipertensión severa - Umbral: ≥140)")
    print(f"   DBP: {user_data['DBP'][0]} mmHg (Hipertensión severa - Umbral: ≥90)")
    print(f"   Fumador: {'Sí' if user_data['is_smoker'][0] else 'No'}")
    print(f"   Sodio: {user_data['DR1TSODI'][0]} mg (Muy alto - Umbral: >2300)")
    print(f"   Carbohidratos: {user_data['pct_carb'][0]}% (Desequilibrio - Rango: 45-65%)")
    print(f"   Grasas: {user_data['pct_fat'][0]}% (Desequilibrio - Rango: 20-35%)")
    
    print("\n🧮 APLICANDO ALGORITMO CIENTÍFICO...")
    
    try:
        # Aplicar el algoritmo de etiquetado científico
        labels_df, metadata = build_label(df, colmap)
        
        result = labels_df.iloc[0]
        risk_label = result["risk_label"]
        risk_score = result["risk_score"]
        
        print(f"\n📈 RESULTADOS:")
        print(f"   Risk Score: {risk_score:.1f}/100")
        print(f"   Clasificación: {risk_label.upper()}")
        
        # Análisis detallado
        print(f"\n📋 ANÁLISIS POR FACTOR:")
        
        # Factor antropométrico (20%)
        bmi_points = 0
        if user_data['BMI'][0] >= 40:
            bmi_points = 20.0
        elif user_data['BMI'][0] >= 35:
            bmi_points = 16.0
        elif user_data['BMI'][0] >= 30:
            bmi_points = 12.0
        elif user_data['BMI'][0] >= 25:
            bmi_points = 6.0
        print(f"   🏃 Antropométrico: {bmi_points}/20 pts (BMI {user_data['BMI'][0]})")
        
        # Factor hemodinámico (25%)
        bp_points = 0
        if user_data['SBP'][0] >= 180 or user_data['DBP'][0] >= 120:
            bp_points = 25.0
        elif user_data['SBP'][0] >= 140 or user_data['DBP'][0] >= 90:
            bp_points = 20.0
        elif user_data['SBP'][0] >= 130 or user_data['DBP'][0] >= 80:
            bp_points = 12.5
        elif user_data['SBP'][0] >= 120:
            bp_points = 5.0
        print(f"   🩺 Hemodinámico: {bp_points}/25 pts (PA {user_data['SBP'][0]}/{user_data['DBP'][0]})")
        
        # Factor conductual (10%)
        behavioral_points = 0
        if user_data['is_smoker'][0] == 1:
            behavioral_points += 5.0
        if user_data['phys_act_days'][0] < 2:
            behavioral_points += 4.0
        elif user_data['phys_act_days'][0] < 3:
            behavioral_points += 2.0
        print(f"   🚭 Conductual: {behavioral_points}/10 pts (Fumador + Actividad)")
        
        estimated_total = bmi_points + bp_points + behavioral_points
        print(f"\n   🔢 Estimado mínimo: {estimated_total} pts (solo factores disponibles)")
        
        print(f"\n🎯 CLASIFICACIÓN ESPERADA vs REAL:")
        expected = "ALTO" if risk_score > 55 else ("MODERADO" if risk_score > 25 else "BAJO")
        print(f"   Esperada: {expected} (score > 55)")
        print(f"   Obtenida: {risk_label.upper()}")
        
        if risk_label == "alto":
            print("   ✅ CORRECTO: Clasificación apropiada para este perfil de riesgo")
        else:
            print("   ❌ PROBLEMA: Debería clasificarse como riesgo ALTO")
            print("   💡 Posible causa: Modelo entrenado con algoritmo anterior")
            
        return risk_label, risk_score
        
    except Exception as e:
        print(f"❌ ERROR en la verificación: {e}")
        return None, None

def recommend_action(risk_label, risk_score):
    """Recomienda la acción a tomar."""
    print(f"\n🎯 RECOMENDACIÓN:")
    
    if risk_label != "alto":
        print("   🔄 RE-ENTRENAR EL MODELO:")
        print("     python entrenar.py")
        print("   ")
        print("   El modelo actual fue entrenado con el algoritmo anterior.")
        print("   Necesita re-entrenamiento con el nuevo sistema científico.")
    else:
        print("   ✅ El algoritmo está funcionando correctamente.")
        print("   El modelo está actualizado con el sistema científico.")

if __name__ == "__main__":
    risk_label, risk_score = test_user_data() 
    
    if risk_label is not None:
        recommend_action(risk_label, risk_score)
    
    print(f"\n📚 Para más detalles consulta: ALGORITMO_ETIQUETADO.md")
