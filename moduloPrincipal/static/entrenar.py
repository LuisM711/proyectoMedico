import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib
with open('dataset.json', 'r', encoding='utf-8') as file:
    dataset = json.load(file)
X = [dato["paciente"] for dato in dataset]
y = [dato["especialista"] for dato in dataset]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
modelo = make_pipeline(TfidfVectorizer(), MultinomialNB())
modelo.fit(X_train, y_train)
y_pred = modelo.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
joblib.dump(modelo, 'modelo_especialistas.pkl')