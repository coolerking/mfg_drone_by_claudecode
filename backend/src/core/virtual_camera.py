"""
Phase 2: 動的カメラストリーム生成モジュール
Tello EDU ダミーシステム用の仮想カメラストリーム実装
"""

import cv2
import numpy as np
import threading
import time
import logging
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovementPattern(Enum):
    """移動パターンの列挙型"""
    STATIC = "static"              # 静止
    LINEAR = "linear"              # 直線移動
    CIRCULAR = "circular"          # 円形移動
    SINE_WAVE = "sine_wave"        # 正弦波移動
    RANDOM_WALK = "random_walk"    # ランダムウォーク

class TrackingObjectType(Enum):
    """追跡対象オブジェクトの種類"""
    PERSON = "person"              # 人物
    VEHICLE = "vehicle"            # 車両
    BALL = "ball"                  # ボール
    BOX = "box"                    # 箱
    ANIMAL = "animal"              # 動物

@dataclass
class TrackingObject:
    """追跡対象オブジェクトのデータクラス"""
    obj_type: TrackingObjectType
    position: Tuple[float, float]  # (x, y) 位置
    size: Tuple[int, int]          # (width, height) サイズ
    color: Tuple[int, int, int]    # BGR色
    movement_pattern: MovementPattern
    velocity: float = 0.0          # 移動速度
    angle: float = 0.0             # 移動角度（度）
    amplitude: float = 50.0        # 振幅（sine_wave用）
    frequency: float = 0.1         # 周波数（sine_wave用）
    center_pos: Optional[Tuple[float, float]] = None  # 中心位置（circular用）
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.center_pos is None:
            self.center_pos = self.position

class VirtualCameraStream:
    """仮想カメラストリームクラス"""
    
    def __init__(self, width: int = 640, height: int = 480, fps: int = 30):
        """
        初期化
        
        Args:
            width: 画像幅
            height: 画像高さ
            fps: フレームレート
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_interval = 1.0 / fps
        
        # 追跡対象オブジェクトのリスト
        self.tracking_objects: List[TrackingObject] = []
        
        # ストリーム制御
        self.is_streaming = False
        self.stream_thread: Optional[threading.Thread] = None
        self.current_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()
        
        # 統計情報
        self.frame_count = 0
        self.start_time = time.time()
        
        logger.info(f"仮想カメラストリーム初期化: {width}x{height}@{fps}fps")
    
    def add_tracking_object(self, obj: TrackingObject) -> None:
        """追跡対象オブジェクトを追加"""
        self.tracking_objects.append(obj)
        logger.info(f"追跡対象追加: {obj.obj_type.value} at {obj.position}")
    
    def remove_tracking_object(self, obj: TrackingObject) -> None:
        """追跡対象オブジェクトを削除"""
        if obj in self.tracking_objects:
            self.tracking_objects.remove(obj)
            logger.info(f"追跡対象削除: {obj.obj_type.value}")
    
    def clear_tracking_objects(self) -> None:
        """全ての追跡対象オブジェクトをクリア"""
        self.tracking_objects.clear()
        logger.info("全ての追跡対象をクリア")
    
    def _generate_background(self) -> np.ndarray:
        """背景画像を生成"""
        # グリッドパターンの背景を生成
        background = np.ones((self.height, self.width, 3), dtype=np.uint8) * 240
        
        # グリッド線を描画
        grid_size = 50
        for i in range(0, self.width, grid_size):
            cv2.line(background, (i, 0), (i, self.height), (200, 200, 200), 1)
        for i in range(0, self.height, grid_size):
            cv2.line(background, (0, i), (self.width, i), (200, 200, 200), 1)
        
        return background
    
    def _update_object_position(self, obj: TrackingObject, elapsed_time: float) -> None:
        """オブジェクトの位置を更新"""
        if obj.movement_pattern == MovementPattern.STATIC:
            return
        
        x, y = obj.position
        
        if obj.movement_pattern == MovementPattern.LINEAR:
            # 直線移動
            dx = obj.velocity * np.cos(np.radians(obj.angle)) * elapsed_time
            dy = obj.velocity * np.sin(np.radians(obj.angle)) * elapsed_time
            x += dx
            y += dy
            
            # 画面端で反転
            if x < 0 or x > self.width:
                obj.angle = 180 - obj.angle
            if y < 0 or y > self.height:
                obj.angle = -obj.angle
                
        elif obj.movement_pattern == MovementPattern.CIRCULAR:
            # 円形移動
            radius = 100
            center_x, center_y = obj.center_pos
            angle = (elapsed_time * obj.frequency) % (2 * np.pi)
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            
        elif obj.movement_pattern == MovementPattern.SINE_WAVE:
            # 正弦波移動
            x += obj.velocity * elapsed_time
            y = obj.center_pos[1] + obj.amplitude * np.sin(elapsed_time * obj.frequency)
            
        elif obj.movement_pattern == MovementPattern.RANDOM_WALK:
            # ランダムウォーク
            dx = np.random.normal(0, obj.velocity * elapsed_time)
            dy = np.random.normal(0, obj.velocity * elapsed_time)
            x += dx
            y += dy
        
        # 画面範囲内に制限
        x = max(0, min(self.width - obj.size[0], x))
        y = max(0, min(self.height - obj.size[1], y))
        
        obj.position = (x, y)
    
    def _draw_object(self, frame: np.ndarray, obj: TrackingObject) -> None:
        """オブジェクトを描画"""
        x, y = int(obj.position[0]), int(obj.position[1])
        w, h = obj.size
        
        if obj.obj_type == TrackingObjectType.PERSON:
            # 人物として円と長方形を組み合わせて描画
            cv2.circle(frame, (x + w//2, y + h//4), h//4, obj.color, -1)  # 頭
            cv2.rectangle(frame, (x, y + h//4), (x + w, y + h), obj.color, -1)  # 体
            
        elif obj.obj_type == TrackingObjectType.VEHICLE:
            # 車両として長方形を描画
            cv2.rectangle(frame, (x, y), (x + w, y + h), obj.color, -1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)  # 輪郭
            
        elif obj.obj_type == TrackingObjectType.BALL:
            # ボールとして円を描画
            cv2.circle(frame, (x + w//2, y + h//2), min(w, h)//2, obj.color, -1)
            
        elif obj.obj_type == TrackingObjectType.BOX:
            # 箱として長方形を描画
            cv2.rectangle(frame, (x, y), (x + w, y + h), obj.color, -1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)  # 輪郭
            
        elif obj.obj_type == TrackingObjectType.ANIMAL:
            # 動物として楕円を描画
            cv2.ellipse(frame, (x + w//2, y + h//2), (w//2, h//2), 0, 0, 360, obj.color, -1)
    
    def _generate_frame(self) -> np.ndarray:
        """1フレームを生成"""
        # 背景生成
        frame = self._generate_background()
        
        # 経過時間を計算
        elapsed_time = time.time() - self.start_time
        
        # 全オブジェクトの位置を更新して描画
        for obj in self.tracking_objects:
            self._update_object_position(obj, elapsed_time)
            self._draw_object(frame, obj)
        
        # フレーム情報をオーバーレイ
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"Time: {elapsed_time:.1f}s", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        return frame
    
    def _stream_loop(self) -> None:
        """ストリーミングループ"""
        while self.is_streaming:
            start_time = time.time()
            
            # フレーム生成
            frame = self._generate_frame()
            
            # フレームをロックして更新
            with self.frame_lock:
                self.current_frame = frame
                self.frame_count += 1
            
            # フレームレート制御
            processing_time = time.time() - start_time
            sleep_time = max(0, self.frame_interval - processing_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def start_stream(self) -> None:
        """ストリーミング開始"""
        if self.is_streaming:
            logger.warning("ストリーミングは既に開始されています")
            return
        
        self.is_streaming = True
        self.start_time = time.time()
        self.frame_count = 0
        
        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()
        
        logger.info("仮想カメラストリーミング開始")
    
    def stop_stream(self) -> None:
        """ストリーミング停止"""
        if not self.is_streaming:
            logger.warning("ストリーミングは既に停止されています")
            return
        
        self.is_streaming = False
        if self.stream_thread:
            self.stream_thread.join(timeout=1.0)
        
        logger.info("仮想カメラストリーミング停止")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """現在のフレームを取得"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
    
    def get_statistics(self) -> Dict[str, Union[int, float]]:
        """統計情報を取得"""
        elapsed_time = time.time() - self.start_time
        actual_fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
        
        return {
            "frame_count": self.frame_count,
            "elapsed_time": elapsed_time,
            "target_fps": self.fps,
            "actual_fps": actual_fps,
            "object_count": len(self.tracking_objects)
        }


class VirtualCameraStreamManager:
    """複数の仮想カメラストリームを管理するクラス"""
    
    def __init__(self):
        """初期化"""
        self.streams: Dict[str, VirtualCameraStream] = {}
        logger.info("仮想カメラストリームマネージャー初期化")
    
    def create_stream(self, name: str, width: int = 640, height: int = 480, fps: int = 30) -> VirtualCameraStream:
        """新しいストリームを作成"""
        if name in self.streams:
            logger.warning(f"ストリーム '{name}' は既に存在します")
            return self.streams[name]
        
        stream = VirtualCameraStream(width, height, fps)
        self.streams[name] = stream
        logger.info(f"ストリーム '{name}' を作成")
        return stream
    
    def get_stream(self, name: str) -> Optional[VirtualCameraStream]:
        """ストリームを取得"""
        return self.streams.get(name)
    
    def remove_stream(self, name: str) -> bool:
        """ストリームを削除"""
        if name in self.streams:
            self.streams[name].stop_stream()
            del self.streams[name]
            logger.info(f"ストリーム '{name}' を削除")
            return True
        return False
    
    def start_all_streams(self) -> None:
        """全ストリームを開始"""
        for stream in self.streams.values():
            stream.start_stream()
        logger.info("全ストリームを開始")
    
    def stop_all_streams(self) -> None:
        """全ストリームを停止"""
        for stream in self.streams.values():
            stream.stop_stream()
        logger.info("全ストリームを停止")
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """全ストリームの統計情報を取得"""
        return {name: stream.get_statistics() for name, stream in self.streams.items()}