from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
# Erlaubt Anfragen von deiner Website (CORS-Lösung)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_data = request.json
        user_msg = user_data.get("message")
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return jsonify({"reply": "Konfigurationsfehler: API_KEY fehlt."})

        # Wir nutzen die stabile v1-API mit dem bewährten gemini-pro Modell
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Du bist der BALTON KI-Assistent. Antworte kurz und hilfsbereit auf Deutsch zu unseren Regalsystemen (BIII, ETAGAIR, KUBUS). Nutzerfrage: {user_msg}"}]
            }]
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        # Prüfung der Antwortstruktur von Google
        if 'candidates' in result and len(result['candidates']) > 0:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            # Gibt die Fehlermeldung der API für das Debugging zurück
            error_msg = result.get('error', {}).get('message', 'Keine gültige Antwort von der KI.')
            return jsonify({"reply": f"KI-Schnittstellenfehler: {error_msg}"})
            
    except Exception as e:
        return jsonify({"reply": f"Systemfehler: {str(e)}"})

if __name__ == "__main__":
    # Render nutzt standardmäßig Port 10000
    app.run(host='0.0.0.0', port=10000)
