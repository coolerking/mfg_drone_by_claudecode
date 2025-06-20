"""
MFG Drone Admin Frontend - Phase 5 完全版
管理者用フロントエンド - 高度制御・ミッションパッド対応・システム設定
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import requests
import json
from typing import Dict, Any, Optional

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mfg-drone-admin-secret-key')

# バックエンドAPI設定
BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://localhost:8000')

class DroneAPIClient:
    """バックエンドAPIとの通信を管理するクライアント"""
    
    def __init__(self, base_url: str = BACKEND_API_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """APIリクエストを送信"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                app.logger.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Request Exception: {e}")
            return None
    
    # ヘルスチェック
    def health_check(self):
        return self._make_request('GET', '/health')
    
    # ドローン接続管理
    def connect_drone(self):
        return self._make_request('POST', '/drone/connect')
    
    def disconnect_drone(self):
        return self._make_request('POST', '/drone/disconnect')
    
    # 基本飛行制御
    def takeoff(self):
        return self._make_request('POST', '/drone/takeoff')
    
    def land(self):
        return self._make_request('POST', '/drone/land')
    
    def emergency_stop(self):
        return self._make_request('POST', '/drone/emergency')
    
    # 基本移動制御
    def move_forward(self, distance: int):
        return self._make_request('POST', '/drone/move/forward', {'distance': distance})
    
    def move_backward(self, distance: int):
        return self._make_request('POST', '/drone/move/back', {'distance': distance})
    
    def move_left(self, distance: int):
        return self._make_request('POST', '/drone/move/left', {'distance': distance})
    
    def move_right(self, distance: int):
        return self._make_request('POST', '/drone/move/right', {'distance': distance})
    
    def move_up(self, distance: int):
        return self._make_request('POST', '/drone/move/up', {'distance': distance})
    
    def move_down(self, distance: int):
        return self._make_request('POST', '/drone/move/down', {'distance': distance})
    
    def rotate(self, direction: str, angle: int):
        return self._make_request('POST', '/drone/rotate', {'direction': direction, 'angle': angle})
    
    def flip(self, direction: str):
        return self._make_request('POST', '/drone/flip', {'direction': direction})
    
    # 高度移動制御（Phase 5）
    def go_xyz(self, x: int, y: int, z: int, speed: int):
        return self._make_request('POST', '/drone/go_xyz', {
            'x': x, 'y': y, 'z': z, 'speed': speed
        })
    
    def curve_xyz(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int):
        return self._make_request('POST', '/drone/curve_xyz', {
            'x1': x1, 'y1': y1, 'z1': z1,
            'x2': x2, 'y2': y2, 'z2': z2,
            'speed': speed
        })
    
    def rc_control(self, left_right: int, forward_backward: int, up_down: int, yaw: int):
        return self._make_request('POST', '/drone/rc_control', {
            'left_right_velocity': left_right,
            'forward_backward_velocity': forward_backward,
            'up_down_velocity': up_down,
            'yaw_velocity': yaw
        })
    
    # カメラ操作
    def start_video_stream(self):
        return self._make_request('POST', '/camera/stream/start')
    
    def stop_video_stream(self):
        return self._make_request('POST', '/camera/stream/stop')
    
    def take_photo(self):
        return self._make_request('POST', '/camera/photo')
    
    def start_recording(self):
        return self._make_request('POST', '/camera/recording/start')
    
    def stop_recording(self):
        return self._make_request('POST', '/camera/recording/stop')
    
    # センサーデータ
    def get_battery(self):
        return self._make_request('GET', '/drone/battery')
    
    def get_altitude(self):
        return self._make_request('GET', '/drone/altitude')
    
    def get_temperature(self):
        return self._make_request('GET', '/drone/temperature')
    
    def get_attitude(self):
        return self._make_request('GET', '/drone/attitude')
    
    def get_velocity(self):
        return self._make_request('GET', '/drone/velocity')
    
    # WiFi・設定
    def set_wifi(self, ssid: str, password: str):
        return self._make_request('PUT', '/drone/wifi', {'ssid': ssid, 'password': password})
    
    def set_speed(self, speed: float):
        return self._make_request('PUT', '/drone/speed', {'speed': speed})
    
    def send_command(self, command: str, timeout: int = 7):
        return self._make_request('POST', '/drone/command', {
            'command': command,
            'timeout': timeout,
            'expect_response': True
        })
    
    # ミッションパッド（Phase 5）
    def enable_mission_pad(self):
        return self._make_request('POST', '/mission_pad/enable')
    
    def disable_mission_pad(self):
        return self._make_request('POST', '/mission_pad/disable')
    
    def set_detection_direction(self, direction: int):
        return self._make_request('PUT', '/mission_pad/detection_direction', {'direction': direction})
    
    def go_to_mission_pad(self, x: int, y: int, z: int, speed: int, pad_id: int):
        return self._make_request('POST', '/mission_pad/go_xyz', {
            'x': x, 'y': y, 'z': z, 'speed': speed, 'mission_pad_id': pad_id
        })
    
    def get_mission_pad_status(self):
        return self._make_request('GET', '/mission_pad/status')
    
    # 物体追跡
    def start_tracking(self, target_object: str, tracking_mode: str = 'center'):
        return self._make_request('POST', '/tracking/start', {
            'target_object': target_object,
            'tracking_mode': tracking_mode
        })
    
    def stop_tracking(self):
        return self._make_request('POST', '/tracking/stop')
    
    def get_tracking_status(self):
        return self._make_request('GET', '/tracking/status')
    
    # モデル管理
    def get_model_list(self):
        return self._make_request('GET', '/model/list')
    
    def delete_model(self, model_name: str):
        return self._make_request('DELETE', f'/model/{model_name}')

# APIクライアントインスタンス
api_client = DroneAPIClient()

@app.route('/')
def index():
    """メインページ表示"""
    return render_template('admin.html')

@app.route('/health')
def health_check():
    """フロントエンドヘルスチェック"""
    backend_status = api_client.health_check()
    return jsonify({
        'status': 'healthy',
        'frontend': 'MFG Drone Admin v1.0.0 (Phase 5)',
        'backend': backend_status['status'] if backend_status else 'unavailable'
    })

# ========================================
# ドローン制御API プロキシ
# ========================================

@app.route('/api/drone/connect', methods=['POST'])
def connect_drone():
    result = api_client.connect_drone()
    return jsonify(result) if result else jsonify({'error': 'Connection failed'}), 500

@app.route('/api/drone/disconnect', methods=['POST'])
def disconnect_drone():
    result = api_client.disconnect_drone()
    return jsonify(result) if result else jsonify({'error': 'Disconnection failed'}), 500

@app.route('/api/drone/takeoff', methods=['POST'])
def takeoff():
    result = api_client.takeoff()
    return jsonify(result) if result else jsonify({'error': 'Takeoff failed'}), 500

@app.route('/api/drone/land', methods=['POST'])
def land():
    result = api_client.land()
    return jsonify(result) if result else jsonify({'error': 'Landing failed'}), 500

@app.route('/api/drone/emergency', methods=['POST'])
def emergency_stop():
    result = api_client.emergency_stop()
    return jsonify(result) if result else jsonify({'error': 'Emergency stop failed'}), 500

# 基本移動制御
@app.route('/api/drone/move/<direction>', methods=['POST'])
def move_drone(direction):
    data = request.get_json()
    distance = data.get('distance', 30)
    
    if direction == 'forward':
        result = api_client.move_forward(distance)
    elif direction == 'backward':
        result = api_client.move_backward(distance)
    elif direction == 'left':
        result = api_client.move_left(distance)
    elif direction == 'right':
        result = api_client.move_right(distance)
    elif direction == 'up':
        result = api_client.move_up(distance)
    elif direction == 'down':
        result = api_client.move_down(distance)
    else:
        return jsonify({'error': 'Invalid direction'}), 400
    
    return jsonify(result) if result else jsonify({'error': f'{direction} movement failed'}), 500

@app.route('/api/drone/rotate', methods=['POST'])
def rotate_drone():
    data = request.get_json()
    direction = data.get('direction')
    angle = data.get('angle', 90)
    
    result = api_client.rotate(direction, angle)
    return jsonify(result) if result else jsonify({'error': 'Rotation failed'}), 500

# 高度移動制御（Phase 5）
@app.route('/api/drone/go_xyz', methods=['POST'])
def go_xyz():
    data = request.get_json()
    x = data.get('x', 0)
    y = data.get('y', 0)
    z = data.get('z', 0)
    speed = data.get('speed', 50)
    
    result = api_client.go_xyz(x, y, z, speed)
    return jsonify(result) if result else jsonify({'error': 'XYZ movement failed'}), 500

@app.route('/api/drone/curve_xyz', methods=['POST'])
def curve_xyz():
    data = request.get_json()
    x1, y1, z1 = data.get('x1', 0), data.get('y1', 0), data.get('z1', 0)
    x2, y2, z2 = data.get('x2', 0), data.get('y2', 0), data.get('z2', 0)
    speed = data.get('speed', 30)
    
    result = api_client.curve_xyz(x1, y1, z1, x2, y2, z2, speed)
    return jsonify(result) if result else jsonify({'error': 'Curve flight failed'}), 500

@app.route('/api/drone/rc_control', methods=['POST'])
def rc_control():
    data = request.get_json()
    left_right = data.get('left_right_velocity', 0)
    forward_backward = data.get('forward_backward_velocity', 0)
    up_down = data.get('up_down_velocity', 0)
    yaw = data.get('yaw_velocity', 0)
    
    result = api_client.rc_control(left_right, forward_backward, up_down, yaw)
    return jsonify(result) if result else jsonify({'error': 'RC control failed'}), 500

# ========================================
# センサーデータAPI
# ========================================

@app.route('/api/sensors/all', methods=['GET'])
def get_all_sensors():
    """全センサーデータを一括取得"""
    battery = api_client.get_battery()
    altitude = api_client.get_altitude()
    temperature = api_client.get_temperature()
    attitude = api_client.get_attitude()
    velocity = api_client.get_velocity()
    
    return jsonify({
        'battery': battery,
        'altitude': altitude,
        'temperature': temperature,
        'attitude': attitude,
        'velocity': velocity
    })

@app.route('/api/drone/battery', methods=['GET'])
def get_battery():
    result = api_client.get_battery()
    return jsonify(result) if result else jsonify({'error': 'Battery data unavailable'}), 503

@app.route('/api/drone/altitude', methods=['GET'])
def get_altitude():
    result = api_client.get_altitude()
    return jsonify(result) if result else jsonify({'error': 'Altitude data unavailable'}), 503

@app.route('/api/drone/temperature', methods=['GET'])
def get_temperature():
    result = api_client.get_temperature()
    return jsonify(result) if result else jsonify({'error': 'Temperature data unavailable'}), 503

@app.route('/api/drone/attitude', methods=['GET'])
def get_attitude():
    result = api_client.get_attitude()
    return jsonify(result) if result else jsonify({'error': 'Attitude data unavailable'}), 503

# ========================================
# カメラ制御API
# ========================================

@app.route('/api/camera/stream/start', methods=['POST'])
def start_video_stream():
    result = api_client.start_video_stream()
    return jsonify(result) if result else jsonify({'error': 'Stream start failed'}), 500

@app.route('/api/camera/stream/stop', methods=['POST'])
def stop_video_stream():
    result = api_client.stop_video_stream()
    return jsonify(result) if result else jsonify({'error': 'Stream stop failed'}), 500

@app.route('/api/camera/photo', methods=['POST'])
def take_photo():
    result = api_client.take_photo()
    return jsonify(result) if result else jsonify({'error': 'Photo capture failed'}), 500

@app.route('/api/camera/recording/start', methods=['POST'])
def start_recording():
    result = api_client.start_recording()
    return jsonify(result) if result else jsonify({'error': 'Recording start failed'}), 500

@app.route('/api/camera/recording/stop', methods=['POST'])
def stop_recording():
    result = api_client.stop_recording()
    return jsonify(result) if result else jsonify({'error': 'Recording stop failed'}), 500

# ビデオストリーミングプロキシ
@app.route('/api/camera/stream')
def video_stream():
    """ビデオストリーミングをプロキシ"""
    try:
        response = requests.get(f'{BACKEND_API_URL}/camera/stream', stream=True)
        return app.response_class(
            response.iter_content(chunk_size=1024),
            mimetype=response.headers.get('content-type')
        )
    except Exception as e:
        app.logger.error(f"Video stream error: {e}")
        return jsonify({'error': 'Video stream unavailable'}), 503

# ========================================
# ミッションパッドAPI（Phase 5）
# ========================================

@app.route('/api/mission_pad/enable', methods=['POST'])
def enable_mission_pad():
    result = api_client.enable_mission_pad()
    return jsonify(result) if result else jsonify({'error': 'Mission pad enable failed'}), 500

@app.route('/api/mission_pad/disable', methods=['POST'])
def disable_mission_pad():
    result = api_client.disable_mission_pad()
    return jsonify(result) if result else jsonify({'error': 'Mission pad disable failed'}), 500

@app.route('/api/mission_pad/detection_direction', methods=['PUT'])
def set_detection_direction():
    data = request.get_json()
    direction = data.get('direction', 0)
    
    result = api_client.set_detection_direction(direction)
    return jsonify(result) if result else jsonify({'error': 'Detection direction setting failed'}), 500

@app.route('/api/mission_pad/go_xyz', methods=['POST'])
def go_to_mission_pad():
    data = request.get_json()
    x = data.get('x', 0)
    y = data.get('y', 0)
    z = data.get('z', 0)
    speed = data.get('speed', 50)
    pad_id = data.get('mission_pad_id', 1)
    
    result = api_client.go_to_mission_pad(x, y, z, speed, pad_id)
    return jsonify(result) if result else jsonify({'error': 'Mission pad movement failed'}), 500

@app.route('/api/mission_pad/status', methods=['GET'])
def get_mission_pad_status():
    result = api_client.get_mission_pad_status()
    return jsonify(result) if result else jsonify({'error': 'Mission pad status unavailable'}), 503

# ========================================
# 物体追跡API
# ========================================

@app.route('/api/tracking/start', methods=['POST'])
def start_tracking():
    data = request.get_json()
    target_object = data.get('target_object')
    tracking_mode = data.get('tracking_mode', 'center')
    
    if not target_object:
        return jsonify({'error': 'Target object not specified'}), 400
    
    result = api_client.start_tracking(target_object, tracking_mode)
    return jsonify(result) if result else jsonify({'error': 'Tracking start failed'}), 500

@app.route('/api/tracking/stop', methods=['POST'])
def stop_tracking():
    result = api_client.stop_tracking()
    return jsonify(result) if result else jsonify({'error': 'Tracking stop failed'}), 500

@app.route('/api/tracking/status', methods=['GET'])
def get_tracking_status():
    result = api_client.get_tracking_status()
    return jsonify(result) if result else jsonify({'error': 'Tracking status unavailable'}), 503

# ========================================
# モデル管理API
# ========================================

@app.route('/api/model/train', methods=['POST'])
def train_model():
    """モデル訓練（ファイルアップロード）"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    object_name = request.form.get('object_name')
    
    if not object_name:
        return jsonify({'error': 'Object name required'}), 400
    
    # バックエンドにファイルを転送
    try:
        files = {'file': (file.filename, file.stream, file.content_type)}
        data = {'object_name': object_name}
        
        response = requests.post(
            f'{BACKEND_API_URL}/model/train',
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Model training failed'}), response.status_code
    
    except Exception as e:
        app.logger.error(f"Model upload error: {e}")
        return jsonify({'error': 'File upload failed'}), 500

@app.route('/api/model/list', methods=['GET'])
def get_model_list():
    result = api_client.get_model_list()
    return jsonify(result) if result else jsonify({'error': 'Model list unavailable'}), 503

@app.route('/api/model/<model_name>', methods=['DELETE'])
def delete_model(model_name):
    result = api_client.delete_model(model_name)
    return jsonify(result) if result else jsonify({'error': 'Model deletion failed'}), 500

# ========================================
# 設定管理API（Phase 5）
# ========================================

@app.route('/api/settings/wifi', methods=['PUT'])
def set_wifi_settings():
    data = request.get_json()
    ssid = data.get('ssid')
    password = data.get('password')
    
    if not ssid or not password:
        return jsonify({'error': 'SSID and password required'}), 400
    
    result = api_client.set_wifi(ssid, password)
    return jsonify(result) if result else jsonify({'error': 'WiFi setting failed'}), 500

@app.route('/api/settings/speed', methods=['PUT'])
def set_flight_speed():
    data = request.get_json()
    speed = data.get('speed')
    
    if not speed or not (1.0 <= speed <= 15.0):
        return jsonify({'error': 'Invalid speed value (1.0-15.0 m/s)'}), 400
    
    result = api_client.set_speed(speed)
    return jsonify(result) if result else jsonify({'error': 'Speed setting failed'}), 500

@app.route('/api/settings/command', methods=['POST'])
def send_custom_command():
    data = request.get_json()
    command = data.get('command')
    timeout = data.get('timeout', 7)
    
    if not command:
        return jsonify({'error': 'Command required'}), 400
    
    result = api_client.send_command(command, timeout)
    return jsonify(result) if result else jsonify({'error': 'Command execution failed'}), 500

# ========================================
# エラーハンドラ
# ========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({'error': 'Backend service unavailable'}), 503

# ========================================
# 開発用設定
# ========================================

if __name__ == '__main__':
    # 開発モード設定
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    
    print("="*60)
    print("🚁 MFG Drone Admin Frontend - Phase 5 完全版")
    print("="*60)
    print(f"📍 URL: http://{host}:{port}")
    print(f"🔗 Backend API: {BACKEND_API_URL}")
    print(f"🛠️  Debug Mode: {debug_mode}")
    print(f"📦 Features:")
    print(f"   ✅ ダッシュボード・ドローン制御")
    print(f"   ✅ 高度制御機能（3D座標・曲線飛行・リアルタイム制御）")
    print(f"   ✅ ミッションパッド対応")
    print(f"   ✅ AI物体追跡・モデル管理")
    print(f"   ✅ カメラ・映像制御")
    print(f"   ✅ システム設定・WiFi管理")
    print(f"   ✅ センサー監視・リアルタイム更新")
    print("="*60)
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )