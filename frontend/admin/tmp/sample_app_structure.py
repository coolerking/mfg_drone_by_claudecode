# サンプル実装: メインアプリケーション構造

"""
管理用フロントエンドサーバ サンプル実装
このファイルは実装計画の具体例を示すためのサンプルコードです。
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import asyncio
import aiohttp
import os
from typing import Dict, Any, Optional

# サンプル設定クラス
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = True
    BACKEND_API_URL = 'http://192.168.1.100:8000'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

# Flask アプリケーション初期化
app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# グローバル状態管理
app_state = {
    'drone_connected': False,
    'drone_flying': False,
    'tracking_active': False,
    'monitoring_active': False
}

# =====================================
# API クライアントクラス（サンプル）
# =====================================

class DroneAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """共通リクエスト処理"""
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.request(method, url, **kwargs) as response:
                    if response.status >= 400:
                        error_data = await response.json()
                        raise Exception(f"API Error: {error_data.get('error', 'Unknown error')}")
                    return await response.json()
            except aiohttp.ClientError as e:
                raise Exception(f"Network error: {str(e)}")
    
    # ドローン制御メソッド
    async def connect_drone(self):
        return await self._request('POST', '/drone/connect')
    
    async def disconnect_drone(self):
        return await self._request('POST', '/drone/disconnect')
    
    async def takeoff(self):
        return await self._request('POST', '/drone/takeoff')
    
    async def land(self):
        return await self._request('POST', '/drone/land')
    
    async def emergency_stop(self):
        return await self._request('POST', '/drone/emergency')
    
    async def move_drone(self, direction: str, distance: int):
        data = {"direction": direction, "distance": distance}
        return await self._request('POST', '/drone/move', json=data)
    
    async def rotate_drone(self, direction: str, angle: int):
        data = {"direction": direction, "angle": angle}
        return await self._request('POST', '/drone/rotate', json=data)
    
    # センサー情報取得
    async def get_drone_status(self):
        return await self._request('GET', '/drone/status')
    
    async def get_battery_level(self):
        return await self._request('GET', '/drone/battery')
    
    # 追跡制御
    async def start_tracking(self, target_object: str, tracking_mode: str = "center"):
        data = {"target_object": target_object, "tracking_mode": tracking_mode}
        return await self._request('POST', '/tracking/start', json=data)
    
    async def stop_tracking(self):
        return await self._request('POST', '/tracking/stop')
    
    async def get_tracking_status(self):
        return await self._request('GET', '/tracking/status')
    
    # モデル管理
    async def list_models(self):
        return await self._request('GET', '/model/list')

# APIクライアントインスタンス
api_client = DroneAPIClient(Config.BACKEND_API_URL)

# =====================================
# ルート定義
# =====================================

@app.route('/')
def dashboard():
    """ダッシュボード画面"""
    return render_template('dashboard.html', app_state=app_state)

@app.route('/drone-control')
def drone_control():
    """ドローン制御画面"""
    return render_template('drone_control.html', app_state=app_state)

@app.route('/model-training')
def model_training():
    """モデル訓練画面"""
    return render_template('model_training.html')

@app.route('/tracking')
def tracking():
    """追跡制御画面"""
    return render_template('tracking.html', app_state=app_state)

@app.route('/settings')
def settings():
    """設定画面"""
    return render_template('settings.html')

# =====================================
# API エンドポイント
# =====================================

@app.route('/api/drone/connect', methods=['POST'])
def api_connect_drone():
    """ドローン接続API"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.connect_drone())
        
        if result.get('success'):
            app_state['drone_connected'] = True
            # WebSocketでクライアントに通知
            socketio.emit('drone_connected', {'connected': True})
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/drone/disconnect', methods=['POST'])
def api_disconnect_drone():
    """ドローン切断API"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.disconnect_drone())
        
        if result.get('success'):
            app_state['drone_connected'] = False
            app_state['drone_flying'] = False
            app_state['tracking_active'] = False
            # WebSocketでクライアントに通知
            socketio.emit('drone_disconnected', {'connected': False})
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/drone/takeoff', methods=['POST'])
def api_takeoff():
    """離陸API"""
    if not app_state['drone_connected']:
        return jsonify({'success': False, 'message': 'ドローンが接続されていません'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.takeoff())
        
        if result.get('success'):
            app_state['drone_flying'] = True
            socketio.emit('drone_flying', {'flying': True})
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/drone/land', methods=['POST'])
def api_land():
    """着陸API"""
    if not app_state['drone_flying']:
        return jsonify({'success': False, 'message': 'ドローンが飛行していません'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.land())
        
        if result.get('success'):
            app_state['drone_flying'] = False
            socketio.emit('drone_flying', {'flying': False})
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/drone/emergency', methods=['POST'])
def api_emergency():
    """緊急停止API"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.emergency_stop())
        
        if result.get('success'):
            app_state['drone_flying'] = False
            app_state['tracking_active'] = False
            socketio.emit('emergency_stop', {'flying': False, 'tracking': False})
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/drone/move', methods=['POST'])
def api_move():
    """移動API"""
    if not app_state['drone_flying']:
        return jsonify({'success': False, 'message': 'ドローンが飛行していません'}), 400
    
    data = request.get_json()
    direction = data.get('direction')
    distance = data.get('distance', 50)
    
    # バリデーション
    valid_directions = ['up', 'down', 'left', 'right', 'forward', 'back']
    if direction not in valid_directions:
        return jsonify({'success': False, 'message': '無効な方向です'}), 400
    
    if not (20 <= distance <= 500):
        return jsonify({'success': False, 'message': '距離は20-500cmの範囲で指定してください'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.move_drone(direction, distance))
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/drone/rotate', methods=['POST'])
def api_rotate():
    """回転API"""
    if not app_state['drone_flying']:
        return jsonify({'success': False, 'message': 'ドローンが飛行していません'}), 400
    
    data = request.get_json()
    direction = data.get('direction')
    angle = data.get('angle', 90)
    
    # バリデーション
    valid_directions = ['clockwise', 'counter_clockwise']
    if direction not in valid_directions:
        return jsonify({'success': False, 'message': '無効な回転方向です'}), 400
    
    if not (1 <= angle <= 360):
        return jsonify({'success': False, 'message': '角度は1-360度の範囲で指定してください'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.rotate_drone(direction, angle))
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/tracking/start', methods=['POST'])
def api_start_tracking():
    """追跡開始API"""
    data = request.get_json()
    target_object = data.get('target_object')
    tracking_mode = data.get('tracking_mode', 'center')
    
    if not target_object:
        return jsonify({'success': False, 'message': '対象オブジェクト名が必要です'}), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.start_tracking(target_object, tracking_mode))
        
        if result.get('success'):
            app_state['tracking_active'] = True
            socketio.emit('tracking_started', {
                'tracking': True, 
                'target': target_object, 
                'mode': tracking_mode
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/tracking/stop', methods=['POST'])
def api_stop_tracking():
    """追跡停止API"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.stop_tracking())
        
        if result.get('success'):
            app_state['tracking_active'] = False
            socketio.emit('tracking_stopped', {'tracking': False})
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/models/list', methods=['GET'])
def api_list_models():
    """モデル一覧取得API"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(api_client.list_models())
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/api/model/train', methods=['POST'])
def api_train_model():
    """モデル訓練API"""
    object_name = request.form.get('object_name')
    files = request.files.getlist('images')
    
    if not object_name:
        return jsonify({'success': False, 'message': 'オブジェクト名が必要です'}), 400
    
    if not files:
        return jsonify({'success': False, 'message': '画像ファイルが必要です'}), 400
    
    # ファイル検証
    for file in files:
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            return jsonify({'success': False, 'message': '対応していないファイル形式です'}), 400
    
    try:
        # ここでバックエンドAPIに画像を送信する処理を実装
        # 実際の実装では multipart/form-data でファイルを送信
        return jsonify({
            'success': True, 
            'message': f'モデル訓練を開始しました: {object_name}',
            'task_id': 'dummy_task_id'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# =====================================
# WebSocket イベント
# =====================================

@socketio.on('connect')
def handle_connect():
    """クライアント接続時"""
    print('Client connected')
    emit('status', {
        'connected': app_state['drone_connected'],
        'flying': app_state['drone_flying'],
        'tracking': app_state['tracking_active']
    })

@socketio.on('disconnect')
def handle_disconnect():
    """クライアント切断時"""
    print('Client disconnected')

@socketio.on('start_monitoring')
def handle_start_monitoring():
    """監視開始"""
    app_state['monitoring_active'] = True
    # バックグラウンドタスクで定期的にセンサーデータを送信
    socketio.start_background_task(sensor_monitoring_task)

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """監視停止"""
    app_state['monitoring_active'] = False

def sensor_monitoring_task():
    """センサーデータ監視タスク（バックグラウンド）"""
    import time
    
    while app_state['monitoring_active']:
        try:
            if app_state['drone_connected']:
                # 非同期でセンサーデータを取得
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # バッテリー情報取得
                battery_data = loop.run_until_complete(api_client.get_battery_level())
                socketio.emit('battery_update', battery_data)
                
                # ドローン状態取得
                status_data = loop.run_until_complete(api_client.get_drone_status())
                socketio.emit('status_update', status_data)
                
                # 追跡状態取得
                if app_state['tracking_active']:
                    tracking_data = loop.run_until_complete(api_client.get_tracking_status())
                    socketio.emit('tracking_update', tracking_data)
                
                loop.close()
                
        except Exception as e:
            socketio.emit('error', {'message': f'監視エラー: {str(e)}'})
        
        time.sleep(1)  # 1秒間隔

# =====================================
# メイン実行部
# =====================================

if __name__ == '__main__':
    # 本番環境では gunicorn 等を使用
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)

"""
実装メモ:

1. このサンプルコードは管理用フロントエンドの基本構造を示している
2. 実際の実装では以下の点を追加考慮する必要がある:
   - 適切なエラーハンドリング
   - セキュリティ対策（CSRF、認証等）
   - ログ管理
   - 設定の外部化
   - テストコードの作成
   - パフォーマンス最適化

3. ファイル構成:
   - このコードは単一ファイルだが、実際はBlueprint等で分割する
   - templates/, static/ ディレクトリに HTML, CSS, JS ファイルを配置
   - services/, utils/ ディレクトリに機能別モジュールを配置

4. 追加実装項目:
   - カメラストリーミング表示
   - ファイルアップロード処理の詳細
   - リアルタイム通信の最適化
   - モバイル対応のレスポンシブUI
"""