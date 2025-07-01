"""
Camera Service Tests
Tests for camera streaming and photo capture functionality
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
from datetime import datetime

from backend.api_server.core.camera_service import CameraService
from backend.api_server.models.drone_models import Photo


class TestCameraService:
    """CameraService のテスト"""
    
    @pytest.fixture
    def camera_service(self):
        """テスト用CameraServiceインスタンス"""
        return CameraService()
    
    @pytest.fixture
    def mock_virtual_camera_stream(self):
        """モックVirtualCameraStreamインスタンス"""
        stream = Mock()
        stream.width = 640
        stream.height = 480
        stream.fps = 30
        stream.tracking_objects = []
        stream.start_stream = Mock()
        stream.stop_stream = Mock()
        stream.add_tracking_object = Mock()
        stream.clear_tracking_objects = Mock()
        stream.get_frame = Mock()
        stream.get_statistics = Mock(return_value={
            "frame_count": 100,
            "elapsed_time": 10.0,
            "target_fps": 30,
            "actual_fps": 29.5,
            "object_count": 3
        })
        return stream
    
    @pytest.mark.asyncio
    async def test_start_camera_stream_success(self, camera_service, mock_virtual_camera_stream):
        """カメラストリーミング開始成功テスト"""
        with patch.object(camera_service.camera_manager, 'create_stream') as mock_create:
            mock_create.return_value = mock_virtual_camera_stream
            
            result = await camera_service.start_camera_stream("drone_001")
            
            assert result["success"] is True
            assert "drone_001" in result["message"]
            assert result["stream_id"] == "drone_001"
            assert result["resolution"] == "640x480"
            assert result["fps"] == 30
            
            mock_create.assert_called_once_with(
                name="drone_001",
                width=640,
                height=480,
                fps=30
            )
            mock_virtual_camera_stream.start_stream.assert_called_once()
            assert camera_service.active_streams["drone_001"] == mock_virtual_camera_stream
    
    @pytest.mark.asyncio
    async def test_start_camera_stream_already_active(self, camera_service, mock_virtual_camera_stream):
        """既にアクティブなストリームの開始テスト"""
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        
        result = await camera_service.start_camera_stream("drone_001")
        
        assert result["success"] is True
        assert "already active" in result["message"]
        assert result["stream_id"] == "drone_001"
    
    @pytest.mark.asyncio
    async def test_stop_camera_stream_success(self, camera_service, mock_virtual_camera_stream):
        """カメラストリーミング停止成功テスト"""
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        
        with patch.object(camera_service.camera_manager, 'remove_stream') as mock_remove:
            result = await camera_service.stop_camera_stream("drone_001")
            
            assert result["success"] is True
            assert "drone_001" in result["message"]
            assert result["stream_id"] == "drone_001"
            
            mock_virtual_camera_stream.stop_stream.assert_called_once()
            mock_remove.assert_called_once_with("drone_001")
            assert "drone_001" not in camera_service.active_streams
    
    @pytest.mark.asyncio
    async def test_stop_camera_stream_not_active(self, camera_service):
        """アクティブでないストリームの停止テスト"""
        result = await camera_service.stop_camera_stream("drone_001")
        
        assert result["success"] is True
        assert "No active camera stream" in result["message"]
        assert result["stream_id"] == "drone_001"
    
    @pytest.mark.asyncio
    async def test_capture_photo_with_active_stream(self, camera_service, mock_virtual_camera_stream):
        """アクティブなストリームでの写真撮影テスト"""
        # テスト用フレームデータを作成
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[:, :] = [100, 150, 200]  # BGR colors
        mock_virtual_camera_stream.get_frame.return_value = test_frame
        
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        
        with patch('cv2.imencode') as mock_imencode:
            # cv2.imencode の戻り値をモック
            mock_buffer = np.array([1, 2, 3, 4, 5], dtype=np.uint8)
            mock_imencode.return_value = (True, mock_buffer)
            
            photo = await camera_service.capture_photo("drone_001")
            
            assert isinstance(photo, Photo)
            assert photo.drone_id == "drone_001"
            assert photo.filename.startswith("drone_photo_drone_001_")
            assert photo.filename.endswith(".jpg")
            assert photo.path.startswith("/photos/")
            assert photo.metadata["resolution"] == "640x480"
            assert photo.metadata["format"] == "JPEG"
            assert photo.metadata["size_bytes"] == 5
            
            mock_virtual_camera_stream.get_frame.assert_called()
            mock_imencode.assert_called_once_with('.jpg', test_frame)
    
    @pytest.mark.asyncio
    async def test_capture_photo_without_active_stream(self, camera_service, mock_virtual_camera_stream):
        """アクティブでないストリームでの写真撮影テスト（一時ストリーム作成）"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_virtual_camera_stream.get_frame.return_value = test_frame
        
        with patch.object(camera_service, 'start_camera_stream') as mock_start, \
             patch.object(camera_service, 'stop_camera_stream') as mock_stop, \
             patch('cv2.imencode') as mock_imencode:
            
            mock_start.return_value = {"success": True}
            mock_stop.return_value = {"success": True}
            camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
            
            mock_buffer = np.array([1, 2, 3], dtype=np.uint8)
            mock_imencode.return_value = (True, mock_buffer)
            
            photo = await camera_service.capture_photo("drone_001")
            
            assert isinstance(photo, Photo)
            assert photo.drone_id == "drone_001"
            
            mock_start.assert_called_once_with("drone_001")
            mock_stop.assert_called_once_with("drone_001")
    
    @pytest.mark.asyncio
    async def test_capture_photo_no_frame_available(self, camera_service, mock_virtual_camera_stream):
        """フレーム取得不可時の写真撮影テスト"""
        mock_virtual_camera_stream.get_frame.return_value = None
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        
        with pytest.raises(ValueError, match="Unable to capture frame"):
            await camera_service.capture_photo("drone_001")
    
    @pytest.mark.asyncio
    async def test_capture_photo_encoding_failure(self, camera_service, mock_virtual_camera_stream):
        """画像エンコーディング失敗時のテスト"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_virtual_camera_stream.get_frame.return_value = test_frame
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        
        with patch('cv2.imencode') as mock_imencode:
            mock_imencode.return_value = (False, None)
            
            with pytest.raises(ValueError, match="Failed to encode frame as JPEG"):
                await camera_service.capture_photo("drone_001")
    
    @pytest.mark.asyncio
    async def test_get_stream_info_existing_stream(self, camera_service, mock_virtual_camera_stream):
        """既存ストリームの情報取得テスト"""
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        
        info = await camera_service.get_stream_info("drone_001")
        
        assert info is not None
        assert info["drone_id"] == "drone_001"
        assert info["is_active"] is True
        assert info["width"] == 640
        assert info["height"] == 480
        assert info["target_fps"] == 30
        assert "statistics" in info
        assert info["tracking_objects"] == 0
    
    @pytest.mark.asyncio
    async def test_get_stream_info_non_existing_stream(self, camera_service):
        """存在しないストリームの情報取得テスト"""
        info = await camera_service.get_stream_info("drone_001")
        assert info is None
    
    @pytest.mark.asyncio
    async def test_get_all_streams_info(self, camera_service, mock_virtual_camera_stream):
        """全ストリーム情報取得テスト"""
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        camera_service.active_streams["drone_002"] = mock_virtual_camera_stream
        
        info_list = await camera_service.get_all_streams_info()
        
        assert len(info_list) == 2
        assert all(info["is_active"] for info in info_list)
    
    @pytest.mark.asyncio
    async def test_get_current_frame_base64(self, camera_service, mock_virtual_camera_stream):
        """現在フレームのBase64取得テスト"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_virtual_camera_stream.get_frame.return_value = test_frame
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        
        with patch('cv2.imencode') as mock_imencode:
            mock_buffer = np.array([1, 2, 3], dtype=np.uint8)
            mock_imencode.return_value = (True, mock_buffer)
            
            base64_data = await camera_service.get_current_frame_base64("drone_001")
            
            assert base64_data is not None
            assert isinstance(base64_data, str)
            mock_imencode.assert_called_once_with('.jpg', test_frame)
    
    @pytest.mark.asyncio
    async def test_get_current_frame_base64_no_stream(self, camera_service):
        """ストリームがない場合のBase64取得テスト"""
        base64_data = await camera_service.get_current_frame_base64("drone_001")
        assert base64_data is None
    
    @pytest.mark.asyncio
    async def test_add_tracking_object(self, camera_service, mock_virtual_camera_stream):
        """追跡オブジェクト追加テスト"""
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        
        object_config = {
            "type": "person",
            "position": [200, 150],
            "size": [40, 80],
            "color": [255, 0, 0],
            "movement_pattern": "linear",
            "movement_speed": 30.0
        }
        
        result = await camera_service.add_tracking_object("drone_001", object_config)
        
        assert result["success"] is True
        assert "drone_001" in result["message"]
        assert result["object_type"] == "person"
        assert result["position"] == (200, 150)
        
        mock_virtual_camera_stream.add_tracking_object.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_tracking_object_no_stream(self, camera_service):
        """ストリームがない場合の追跡オブジェクト追加テスト"""
        object_config = {"type": "person"}
        
        with pytest.raises(ValueError, match="No active camera stream"):
            await camera_service.add_tracking_object("drone_001", object_config)
    
    @pytest.mark.asyncio
    async def test_clear_tracking_objects(self, camera_service, mock_virtual_camera_stream):
        """追跡オブジェクトクリアテスト"""
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        
        result = await camera_service.clear_tracking_objects("drone_001")
        
        assert result["success"] is True
        assert "drone_001" in result["message"]
        mock_virtual_camera_stream.clear_tracking_objects.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_tracking_objects_no_stream(self, camera_service):
        """ストリームがない場合の追跡オブジェクトクリアテスト"""
        with pytest.raises(ValueError, match="No active camera stream"):
            await camera_service.clear_tracking_objects("drone_001")
    
    @pytest.mark.asyncio
    async def test_shutdown(self, camera_service, mock_virtual_camera_stream):
        """シャットダウンテスト"""
        camera_service.active_streams["drone_001"] = mock_virtual_camera_stream
        camera_service.active_streams["drone_002"] = mock_virtual_camera_stream
        
        with patch.object(camera_service, 'stop_camera_stream') as mock_stop, \
             patch.object(camera_service.camera_manager, 'stop_all_streams') as mock_stop_all:
            
            mock_stop.return_value = {"success": True}
            
            await camera_service.shutdown()
            
            assert mock_stop.call_count == 2
            mock_stop_all.assert_called_once()


@pytest.mark.asyncio
async def test_camera_service_integration():
    """CameraService統合テスト"""
    camera_service = CameraService()
    
    try:
        # ストリーム開始
        result = await camera_service.start_camera_stream("test_drone")
        assert result["success"] is True
        
        # ストリーム情報取得
        info = await camera_service.get_stream_info("test_drone")
        assert info is not None
        assert info["is_active"] is True
        
        # フレーム取得を試行（実際のフレームが生成されるまで少し待機）
        await asyncio.sleep(0.2)
        
        # Base64フレーム取得
        base64_data = await camera_service.get_current_frame_base64("test_drone")
        assert base64_data is not None
        
        # 追跡オブジェクト追加
        object_config = {
            "type": "ball",
            "position": [100, 100],
            "size": [30, 30],
            "color": [0, 0, 255],
            "movement_pattern": "circular"
        }
        result = await camera_service.add_tracking_object("test_drone", object_config)
        assert result["success"] is True
        
        # 写真撮影
        photo = await camera_service.capture_photo("test_drone")
        assert isinstance(photo, Photo)
        assert photo.drone_id == "test_drone"
        
        # 追跡オブジェクトクリア
        result = await camera_service.clear_tracking_objects("test_drone")
        assert result["success"] is True
        
        # ストリーム停止
        result = await camera_service.stop_camera_stream("test_drone")
        assert result["success"] is True
        
    finally:
        # クリーンアップ
        await camera_service.shutdown()