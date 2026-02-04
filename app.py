from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_data = request.json
        user_msg = user_data.get("message")
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return jsonify({"reply": "Konfigurationsfehler: API_KEY fehlt."})

        # KORRIGIERTE URL: Wir nutzen v1beta und das korrekte Modell-Format
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Du bist der BALTON KI-Assistent. Antworte kurz und hilfsbereit auf Deutsch zu den Regalsystemen BIII und ETAGAIR. Frage: {user_msg}"}]
            }]
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            # Zeigt uns den exakten Fehler von Google, falls es noch hakt
            error_details = result.get('error', {}).get('message', 'Unbekannter KI-Fehler')
            return jsonify({"reply": f"KI-Schnittstellenfehler: {error_details}"})
            
    except Exception as e:
        return jsonify({"reply": f"Systemfehler: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
