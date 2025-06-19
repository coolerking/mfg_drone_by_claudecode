"""
バックエンドドローンAPI統合クライアント
"""

import requests
import json
import os
from typing import Dict, Any, List, Optional
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DroneAPIClient:
    """バックエンドドローンAPIとの通信クライアント"""
    
    def __init__(self, base_url: str = None):
        """
        Args:
            base_url: バックエンドAPIのベースURL
        """
        self.base_url = base_url or os.environ.get('BACKEND_API_URL', 'http://localhost:8000')
        self.timeout = 30  # タイムアウト設定
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        HTTPリクエストを実行
        
        Args:
            method: HTTPメソッド
            endpoint: APIエンドポイント 
            **kwargs: requests.requestに渡す追加引数
            
        Returns:
            APIレスポンス
            
        Raises:
            Exception: APIエラー
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
            
        except requests.exceptions.Timeout:
            logger.error(f"API timeout: {method} {url}")
            raise Exception(f"APIタイムアウト: {endpoint}")
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {method} {url}")
            raise Exception(f"バックエンドAPIに接続できません: {self.base_url}")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} {url}")
            try:
                error_data = e.response.json()
                raise Exception(error_data.get('detail', str(e)))
            except:
                raise Exception(f"HTTPエラー: {e.response.status_code}")
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"予期しないエラー: {str(e)}")
    
    # システム・ヘルスチェック
    def health_check(self) -> Dict[str, Any]:
        """システムヘルスチェック"""
        return self._make_request('GET', '/health')
    
    # ドローン接続管理
    def connect_drone(self) -> Dict[str, Any]:
        """ドローン接続"""
        return self._make_request('POST', '/drone/connect')
    
    def disconnect_drone(self) -> Dict[str, Any]:
        """ドローン切断"""
        return self._make_request('POST', '/drone/disconnect')
    
    def get_connection_status(self) -> Dict[str, Any]:
        """接続状態取得"""
        return self._make_request('GET', '/drone/status')
    
    # 基本飛行制御
    def takeoff(self) -> Dict[str, Any]:
        """離陸"""
        return self._make_request('POST', '/drone/takeoff')
    
    def land(self) -> Dict[str, Any]:
        """着陸"""
        return self._make_request('POST', '/drone/land')
    
    def emergency_stop(self) -> Dict[str, Any]:
        """緊急停止"""
        return self._make_request('POST', '/drone/emergency')
    
    # 移動制御
    def move_drone(self, direction: str, distance: int = 50) -> Dict[str, Any]:
        """
        ドローン移動
        
        Args:
            direction: 移動方向 (forward, backward, left, right, up, down)
            distance: 移動距離(cm)
        """
        data = {'distance': distance}
        return self._make_request('POST', f'/drone/move/{direction}', json=data)
    
    def rotate_drone(self, direction: str, angle: int = 90) -> Dict[str, Any]:
        """
        ドローン回転
        
        Args:
            direction: 回転方向 (clockwise, counter_clockwise)
            angle: 回転角度(度)
        """
        data = {'angle': angle}
        return self._make_request('POST', f'/drone/rotate/{direction}', json=data)
    
    # センサーデータ
    def get_battery_level(self) -> Dict[str, Any]:
        """バッテリー残量取得"""
        return self._make_request('GET', '/drone/battery')
    
    def get_altitude(self) -> Dict[str, Any]:
        """高度取得"""
        return self._make_request('GET', '/drone/altitude')
    
    def get_attitude(self) -> Dict[str, Any]:
        """姿勢取得"""
        return self._make_request('GET', '/drone/attitude')
    
    def get_speed(self) -> Dict[str, Any]:
        """速度取得"""
        return self._make_request('GET', '/drone/speed')
    
    def get_all_sensors(self) -> Dict[str, Any]:
        """全センサー情報取得"""
        return self._make_request('GET', '/drone/sensors')
    
    def get_drone_status(self) -> Dict[str, Any]:
        """ドローン状態取得"""
        return self._make_request('GET', '/drone/status')
    
    # カメラ制御
    def get_camera_stream_url(self) -> str:
        """カメラストリームURL取得"""
        return f"{self.base_url}/drone/camera/stream"
    
    def capture_photo(self) -> Dict[str, Any]:
        """写真撮影"""
        return self._make_request('POST', '/drone/camera/capture')
    
    def start_recording(self) -> Dict[str, Any]:
        """録画開始"""
        return self._make_request('POST', '/drone/camera/start_recording')
    
    def stop_recording(self) -> Dict[str, Any]:
        """録画停止"""
        return self._make_request('POST', '/drone/camera/stop_recording')
    
    # 物体追跡
    def start_tracking(self, target_object: str, tracking_mode: str = 'center') -> Dict[str, Any]:
        """
        物体追跡開始
        
        Args:
            target_object: 追跡対象オブジェクト名
            tracking_mode: 追跡モード (center, follow)
        """
        data = {
            'target_object': target_object,
            'tracking_mode': tracking_mode
        }
        return self._make_request('POST', '/tracking/start', json=data)
    
    def stop_tracking(self) -> Dict[str, Any]:
        """物体追跡停止"""
        return self._make_request('POST', '/tracking/stop')
    
    def get_tracking_status(self) -> Dict[str, Any]:
        """追跡状態取得"""
        return self._make_request('GET', '/tracking/status')
    
    # モデル管理
    def get_models(self) -> Dict[str, Any]:
        """モデル一覧取得"""
        return self._make_request('GET', '/models')
    
    def upload_training_images(self, object_name: str, image_paths: List[str]) -> Dict[str, Any]:
        """
        学習画像アップロード
        
        Args:
            object_name: オブジェクト名
            image_paths: 画像ファイルパスリスト
        """
        files = []
        try:
            for path in image_paths:
                with open(path, 'rb') as f:
                    files.append(('images', f))
            
            data = {'object_name': object_name}
            response = self.session.post(
                f"{self.base_url}/models/upload",
                data=data,
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Image upload error: {str(e)}")
            raise Exception(f"画像アップロードエラー: {str(e)}")
    
    def train_model(self, object_name: str) -> Dict[str, Any]:
        """
        モデル訓練開始
        
        Args:
            object_name: 訓練対象オブジェクト名
        """
        data = {'object_name': object_name}
        return self._make_request('POST', '/models/train', json=data)
    
    def get_training_status(self, object_name: str) -> Dict[str, Any]:
        """
        訓練状態取得
        
        Args:
            object_name: オブジェクト名
        """
        return self._make_request('GET', f'/models/train/{object_name}/status')
    
    # 設定管理
    def get_settings(self) -> Dict[str, Any]:
        """設定取得"""
        return self._make_request('GET', '/settings')
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        設定更新
        
        Args:
            settings: 設定データ
        """
        return self._make_request('POST', '/settings', json=settings)
    
    def update_wifi_settings(self, ssid: str, password: str) -> Dict[str, Any]:
        """
        WiFi設定更新
        
        Args:
            ssid: WiFi SSID
            password: WiFiパスワード
        """
        data = {'ssid': ssid, 'password': password}
        return self._make_request('POST', '/settings/wifi', json=data)
    
    def update_speed_settings(self, speed: int) -> Dict[str, Any]:
        """
        速度設定更新
        
        Args:
            speed: 速度設定値
        """
        data = {'speed': speed}
        return self._make_request('POST', '/settings/speed', json=data)