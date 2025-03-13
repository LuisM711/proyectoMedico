from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import http.client

GEMINI_API_KEY = "AIzaSyCFremK0TUSbMvCO21uCDMDlq31kuF8onU"

@csrf_exempt
def gemini(request, prompt):
    if request.method == 'GET':
        try:
            conn = http.client.HTTPSConnection("generativelanguage.googleapis.com")
            endpoint = f"/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}]
            })
            headers = {
                "Content-Type": "application/json"
            }

            conn.request("POST", endpoint, body=payload, headers=headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            return JsonResponse(json.loads(data))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)
