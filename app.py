from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Crear la base de datos
with app.app_context():
    db.create_all()

## Rutas del microservicio

# Ruta para verificar que el servicio está funcionando
@app.route('/')
def home():
    return jsonify({"message": "Servicio de Autenticacion en funcionamiento"}), 200

# Registro de usuario
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validar que los datos necesarios estén presentes
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Faltan los campos 'email' y 'password'"}), 400

    # Validar formato de correo electrónico
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({"error": "Formato de correo electrónico inválido"}), 400

    # Verificar si el correo ya está registrado
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "El correo ya está registrado"}), 400

    # Crear un nuevo usuario con la contraseña cifrada
    hashed_password = generate_password_hash(data['password'], method='pbkdf2')
    new_user = User(email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuario registrado exitosamente"}), 201

# Inicio de sesión
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validar que los datos necesarios estén presentes
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Faltan los campos 'email' y 'password'"}), 400

    # Validar formato de correo electrónico
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({"error": "Formato de correo electrónico inválido"}), 400

    # Verificar si el correo existe
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Verificar la contraseña
    if not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Contraseña incorrecta"}), 401

    return jsonify({"message": "Inicio de sesión exitoso"}), 200

if __name__ == '__main__':
    app.run(debug=True)
