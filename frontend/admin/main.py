"""
MFG Drone Admin Frontend
管理者用フロントエンド - 物体学習、ドローン制御、追跡開始/停止
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
import threading
import time
import logging

# Blueprints
from blueprints.tracking import tracking_bp

# Services
from services.tracking_service import tracking_service

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Flask-SocketIO初期化
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Blueprints登録
app.register_blueprint(tracking_bp)

@app.route('/')
def index():
    """メインダッシュボード"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}

# WebSocket イベントハンドラ
@socketio.on('connect')
def handle_connect():
    """WebSocket接続時"""
    logger.info('WebSocket client connected')
    emit('status', {'message': 'Connected to MFG Drone Admin'})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket切断時"""
    logger.info('WebSocket client disconnected')

@socketio.on('request_tracking_status')
def handle_tracking_status_request():
    """追跡状態要求"""
    try:
        status = tracking_service.get_tracking_status()
        emit('tracking_status', status)
    except Exception as e:
        logger.error(f"Tracking status request error: {e}")
        emit('tracking_error', {'message': str(e)})

# バックグラウンドタスク: 追跡状態監視
def background_tracking_monitor():
    """バックグラウンドで追跡状態を監視し、WebSocketで配信"""
    while True:
        try:
            status = tracking_service.get_tracking_status()
            if status.get('is_tracking'):
                socketio.emit('tracking_status', status)
        except Exception as e:
            logger.error(f"Background tracking monitor error: {e}")
            socketio.emit('tracking_error', {'message': str(e)})
        
        time.sleep(1)  # 1秒間隔

# バックグラウンドタスク開始
def start_background_tasks():
    """バックグラウンドタスクを開始"""
    monitor_thread = threading.Thread(target=background_tracking_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    logger.info("Background tracking monitor started")

if __name__ == '__main__':
    # バックグラウンドタスク開始
    start_background_tasks()
    
    # Flask-SocketIOでサーバー開始
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)