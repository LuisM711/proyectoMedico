"""Script para analizar la distribución del dataset y el uso del balanceador."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # Subir un nivel desde scripts/ a tesis/
DIST_FILE = ROOT / "model_artifacts" / "label_dist.json"
METADATA_FILE = ROOT / "model_artifacts" / "scientific_metadata.json"

print("=" * 60)
print("ANÁLISIS DEL DATASET DEL MODELO NUTRICIONAL")
print("=" * 60)

# Cargar distribución
with open(DIST_FILE, 'r', encoding='utf-8') as f:
    dist = json.load(f)

# Cargar metadatos
with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(f"\nTOTAL DE MUESTRAS: {dist['n_muestras']}")
print("\n" + "-" * 60)
print("DISTRIBUCION POR CLASE:")
print("-" * 60)

alto = dist['distribucion_etiquetas']['alto']
moderado = dist['distribucion_etiquetas']['moderado']
saludable = dist['distribucion_etiquetas']['saludable']
total = dist['n_muestras']

print(f"\nALTO (Riesgo alto):")
print(f"   - Cantidad: {alto:,} muestras")
print(f"   - Porcentaje: {dist['proporcion_etiquetas']['alto']*100:.2f}%")

print(f"\nMODERADO (Riesgo moderado):")
print(f"   - Cantidad: {moderado:,} muestras")
print(f"   - Porcentaje: {dist['proporcion_etiquetas']['moderado']*100:.2f}%")

print(f"\nSALUDABLE (Riesgo bajo):")
print(f"   - Cantidad: {saludable:,} muestras")
print(f"   - Porcentaje: {dist['proporcion_etiquetas']['saludable']*100:.2f}%")

print("\n" + "-" * 60)
print("ANALISIS DE DESBALANCE:")
print("-" * 60)

print(f"\nRazones de desbalance:")
print(f"   - Alto vs Saludable: {alto/saludable:.0f}:1")
print(f"   - Moderado vs Saludable: {moderado/saludable:.0f}:1")
print(f"   - Alto vs Moderado: {alto/moderado:.2f}:1")

print("\n" + "-" * 60)
print("BALANCEADOR UTILIZADO:")
print("-" * 60)

print(f"\nHiperparametro: class_weight='balanced'")
print(f"   - Tipo de modelo: {metadata['modelo']['tipo']}")
print(f"   - Numero de estimadores: {metadata['modelo']['n_estimators']}")
print(f"   - min_samples_leaf: {metadata['modelo']['min_samples_leaf']}")

print("\nQue hace class_weight='balanced'?")
print("   El balanceador ajusta automaticamente los pesos de las clases")
print("   de forma inversamente proporcional a su frecuencia:")
print(f"   - Peso para 'alto': {total/(3*alto):.4f}")
print(f"   - Peso para 'moderado': {total/(3*moderado):.4f}")
print(f"   - Peso para 'saludable': {total/(3*saludable):.4f}")

print("\n" + "-" * 60)
print("METRICAS DEL MODELO:")
print("-" * 60)

metrics = metadata['modelo']['metricas']
print(f"\nAccuracy global: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
print(f"\nPor clase:")
for clase in ['alto', 'moderado', 'saludable']:
    m = metrics[clase]
    print(f"\n  {clase.upper()}:")
    print(f"    - Precision: {m['precision']:.4f} ({m['precision']*100:.2f}%)")
    print(f"    - Recall: {m['recall']:.4f} ({m['recall']*100:.2f}%)")
    print(f"    - F1-Score: {m['f1']:.4f} ({m['f1']*100:.2f}%)")

print("\n" + "=" * 60)
print("RESUMEN:")
print("=" * 60)
print(f"Dataset muy desbalanceado (solo {saludable} muestras de 'saludable' vs {alto} de 'alto')")
print(f"Se utilizo class_weight='balanced' para compensar el desbalance")
print(f"El modelo logro excelentes metricas a pesar del desbalance extremo")
print("=" * 60)

