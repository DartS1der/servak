from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feeder.db'
app.config['SECRET_KEY'] = 'ваш_секретный_ключ'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    feeders = db.relationship('Feeder', backref='owner', lazy=True)

# Модель кормушки
class Feeder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    schedule = db.Column(db.String(255), default="[]")  # JSON: [{"time": "12:00", "grams": 50}]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Регистрация
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = generate_password_hash(data.get('password'))
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Пользователь уже существует"}), 400
    
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True})

# Авторизация
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password, data.get('password')):
        login_user(user)
        return jsonify({"success": True})
    return jsonify({"error": "Неверный логин или пароль"}), 401

# Получить данные кормушки (для ESP32)
@app.route('/feeder/<int:feeder_id>', methods=['GET'])
def get_feeder_data(feeder_id):
    feeder = Feeder.query.get(feeder_id)
    if not feeder:
        return jsonify({"error": "Кормушка не найдена"}), 404
    return jsonify({"schedule": feeder.schedule})

# Обновить расписание (для приложения)
@app.route('/feeder/<int:feeder_id>/update', methods=['POST'])
@login_required
def update_feeder(feeder_id):
    feeder = Feeder.query.get(feeder_id)
    if not feeder or feeder.owner.id != current_user.id:
        return jsonify({"error": "Доступ запрещён"}), 403
    
    feeder.schedule = request.json.get('schedule')
    db.session.commit()
    return jsonify({"success": True})

if name == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
