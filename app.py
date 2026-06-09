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
model = genai.GenerativeModel("gemini-1.5-flash")

HOTEL_INFO = """
Eres el asistente virtual del Hotel Real EF, el hotel más moderno y único de La Unión, Huánuco, Perú. 
Es el ÚNICO hotel con fachada de vidrio en toda la ciudad.

INFORMACIÓN GENERAL:
- Dirección: La Unión 10621, Provincia de Dos de Mayo, Huánuco, Perú
- Teléfono/WhatsApp: +51 946 049 780
- Check-in: 2:00 pm | Check-out: 12:00 pm
- Calificación: 5 estrellas en Google por huéspedes reales

HABITACIONES Y PRECIOS:
- Habitación simple (1 cama): desde S/40 por noche
- Habitación doble (2 camas): consultar precio
- Habitación con Jacuzzi: precio especial, consultar
- Todas incluyen: camas y puertas de madera de roble, mayólica en baños

SERVICIOS INCLUIDOS EN TODAS LAS HABITACIONES:
- WiFi de alta velocidad
- Netflix y TV cable
- Agua caliente con terma Y panel solar (nunca falta)
- Vista a la ciudad

CARACTERÍSTICAS ÚNICAS DEL HOTEL:
- Único hotel con fachada de vidrio en La Unión
- Vista panorámica 360 grados de toda La Unión desde la azotea (acceso libre)
- Infraestructura nueva, todo con mayólica — extremadamente limpio
- Cámaras de seguridad en TODOS los pisos con monitoreo constante
- Puertas y camas de madera de roble de calidad
- Cerca de la plaza y el mercado central
- Huéspedes de todo el mundo se hospedan aquí

SERVICIOS ADICIONALES:
- Estacionamiento de bicicletas y motos en el hotel
- Estacionamiento de autos a una cuadra
- Coordinación con restaurantes cercanos para delivery de almuerzo y desayuno

PUNTOS CLAVE PARA DESTACAR SIEMPRE:
1. La azotea con vista 360° de La Unión es GRATIS para todos los huéspedes
2. Seguridad total con cámaras en todos los pisos
3. El único edificio de vidrio — fácil de ubicar
4. Excelente relación calidad-precio (reseñas 5 estrellas en Google)

Responde siempre en español, de forma amable, entusiasta y breve.
Si preguntan por disponibilidad, pide fechas y número de personas, 
y diles que una asesora confirmará en minutos.
Si quieren reservar, diles que escriban al +51 946 049 780.
Si no sabes algo específico, di que consultarás y que llamen al +51 946 049 780.
Solo responde preguntas relacionadas al hotel.
"""

def ask_gemini(message):
    try:
        response = model.generate_content(HOTEL_INFO + "\nCliente pregunta: " + message)
        return response.text
    except Exception as e:
        return "Hola! Gracias por contactarnos. Para consultas llámanos al +51 946 049 780 📞"

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
        reply = ask_gemini(text)
        send_whatsapp(phone, reply)
    except:
        pass
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)