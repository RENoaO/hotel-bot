from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import os

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WA_TOKEN = os.environ.get("WA_TOKEN")
WA_PHONE_ID = os.environ.get("WA_PHONE_ID")
VERIFY_TOKEN = "hotelrealef2024"

genai.configure(api_key=GEMINI_API_KEY)

HOTEL_INFO = """
Eres el asistente virtual del Hotel Real EF, el hotel más moderno y único de La Unión, Huánuco, Perú.
Es el ÚNICO hotel con fachada de vidrio en toda la ciudad.

INFORMACIÓN GENERAL:
- Dirección: La Unión 10621, Provincia de Dos de Mayo, Huánuco, Perú
- Teléfono/WhatsApp: +51 946 049 780
- Check-in: 2:00 pm | Check-out: 12:00 pm
- Calificación: 5 estrellas en Google

HABITACIONES Y PRECIOS:
- Habitación simple (1 cama): desde S/40 por noche
- Habitación doble (2 camas): consultar precio
- Habitación con Jacuzzi: precio especial, consultar
- Todas con camas y puertas de madera de roble

SERVICIOS INCLUIDOS:
- WiFi, Netflix, TV cable
- Agua caliente con terma y panel solar
- Vista panorámica 360 grados desde azotea (acceso libre)
- Cámaras de seguridad en todos los pisos
- Estacionamiento de bicicletas y motos
- Estacionamiento de autos a una cuadra
- Delivery de comida coordinado con restaurantes cercanos

Responde siempre en español, amable y breve.
Para reservas dirígelos al +51 946 049 780.
Solo responde preguntas del hotel.
"""

def ask_gemini(message):
    try:
        client = genai.GenerativeModel("gemini-2.0-flash-lite")
        response = client.generate_content(HOTEL_INFO + "\nCliente pregunta: " + message)
        return response.text
    except Exception as e:
        print(f"Error Gemini: {e}")
        return "¡Hola! Bienvenido al Hotel Real EF 🏨 Para consultas y reservas contáctanos al +51 946 049 780 📞"

def send_whatsapp(phone, message):
    url = f"https://graph.facebook.com/v18.0/{WA_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = msg["from"]
        text = msg["text"]["body"]
        print(f"Mensaje de {phone}: {text}")
        reply = ask_gemini(text)
        print(f"Respuesta: {reply}")
        send_whatsapp(phone, reply)
    except Exception as e:
        print(f"Error webhook: {e}")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)