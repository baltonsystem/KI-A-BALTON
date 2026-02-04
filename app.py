from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
# Erlaubt Anfragen von allen Quellen (CORS-Lösung)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_data = request.json
        user_msg = user_data.get("message")
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return jsonify({"reply": "Konfigurationsfehler: API-Key fehlt auf dem Server."})

        # Stabilere API-URL mit gemini-pro
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Du bist der BALTON KI-Assistent. Antworte freundlich und präzise auf Deutsch. Thema: BALTON Regalsysteme (BIII, ETAGAIR, KUBUS). Nutzerfrage: {user_msg}"}]
            }]
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        # Prüfung der KI-Antwort
        if 'candidates' in result and len(result['candidates']) > 0:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            # Zeigt den genauen Fehler der Google-API im Chat an
            error_msg = result.get('error', {}).get('message', 'Keine Antwort von KI erhalten.')
            return jsonify({"reply": f"KI-Schnittstellenfehler: {error_msg}"})
            
    except Exception as e:
        return jsonify({"reply": f"Systemfehler: {str(e)}"})

if __name__ == "__main__":
    # Port 10000 ist Standard für Render
    app.run(host='0.0.0.0', port=10000)
