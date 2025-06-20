"""
MFG Drone Admin Frontend
管理者用フロントエンド - 物体学習、ドローン制御、追跡開始/停止
"""

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/connection')
def connection():
    return render_template('connection.html')

@app.route('/flight')
def flight():
    return render_template('flight.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/sensors')
def sensors():
    return render_template('sensors.html')

@app.route('/models')
def models():
    return render_template('models.html')

@app.route('/tracking')
def tracking():
    return render_template('tracking.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/health')
def health_check():
    return {"status": "healthy"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)