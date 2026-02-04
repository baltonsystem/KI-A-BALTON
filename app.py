from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
# Erlaubt Anfragen von deiner Website
CORS(app, resources={r"/*": {"origins": "*"}})

# Deine trainierten Informationen als System-Anweisung
SYSTEM_INSTRUCTIONS = """
Du bist der offizielle KI-Assistent von BALTON. 
Ton & Persönlichkeit: Deutsch, freundlich, professionell. Standardmäßig "Sie", außer der Nutzer duzt.
Wissensbasis:
- Produkte: Regalsysteme BIII (B3), ETAGAIR, KUBUS, Garderoben. Made in Germany.
- Versand: DHL, DPD, GLS. Paletten per DB Schenker (Bordsteinkante).
- Zahlung: Vorkasse (Überweisung), PayPal, Kreditkarte. Keine Barzahlung bei Abholung.
- Kontakt: info@balton.com.
Regeln: Keine verbindlichen Liefertermine, keine Rechtsberatung, keine Kundendaten im Chat.
Bei Unklarheiten verweise an den Support: info@balton.com.
"""

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_data = request.json
        user_msg = user_data.get("message")
        
        # Holt den Key aus den Render-Einstellungen (Environment)
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return jsonify({"reply": "Konfigurationsfehler: Bitte den API_KEY in Render hinterlegen."})

        # URL für das kostenlose Modell gemini-1.5-flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        # Hier verbinden wir dein Training mit der Nutzerfrage
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"SYSTEM-ANWEISUNG: {SYSTEM_INSTRUCTIONS}\n\nNUTZERFRAGE: {user_msg}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500
            }
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            # Zeigt den Fehler von Google an, falls der Key oder das Modell hakt
            error_msg = result.get('error', {}).get('message', 'Keine Antwort erhalten.')
            return jsonify({"reply": f"KI-Schnittstellenfehler: {error_msg}"})
            
    except Exception as e:
        return jsonify({"reply": f"System-Fehler: {str(e)}"})

if __name__ == "__main__":
    # Port 10000 ist der Standard für Render
    app.run(host='0.0.0.0', port=10000)
