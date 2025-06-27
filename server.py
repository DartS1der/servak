from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')  # Фикс для Render
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-secret-key'  # Важно для сессий!
db = SQLAlchemy(app)

# Модели БД
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    feeders = db.relationship('Feeder', backref='user')

class Feeder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    schedule = db.Column(db.String(200))  # JSON: [{"time": "08:00", "grams": 50}]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Создаем таблицы при первом запуске
with app.app_context():
    db.create_all()

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        if User.query.filter_by(username=username).first():
            return "Пользователь уже существует!"
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        session['username'] = username
        return redirect(url_for('home'))
    
    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('home'))
        
        return "Неверный логин или пароль!"
    
    return render_template('login.html')

# Выход
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Главная страница
@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    return render_template('index.html', user=user)

# API для работы с кормушками
@app.route('/api/feeders', methods=['GET', 'POST'])
def feeders():
    if 'username' not in session:
        return jsonify({"error": "Требуется авторизация"}), 401
    
    user = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        data = request.json
        new_feeder = Feeder(
            name=data['name'],
            schedule=data['schedule'],
            user_id=user.id
        )
        db.session.add(new_feeder)
        db.session.commit()
        return jsonify({"success": True})
    
    # GET запрос - список кормушек
    feeders = [{"id": f.id, "name": f.name} for f in user.feeders]
    return jsonify({"feeders": feeders})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
