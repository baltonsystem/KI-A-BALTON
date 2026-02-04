from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Deine trainierten System-Instructions
SYSTEM_PROMPT = """
Du bist der offizielle KI-Assistent von BALTON.
WISSEN:
- Produkte: Regalsysteme BIII (B3), ETAGAIR, KUBUS. Made in Germany.
- Versand: DHL, DPD, GLS. Paletten per DB Schenker (bis Bordsteinkante).
- Zahlung: Vorkasse (Überweisung), PayPal, Kreditkarte. Keine Barzahlung bei Abholung.
- Kontakt: info@balton.com.
STIL: Deutsch, professionell, freundlich. Antworte kurz und präzise.
"""

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_data = request.json
        user_msg = user_data.get("message")
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return jsonify({"reply": "Fehler: API_KEY fehlt in den Render-Einstellungen."})

        # Wir nutzen den v1beta Endpunkt, der am besten mit kostenlosen Keys funktioniert
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "role": "user", 
                    "parts": [{"text": f"System-Anweisung: {SYSTEM_PROMPT}\n\nNutzer-Frage: {user_msg}"}]
                }
            ]
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            # Zeigt den exakten Fehlergrund von Google an (z.B. Key ungültig)
            error_msg = result.get('error', {}).get('message', 'Keine Antwort von Google erhalten.')
            return jsonify({"reply": f"KI-Fehler: {error_msg}"})
            
    except Exception as e:
        return jsonify({"reply": f"System-Fehler: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
