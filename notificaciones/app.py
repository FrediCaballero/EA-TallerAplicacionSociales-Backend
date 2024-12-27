from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Ruta para verificar que el servicio está funcionando
@app.route('/')
def home():
    return "Servicio de Notificaciones en funcionamiento", 200

# Ruta para enviar notificaciones
@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.get_json()

    # Validar que el cuerpo de la solicitud contiene los datos necesarios
    if not data or 'email' not in data or 'message' not in data:
        return jsonify({"error": "Faltan los datos requeridos: 'email' y 'message'"}), 400

    # Validar formato de email
    email = data['email']
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Formato de correo electrónico inválido"}), 400

    message = data['message']

    # Simulación del envío de un correo electrónico
    print(f"Simulando envío de correo a {email} con el mensaje:\n{message}")

    # Aquí es donde integrarías el código real para enviar el correo (por ejemplo, usando smtplib o un servicio externo)

    return jsonify({"status": "Correo enviado exitosamente"}), 200

if __name__ == '__main__':
    app.run(debug=True)
