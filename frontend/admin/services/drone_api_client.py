"""
Drone API Client - バックエンドAPI統合クライアント
Raspberry Pi 5上のFastAPIバックエンドとの通信を管理
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DroneAPIClient:
    """ドローンバックエンドAPI統合クライアント"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Args:
            base_url: バックエンドAPIのベースURL
            timeout: リクエストタイムアウト（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        APIリクエストを実行
        
        Args:
            method: HTTPメソッド
            endpoint: APIエンドポイント
            **kwargs: requestsライブラリのパラメータ
            
        Returns:
            APIレスポンス辞書
            
        Raises:
            requests.RequestException: API通信エラー
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {method} {url} - {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise
    
    # ===== System Health =====
    def health_check(self) -> Dict[str, Any]:
        """システムヘルスチェック"""
        return self._make_request('GET', '/health')
    
    def get_current_timestamp(self) -> str:
        """現在時刻取得"""
        return datetime.now().isoformat()
    
    # ===== Connection Management =====
    def connect_drone(self) -> Dict[str, Any]:
        """ドローン接続"""
        return self._make_request('POST', '/drone/connect')
    
    def disconnect_drone(self) -> Dict[str, Any]:
        """ドローン切断"""
        return self._make_request('POST', '/drone/disconnect')
    
    def get_connection_status(self) -> Dict[str, Any]:
        """接続状態取得"""
        try:
            # バックエンドに接続状態確認エンドポイントがある場合
            return self._make_request('GET', '/drone/status')
        except:
            # フォールバック: ヘルスチェックで代用
            return {'connected': False, 'status': 'unknown'}
    
    # ===== Flight Control =====
    def takeoff(self) -> Dict[str, Any]:
        """離陸"""
        return self._make_request('POST', '/drone/takeoff')
    
    def land(self) -> Dict[str, Any]:
        """着陸"""
        return self._make_request('POST', '/drone/land')
    
    def emergency_stop(self) -> Dict[str, Any]:
        """緊急停止"""
        return self._make_request('POST', '/drone/emergency')
    
    # ===== Movement Control =====
    def move_drone(self, direction: str, distance: int) -> Dict[str, Any]:
        """
        ドローン移動
        
        Args:
            direction: 移動方向 ('forward', 'back', 'left', 'right', 'up', 'down')
            distance: 移動距離（cm）
        """
        return self._make_request('POST', f'/drone/move/{direction}', 
                                json={'distance': distance})
    
    def rotate_drone(self, direction: str, angle: int) -> Dict[str, Any]:
        """
        ドローン回転
        
        Args:
            direction: 回転方向 ('cw', 'ccw')
            angle: 回転角度（度）
        """
        return self._make_request('POST', f'/drone/rotate_{direction}', 
                                json={'angle': angle})
    
    # ===== Sensor Data =====
    def get_all_sensor_data(self) -> Dict[str, Any]:
        """全センサーデータ取得"""
        try:
            battery = self.get_battery_info()
            attitude = self.get_attitude_data()
            height = self.get_height()
            speed = self.get_speed()
            temperature = self.get_temperature()
            
            return {
                'battery': battery,
                'attitude': attitude,
                'height': height,
                'speed': speed,
                'temperature': temperature,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Sensor data collection error: {str(e)}")
            return {'error': str(e)}
    
    def get_battery_info(self) -> Dict[str, Any]:
        """バッテリー情報取得"""
        return self._make_request('GET', '/drone/battery')
    
    def get_attitude_data(self) -> Dict[str, Any]:
        """姿勢データ取得"""
        return self._make_request('GET', '/drone/attitude')
    
    def get_height(self) -> Dict[str, Any]:
        """高度取得"""
        return self._make_request('GET', '/drone/height')
    
    def get_speed(self) -> Dict[str, Any]:
        """速度取得"""
        return self._make_request('GET', '/drone/speed')
    
    def get_temperature(self) -> Dict[str, Any]:
        """温度取得"""
        return self._make_request('GET', '/drone/temperature')
    
    def get_sensor_summary(self) -> Dict[str, Any]:
        """センサーサマリー取得"""
        try:
            return {
                'battery_percentage': self.get_battery_info().get('battery_percentage', 0),
                'height': self.get_height().get('height', 0),
                'temperature': self.get_temperature().get('temperature', 0)
            }
        except:
            return {'battery_percentage': 0, 'height': 0, 'temperature': 0}
    
    def get_live_metrics(self) -> Dict[str, Any]:
        """ライブメトリクス取得"""
        return self.get_all_sensor_data()
    
    # ===== Camera Control =====
    def start_camera_stream(self) -> Dict[str, Any]:
        """カメラストリーミング開始"""
        return self._make_request('POST', '/drone/streamon')
    
    def stop_camera_stream(self) -> Dict[str, Any]:
        """カメラストリーミング停止"""
        return self._make_request('POST', '/drone/streamoff')
    
    def take_photo(self) -> Dict[str, Any]:
        """写真撮影"""
        return self._make_request('POST', '/camera/capture')
    
    def start_video_recording(self) -> Dict[str, Any]:
        """動画録画開始"""
        return self._make_request('POST', '/camera/record/start')
    
    def stop_video_recording(self) -> Dict[str, Any]:
        """動画録画停止"""
        return self._make_request('POST', '/camera/record/stop')
    
    # ===== Object Tracking =====
    def start_tracking(self, target_object: str, tracking_mode: str = 'center') -> Dict[str, Any]:
        """
        物体追跡開始
        
        Args:
            target_object: 追跡対象オブジェクト名
            tracking_mode: 追跡モード ('center', 'follow')
        """
        return self._make_request('POST', '/tracking/start', json={
            'target_object': target_object,
            'tracking_mode': tracking_mode
        })
    
    def stop_tracking(self) -> Dict[str, Any]:
        """物体追跡停止"""
        return self._make_request('POST', '/tracking/stop')
    
    def get_tracking_status(self) -> Dict[str, Any]:
        """追跡状態取得"""
        return self._make_request('GET', '/tracking/status')
    
    # ===== Model Management =====
    def list_models(self) -> Dict[str, Any]:
        """利用可能モデル一覧"""
        return self._make_request('GET', '/models')
    
    def upload_training_images(self, file_paths: List[str], object_name: str) -> Dict[str, Any]:
        """
        学習用画像アップロード
        
        Args:
            file_paths: 画像ファイルパスリスト
            object_name: オブジェクト名
        """
        # 実際の実装では、multipart/form-dataでファイルをアップロード
        return self._make_request('POST', '/models/upload', json={
            'object_name': object_name,
            'file_count': len(file_paths)
        })
    
    def start_training(self, object_name: str, training_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        モデル学習開始
        
        Args:
            object_name: オブジェクト名
            training_params: 学習パラメータ
        """
        data = {'object_name': object_name}
        if training_params:
            data.update(training_params)
        
        return self._make_request('POST', '/models/train', json=data)
    
    def get_training_status(self, training_id: str) -> Dict[str, Any]:
        """
        学習進捗取得
        
        Args:
            training_id: 学習ID
        """
        return self._make_request('GET', f'/models/training/{training_id}/status')
    
    # ===== Settings Management =====
    def get_drone_settings(self) -> Dict[str, Any]:
        """ドローン設定取得"""
        return self._make_request('GET', '/settings')
    
    def update_drone_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        ドローン設定更新
        
        Args:
            settings: 設定辞書
        """
        return self._make_request('PUT', '/settings', json=settings)
    
    def set_speed(self, speed: int) -> Dict[str, Any]:
        """
        速度設定
        
        Args:
            speed: 速度値（10-100）
        """
        return self._make_request('POST', '/drone/speed', json={'speed': speed})
    
    def set_wifi_credentials(self, ssid: str, password: str) -> Dict[str, Any]:
        """
        WiFi設定
        
        Args:
            ssid: WiFi SSID
            password: WiFiパスワード
        """
        return self._make_request('POST', '/settings/wifi', json={
            'ssid': ssid,
            'password': password
        })