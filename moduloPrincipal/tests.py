import json

from django.test import Client, TestCase
from django.urls import reverse


class PerfilNutricionalAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("perfil_nutricional")

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_score_saludable(self):
        payload = {
            "scores": {
                "alcohol": 0,
                "frutas": 0,
                "verduras": 0,
                "bebidas_azucaradas": 0,
                "comida_rapida": 0,
                "agua": 0,
                "granos_integrales": 0,
                "sal_mesa": 0,
                "suplementos": 0,
                "desayuno": 0,
            }
        }
        response = self._post(payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["risk_label"], "saludable")
        self.assertAlmostEqual(data["score"], 0.0, places=1)
        self.assertIn("model_probabilities", data)
        self.assertGreater(data["model_probabilities"]["saludable"], 0.8)
        self.assertIn("model_features", data)
        self.assertEqual(data["model_features"]["alcohol"], 0.0)

    def test_score_alto(self):
        payload = {
            "scores": {
                "alcohol": 10,
                "frutas": 10,
                "verduras": 10,
                "bebidas_azucaradas": 10,
                "comida_rapida": 10,
                "agua": 10,
                "granos_integrales": 10,
                "sal_mesa": 10,
                "suplementos": 5,
                "desayuno": 10,
            }
        }
        response = self._post(payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["risk_label"], "alto")
        self.assertGreaterEqual(data["score"], 90)
        self.assertIn("model_probabilities", data)
        self.assertGreater(data["model_probabilities"]["alto"], 0.9)
        self.assertIn("model_metadata", data)
