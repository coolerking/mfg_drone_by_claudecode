"""
MFG Drone Admin Frontend
管理者用フロントエンド - 物体学習、ドローン制御、追跡開始/停止
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os

# Blueprints
from blueprints.model import model_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# ファイルアップロード設定
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB制限
app.config['UPLOAD_FOLDER'] = 'uploads'

# Flask-SocketIO設定
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Blueprint登録
app.register_blueprint(model_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return {"status": "healthy", "features": ["model_training", "file_upload", "websocket"]}

# WebSocketイベントハンドラ
@socketio.on('connect')
def handle_connect():
    """クライアント接続時"""
    emit('status', {'message': '管理者フロントエンドに接続しました'})

@socketio.on('disconnect')
def handle_disconnect():
    """クライアント切断時"""
    print('クライアントが切断されました')

@socketio.on('training_status_request')
def handle_training_status_request(data):
    """訓練ステータス要求"""
    task_id = data.get('task_id')
    # 実装予定: バックエンドから訓練ステータスを取得
    emit('training_status', {
        'task_id': task_id,
        'status': 'in_progress',
        'progress': 50,
        'message': '訓練中...'
    })

if __name__ == '__main__':
    # アップロードディレクトリ作成
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Flask-SocketIOで起動
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)