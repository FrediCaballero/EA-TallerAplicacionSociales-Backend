from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)

# Habilitar CORS en todas las rutas
CORS(app)

# URLs de los microservicios
AUTH_SERVICE_URL = "https://backend-autenticacion.onrender.com/auth"
TASKS_SERVICE_URL = "https://backend-tareas-comentarios.onrender.com/tasks"
NOTIFICATIONS_SERVICE_URL = "https://backend-notificaciones-6wot.onrender.com/notify"

# Rutas del API Gateway

# Ruta para verificar que el servicio está funcionando
@app.route('/')
def home():
    return jsonify({"message": "API GATEWAY en funcionamiento"}), 200

# Registro de usuario
@app.route('/register', methods=['POST'])
def register():
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al comunicarse con el servicio de autenticación", "details": str(e)}), 500

# Inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/login", json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al comunicarse con el servicio de autenticación", "details": str(e)}), 500

# Crear una nueva tarea
@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        # Crear la tarea en el servicio de tareas
        response = requests.post(f"{TASKS_SERVICE_URL}", json=request.get_json())

        # Si la tarea se crea correctamente, enviar la notificación
        if response.status_code == 201:
            task = response.json()  # La tarea recién creada
            notification_data = {
                "message": f"Se ha creado una nueva tarea: {task['title']}",  # Título de la tarea
                "email": task.get('assigned_to')  # Suponiendo que cada tarea tiene un ID de usuario asignado
            }
            # Enviar la notificación usando el servicio de notificaciones
            notification_response = requests.post(f"{NOTIFICATIONS_SERVICE_URL}", json=notification_data)

            if notification_response.status_code != 200:
                return jsonify({"error": "Error al enviar la notificación"}), 500

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al comunicarse con el servicio de tareas", "details": str(e)}), 500
   

# Listar todas las tareas
@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        response = requests.get(f"{TASKS_SERVICE_URL}")
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al comunicarse con el servicio de tareas", "details": str(e)}), 500

# Agregar un comentario a una tarea
@app.route('/tasks/<int:task_id>/comments', methods=['POST'])
def add_comment(task_id):
    try:
        response = requests.post(f"{TASKS_SERVICE_URL}/{task_id}/comments", json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al comunicarse con el servicio de tareas", "details": str(e)}), 500

# Obtener comentarios de una tarea
@app.route('/tasks/<int:task_id>/comments', methods=['GET'])
def get_comments(task_id):
    try:
        response = requests.get(f"{TASKS_SERVICE_URL}/{task_id}/comments")
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al comunicarse con el servicio de tareas", "details": str(e)}), 500

# Cambiar estado de una tarea
@app.route('/tasks/<int:task_id>/status', methods=['PATCH'])
def update_task_status(task_id):
    try:
        response = requests.patch(f"{TASKS_SERVICE_URL}/{task_id}/status", json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al comunicarse con el servicio de tareas", "details": str(e)}), 500

# Eliminar una tarea
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        response = requests.delete(f"{TASKS_SERVICE_URL}/{task_id}")
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al comunicarse con el servicio de tareas", "details": str(e)}), 500

# Enviar una notificación
@app.route('/notify', methods=['POST'])
def send_notification():
    try:
        response = requests.post(f"{NOTIFICATIONS_SERVICE_URL}", json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al comunicarse con el servicio de notificaciones", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
