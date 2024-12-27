from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos de la base de datos
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    assigned_to = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False)
    visible = db.Column(db.Boolean, default=True, nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# Crear la base de datos
with app.app_context():
    db.create_all()

## Rutas para el servicio de tareas

# Ruta para verificar que el servicio está funcionando
@app.route('/')
def home():
    return jsonify({"message": "Servicio de Tareas y Comentarios en funcionamiento"}), 200

# Crear una nueva tarea
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    if not data or 'title' not in data or 'description' not in data or 'assigned_to' not in data:
        return jsonify({"error": "Faltan datos requeridos: 'title', 'description', 'assigned_to'"}), 400

    new_task = Task(
        title=data['title'],
        description=data['description'],
        assigned_to=data['assigned_to']
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "assigned_to": new_task.assigned_to,
        "status": new_task.status
    }), 201

# Obtener todas las tareas
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.filter_by(visible=True).all()
    return jsonify([{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "assigned_to": task.assigned_to,
        "status": task.status
    } for task in tasks]), 200

# Modificar el estado de una tarea
@app.route('/tasks/<int:task_id>/status', methods=['PATCH'])
def update_task_status(task_id):
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"error": "Falta el campo 'status'"}), 400

    task = Task.query.get(task_id)
    if task and task.visible:
        task.status = data['status']
        db.session.commit()
        return jsonify({"message": "Estado de la tarea actualizado", "task": {
            "id": task.id,
            "title": task.title,
            "status": task.status
        }}), 200

    return jsonify({"error": "Tarea no encontrada o no visible"}), 404

# Eliminar una tarea (eliminación lógica)
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.visible = False
        db.session.commit()
        return jsonify({"message": "Tarea eliminada correctamente"}), 200

    return jsonify({"error": "Tarea no encontrada"}), 404

# Agregar un comentario a una tarea
@app.route('/tasks/<int:task_id>/comments', methods=['POST'])
def add_comment(task_id):
    data = request.get_json()

    if not data or 'user' not in data or 'comment' not in data:
        return jsonify({"error": "Faltan datos requeridos: 'user', 'comment'"}), 400

    task = Task.query.get(task_id)
    if task and task.visible:
        new_comment = Comment(
            task_id=task_id,
            user=data['user'],
            comment=data['comment']
        )
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({
            "id": new_comment.id,
            "task_id": new_comment.task_id,
            "user": new_comment.user,
            "comment": new_comment.comment,
            "timestamp": new_comment.timestamp.isoformat()
        }), 201

    return jsonify({"error": "Tarea no encontrada o no visible"}), 404

# Obtener los comentarios de una tarea
@app.route('/tasks/<int:task_id>/comments', methods=['GET'])
def get_comments(task_id):
    # Verificar que la tarea existe y es visible
    task = Task.query.get(task_id)
    if not task or not task.visible:
        return jsonify({"error": "Tarea no encontrada o no visible"}), 404

    # Obtener los comentarios de la tarea
    comments = Comment.query.filter_by(task_id=task_id).all()
    if not comments:
        return jsonify({"error": "No hay comentarios para esta tarea"}), 404

    return jsonify([{
        "id": comment.id,
        "user": comment.user,
        "comment": comment.comment,
        "timestamp": comment.timestamp.isoformat()
    } for comment in comments]), 200

if __name__ == '__main__':
    app.run(debug=True, port=5002)
