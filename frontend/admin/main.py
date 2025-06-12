"""
MFG Drone Admin Frontend
管理者用フロントエンド - 物体学習、ドローン制御、追跡開始/停止
"""

from flask import Flask, render_template
from flask_socketio import SocketIO
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Register Blueprints
from blueprints.camera import camera_bp
app.register_blueprint(camera_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera')
def camera():
    return render_template('camera/dashboard.html')

@app.route('/health')
def health_check():
    return {"status": "healthy"}

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

if __name__ == '__main__':
    logger.info('Starting MFG Drone Admin Frontend')
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)