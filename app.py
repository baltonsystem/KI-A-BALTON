from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
# Erlaubt Anfragen von deiner spezifischen Domain
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_data = request.json
        user_msg = user_data.get("message")
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return jsonify({"reply": "Fehler: API_KEY fehlt in den Environment Variables."})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": user_msg}]}],
            "systemInstruction": {"parts": [{"text": "Du bist der BALTON KI-Assistent. Antworte freundlich auf Deutsch zu unseren Regalsystemen (BIII, ETAGAIR). Bei Reklamationen verweise an info@balton.com."}]}
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        # Sicherere Abfrage der Antwort
        if 'candidates' in result:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": f"KI-Fehler: {result.get('error', {}).get('message', 'Unbekannter Fehler')}"})
            
    except Exception as e:
        return jsonify({"reply": f"Server-Fehler: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
