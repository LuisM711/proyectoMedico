from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Nota: En producción, usa la protección CSRF adecuada.
def reglasDifusas(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            respuestas = data.get('respuestas', [])
            
            if len(respuestas) < 10:
                return JsonResponse({"error": "Faltan respuestas en el cuestionario."}, status=400)
            
            sintomas = {
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
            scores = {
                "Médico General (Atención Primaria)": sintomas['fatiga'] + sintomas['temperatura'] + sintomas['dolor_cabeza'] + sintomas['apetito'],
                "Neumólogo (Sistema Respiratorio)": sintomas['dificultad_resp'] + sintomas['tos'] + sintomas['opresion_pecho'],
                "Cardiólogo (Corazón)": sintomas['opresion_pecho'] + sintomas['mareos'] + sintomas['dificultad_resp'],
                "Reumatólogo (Huesos/Músculos)": sintomas['dolor_articular'] + sintomas['fatiga'] + sintomas['cambios_piel'],
                "Dermatólogo (Piel)": sintomas['cambios_piel'] + sintomas['temperatura'],
                "Gastroenterólogo": sintomas['apetito'],
                "Neurólogo": sintomas['dolor_cabeza'] + sintomas['mareos'],
                "Infectólogo": sintomas['temperatura'] + sintomas['tos'] + sintomas['dificultad_resp'],
                "Otorrinolaringólogo": sintomas['dolor_cabeza'] + sintomas['tos']
            }

            umbrales = {
                "Médico General (Atención Primaria)": 12,
                "Neumólogo (Sistema Respiratorio)": 8,
                "Cardiólogo (Corazón)": 10,
                "Reumatólogo (Huesos/Músculos)": 9,
                "Dermatólogo (Piel)": 7,
                "Gastroenterólogo": 3,
                "Neurólogo": 6,
                "Infectólogo": 8,
                "Otorrinolaringólogo": 7
            }
            recomendaciones = [especialidad for especialidad, score in scores.items() 
                              if score >= umbrales.get(especialidad, float('inf'))]
            if not recomendaciones:
                recomendaciones.append("No se requiere especialista específico; se recomienda evaluación general.")

            result = {
                "especialista": recomendaciones,
                "scores": scores
            }
            return JsonResponse(result, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Error en el formato JSON."}, status=400)
        except KeyError as e:
            return JsonResponse({"error": f"Falta la clave: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error procesando los datos: {str(e)}"}, status=400)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)