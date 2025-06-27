from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

# Маршрут для главной страницы
@app.route('/')
def home():
    return render_template('index.html')

# API для получения расписания кормления
@app.route('/api/schedule')
def get_schedule():
    return jsonify({
        "schedule": [
            {"time": "08:00", "grams": 50},
            {"time": "20:00", "grams": 70}
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
