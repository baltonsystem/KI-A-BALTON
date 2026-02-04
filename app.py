from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
# Erlaubt Anfragen von deiner Website (CORS)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 1. Daten empfangen
        user_data = request.json
        user_msg = user_data.get("message")
        api_key = os.environ.get("GEMINI_API_KEY")
        
        # Sicherheits-Check
        if not api_key:
            return jsonify({"reply": "Server-Fehler: API-Key fehlt."})

        # 2. Anfrage an Google (Wir nutzen hier v1 und gemini-pro für Stabilität)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Du bist der BALTON KI-Assistent. Antworte kurz, freundlich und hilfreich auf Deutsch. Thema: Regalsysteme (BIII, ETAGAIR). Frage des Kunden: {user_msg}"}]
            }]
        }
        
        # 3. Senden und Antwort verarbeiten
        response = requests.post(url, json=payload)
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            # Zeigt den genauen Fehler an, falls Google blockiert
            error_msg = result.get('error', {}).get('message', 'Keine Antwort erhalten.')
            return jsonify({"reply": f"KI-Fehler: {error_msg}"})
            
    except Exception as e:
        return jsonify({"reply": f"System-Fehler: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
