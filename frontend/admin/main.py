"""
MFG Drone Admin Frontend
管理者用フロントエンド - 物体学習、ドローン制御、追跡開始/停止
Flask-SocketIOを使用したリアルタイム通信対応
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
import logging
import threading
import time
from blueprints.drone import drone_bp
from services.api_client import api_client

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask アプリケーション初期化
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Flask-SocketIO 初期化
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Blueprint 登録
app.register_blueprint(drone_bp)

# グローバル状態管理
app_state = {
    "monitoring": False,
    "connected_clients": 0
}

@app.route('/')
def index():
    """メインダッシュボード"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """ヘルスチェック"""
    backend_health = api_client.health_check()
    return {
        "status": "healthy",
        "backend": backend_health.get("success", False),
        "clients": app_state["connected_clients"]
    }

# WebSocket イベントハンドラー
@socketio.on('connect')
def handle_connect():
    """クライアント接続時の処理"""
    app_state["connected_clients"] += 1
    logger.info(f'Client connected. Total clients: {app_state["connected_clients"]}')
    
    # 接続時に初期状態を送信
    emit('connection_status', {'connected': True})
    
    # 監視が未開始の場合は開始
    if not app_state["monitoring"]:
        start_monitoring()

@socketio.on('disconnect')
def handle_disconnect():
    """クライアント切断時の処理"""
    app_state["connected_clients"] -= 1
    logger.info(f'Client disconnected. Total clients: {app_state["connected_clients"]}')
    
    # 全クライアントが切断されたら監視停止
    if app_state["connected_clients"] <= 0:
        stop_monitoring()

@socketio.on('request_status')
def handle_status_request():
    """クライアントからのステータス要求"""
    status_data = get_current_status()
    emit('status_update', status_data)

@socketio.on('drone_command')
def handle_drone_command(data):
    """ドローンコマンド実行"""
    command = data.get('command')
    params = data.get('params', {})
    
    logger.info(f'Executing drone command: {command} with params: {params}')
    
    try:
        if command == 'connect':
            result = api_client.connect_drone()
        elif command == 'disconnect':
            result = api_client.disconnect_drone()
        elif command == 'takeoff':
            result = api_client.takeoff()
        elif command == 'land':
            result = api_client.land()
        elif command == 'emergency':
            result = api_client.emergency_stop()
        elif command == 'hover':
            result = api_client.hover()
        elif command == 'move':
            result = api_client.move_drone(params.get('direction'), params.get('distance'))
        elif command == 'rotate':
            result = api_client.rotate_drone(params.get('direction'), params.get('angle'))
        else:
            result = {"success": False, "data": {"error": "Unknown command"}}
        
        emit('command_result', {
            'command': command,
            'result': result
        })
        
        # コマンド実行後、状態を更新
        if result.get('success'):
            status_data = get_current_status()
            emit('status_update', status_data, broadcast=True)
            
    except Exception as e:
        logger.error(f'Command execution error: {e}')
        emit('command_result', {
            'command': command,
            'result': {
                "success": False,
                "data": {"error": str(e)},
                "status_code": 500
            }
        })

def get_current_status():
    """現在のドローン状態を取得"""
    try:
        # ドローンの基本状態
        status = api_client.get_drone_status()
        sensors = api_client.get_sensors() if hasattr(api_client, 'get_sensors') else {}
        
        # センサー情報を個別取得
        battery = api_client.get_battery()
        height = api_client.get_height()
        temperature = api_client.get_temperature()
        
        return {
            "timestamp": time.time(),
            "drone_status": status.get("data", {}),
            "battery": battery.get("data", {}).get("battery", 0) if battery.get("success") else 0,
            "height": height.get("data", {}).get("height", 0) if height.get("success") else 0,
            "temperature": temperature.get("data", {}).get("temperature", 0) if temperature.get("success") else 0,
            "backend_connected": status.get("success", False)
        }
    except Exception as e:
        logger.error(f'Error getting status: {e}')
        return {
            "timestamp": time.time(),
            "drone_status": {},
            "battery": 0,
            "height": 0,
            "temperature": 0,
            "backend_connected": False,
            "error": str(e)
        }

def monitoring_loop():
    """リアルタイム監視ループ"""
    while app_state["monitoring"]:
        try:
            if app_state["connected_clients"] > 0:
                status_data = get_current_status()
                socketio.emit('status_update', status_data)
        except Exception as e:
            logger.error(f'Monitoring loop error: {e}')
        
        time.sleep(1)  # 1秒間隔で更新

def start_monitoring():
    """リアルタイム監視開始"""
    if not app_state["monitoring"]:
        app_state["monitoring"] = True
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        logger.info('Real-time monitoring started')

def stop_monitoring():
    """リアルタイム監視停止"""
    app_state["monitoring"] = False
    logger.info('Real-time monitoring stopped')

if __name__ == '__main__':
    logger.info('Starting MFG Drone Admin Frontend')
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)