from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


sintomas = {
    'dolor_cabeza': ctrl.Antecedent(np.arange(0, 6, 1), 'dolor_cabeza'),
    'fatiga': ctrl.Antecedent(np.arange(0, 6, 1), 'fatiga'),
    'dificultad_resp': ctrl.Antecedent(np.arange(0, 6, 1), 'dificultad_resp'),
    'temperatura': ctrl.Antecedent(np.arange(0, 6, 1), 'temperatura'),
    'dolor_articular': ctrl.Antecedent(np.arange(0, 6, 1), 'dolor_articular'),
    'apetito': ctrl.Antecedent(np.arange(0, 6, 1), 'apetito'),
    'tos': ctrl.Antecedent(np.arange(0, 6, 1), 'tos'),
    'opresion_pecho': ctrl.Antecedent(np.arange(0, 6, 1), 'opresion_pecho'),
    'mareos': ctrl.Antecedent(np.arange(0, 6, 1), 'mareos'),
    'cambios_piel': ctrl.Antecedent(np.arange(0, 6, 1), 'cambios_piel')
}


especialistas = {
    'medico_general': ctrl.Consequent(np.arange(0, 11, 1), 'medico_general'),
    'neumologo': ctrl.Consequent(np.arange(0, 11, 1), 'neumologo'),
    'cardiologo': ctrl.Consequent(np.arange(0, 11, 1), 'cardiologo'),
    'reumatologo': ctrl.Consequent(np.arange(0, 11, 1), 'reumatologo'),
    'dermatologo': ctrl.Consequent(np.arange(0, 11, 1), 'dermatologo'),
    'gastroenterologo': ctrl.Consequent(np.arange(0, 11, 1), 'gastroenterologo'),
    'neurologo': ctrl.Consequent(np.arange(0, 11, 1), 'neurologo'),
    'infectologo': ctrl.Consequent(np.arange(0, 11, 1), 'infectologo'),
    'otorrinolaringologo': ctrl.Consequent(np.arange(0, 11, 1), 'otorrinolaringologo')
}


for sintoma in sintomas.values():
    sintoma['bajo'] = fuzz.trimf(sintoma.universe, [0, 0, 2])
    sintoma['medio'] = fuzz.trimf(sintoma.universe, [1, 2.5, 4])
    sintoma['alto'] = fuzz.trimf(sintoma.universe, [3, 5, 5])

# Funciones de pertenencia para especialistas
for esp in especialistas.values():
    esp['bajo'] = fuzz.trimf(esp.universe, [0, 0, 4])
    esp['medio'] = fuzz.trimf(esp.universe, [2, 5, 8])
    esp['alto'] = fuzz.trimf(esp.universe, [6, 10, 10])



reglas = [

    ctrl.Rule(
        sintomas['fatiga']['alto'] | sintomas['temperatura']['alto'] |
        sintomas['dolor_cabeza']['alto'] | sintomas['apetito']['alto'],
        especialistas['medico_general']['alto']
    ),

    ctrl.Rule(
        sintomas['dificultad_resp']['alto'] & sintomas['tos']['alto'],
        especialistas['neumologo']['alto']
    ),

    ctrl.Rule(
        sintomas['opresion_pecho']['alto'] & sintomas['mareos']['alto'],
        especialistas['cardiologo']['alto']
    ),

    ctrl.Rule(
        sintomas['dolor_articular']['alto'] & sintomas['fatiga']['alto'],
        especialistas['reumatologo']['alto']
    ),

    ctrl.Rule(
        sintomas['cambios_piel']['alto'] & sintomas['temperatura']['alto'],
        especialistas['dermatologo']['alto']
    ),

    ctrl.Rule(
        sintomas['apetito']['alto'],
        especialistas['gastroenterologo']['alto']
    ),

    ctrl.Rule(
        sintomas['dolor_cabeza']['alto'] & sintomas['mareos']['alto'],
        especialistas['neurologo']['alto']
    ),

    ctrl.Rule(
        sintomas['temperatura']['alto'] & sintomas['tos']['alto'],
        especialistas['infectologo']['alto']
    ),
    
    ctrl.Rule(
        sintomas['dolor_cabeza']['alto'] & sintomas['tos']['alto'],
        especialistas['otorrinolaringologo']['alto']
    )
]

sistema_control = ctrl.ControlSystem(reglas)
sistema_simulacion = ctrl.ControlSystemSimulation(sistema_control)

@csrf_exempt
def reglasDifusas(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            respuestas = data.get('respuestas', [])
            if len(respuestas) < 10:
                return JsonResponse({"error": "Faltan respuestas en el cuestionario."}, status=400)
            
            inputs = {
                'dolor_cabeza': float(respuestas[0]['respuesta']),
                'fatiga': float(respuestas[1]['respuesta']),
                'dificultad_resp': float(respuestas[2]['respuesta']),
                'temperatura': float(respuestas[3]['respuesta']),
                'dolor_articular': float(respuestas[4]['respuesta']),
                'apetito': float(respuestas[5]['respuesta']),
                'tos': float(respuestas[6]['respuesta']),
                'opresion_pecho': float(respuestas[7]['respuesta']),
                'mareos': float(respuestas[8]['respuesta']),
                'cambios_piel': float(respuestas[9]['respuesta'])
            }

            for key, value in inputs.items():
                sistema_simulacion.input[key] = value

            print("sistema_simulacion")
            print(sistema_simulacion.input)
            
            sistema_simulacion.compute()
            print("exito")
            resultados = {}
            for esp_nombre, esp_consecuente in especialistas.items():
                try:
                    resultados[esp_nombre] = sistema_simulacion.output[esp_consecuente.label]
                except KeyError:
                    print("Error en " + esp_nombre)
                    resultados[esp_nombre] = 0.0
            print("resultados")
            print(resultados)
            umbral = 5.0
            recomendaciones = [esp for esp, score in resultados.items() if score >= umbral]
            
            if not recomendaciones:
                recomendaciones.append("Evaluación general recomendada")

            return JsonResponse({
                "especialistas_recomendados": recomendaciones,
                "puntuaciones_difusas": resultados
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Error en el formato JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)