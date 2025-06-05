"""
カメラ操作APIのテスト
"""

import pytest
from tests.stubs.drone_stub import TelloStub


class TestVideoStreaming:
    """ビデオストリーミングテストクラス"""
    
    def test_streamon_success(self, connected_drone):
        """ストリーミング開始成功テスト"""
        result = connected_drone.streamon()
        assert result is True
        assert connected_drone._streaming is True
    
    def test_streamon_not_connected(self, drone):
        """未接続時のストリーミング開始テスト"""
        result = drone.streamon()
        assert result is False
        assert drone._streaming is False
    
    def test_streamon_already_streaming(self, connected_drone):
        """既にストリーミング中の開始テスト"""
        # 最初のストリーミング開始
        connected_drone.streamon()
        assert connected_drone._streaming is True
        
        # 2回目のストリーミング開始（失敗）
        result = connected_drone.streamon()
        assert result is False
    
    def test_streamon_command_failure(self, connected_drone):
        """ストリーミング開始コマンド失敗テスト"""
        connected_drone.set_simulate_command_error(True)
        result = connected_drone.streamon()
        assert result is False
        assert connected_drone._streaming is False
    
    def test_streamoff_success(self, connected_drone):
        """ストリーミング停止成功テスト"""
        # ストリーミング開始
        connected_drone.streamon()
        assert connected_drone._streaming is True
        
        # ストリーミング停止
        result = connected_drone.streamoff()
        assert result is True
        assert connected_drone._streaming is False
    
    def test_streamoff_not_connected(self, drone):
        """未接続時のストリーミング停止テスト"""
        result = drone.streamoff()
        assert result is False
    
    def test_streamoff_not_streaming(self, connected_drone):
        """ストリーミング未開始での停止テスト"""
        result = connected_drone.streamoff()
        assert result is False
    
    def test_get_frame_read_success(self, connected_drone):
        """フレーム読み取り成功テスト"""
        # ストリーミング開始
        connected_drone.streamon()
        
        # フレーム読み取りオブジェクト取得
        frame_read = connected_drone.get_frame_read()
        assert frame_read is not None
    
    def test_get_frame_read_not_streaming(self, connected_drone):
        """ストリーミング未開始でのフレーム読み取りテスト"""
        frame_read = connected_drone.get_frame_read()
        assert frame_read is None


class TestPhotoCapture:
    """写真撮影テストクラス"""
    
    def test_take_picture_success(self, connected_drone):
        """写真撮影成功テスト"""
        result = connected_drone.take_picture()
        assert result is True
    
    def test_take_picture_not_connected(self, drone):
        """未接続時の写真撮影テスト"""
        result = drone.take_picture()
        assert result is False
    
    def test_take_picture_command_failure(self, connected_drone):
        """写真撮影コマンド失敗テスト"""
        connected_drone.set_simulate_command_error(True)
        result = connected_drone.take_picture()
        assert result is False
    
    def test_take_picture_while_streaming(self, connected_drone):
        """ストリーミング中の写真撮影テスト"""
        # ストリーミング開始
        connected_drone.streamon()
        
        # 写真撮影
        result = connected_drone.take_picture()
        assert result is True
    
    def test_take_picture_while_flying(self, flying_drone):
        """飛行中の写真撮影テスト"""
        result = flying_drone.take_picture()
        assert result is True


class TestVideoRecording:
    """動画録画テストクラス"""
    
    def test_start_video_capture_success(self, connected_drone):
        """動画録画開始成功テスト"""
        result = connected_drone.start_video_capture()
        assert result is True
    
    def test_start_video_capture_not_connected(self, drone):
        """未接続時の動画録画開始テスト"""
        result = drone.start_video_capture()
        assert result is False
    
    def test_start_video_capture_command_failure(self, connected_drone):
        """動画録画開始コマンド失敗テスト"""
        connected_drone.set_simulate_command_error(True)
        result = connected_drone.start_video_capture()
        assert result is False
    
    def test_stop_video_capture_success(self, connected_drone):
        """動画録画停止成功テスト"""
        # 録画開始
        connected_drone.start_video_capture()
        
        # 録画停止
        result = connected_drone.stop_video_capture()
        assert result is True
    
    def test_stop_video_capture_not_connected(self, drone):
        """未接続時の動画録画停止テスト"""
        result = drone.stop_video_capture()
        assert result is False
    
    def test_stop_video_capture_command_failure(self, connected_drone):
        """動画録画停止コマンド失敗テスト"""
        connected_drone.set_simulate_command_error(True)
        result = connected_drone.stop_video_capture()
        assert result is False


class TestCameraSettings:
    """カメラ設定テストクラス"""
    
    def test_set_video_resolution_success(self, connected_drone):
        """ビデオ解像度設定成功テスト"""
        # 高解像度設定
        result_high = connected_drone.set_video_resolution("high")
        assert result_high is True
        
        # 低解像度設定
        result_low = connected_drone.set_video_resolution("low")
        assert result_low is True
    
    def test_set_video_resolution_invalid(self, connected_drone):
        """無効なビデオ解像度設定テスト"""
        result = connected_drone.set_video_resolution("invalid")
        assert result is False
    
    def test_set_video_resolution_not_connected(self, drone):
        """未接続時のビデオ解像度設定テスト"""
        result = drone.set_video_resolution("high")
        assert result is False
    
    def test_set_video_fps_success(self, connected_drone):
        """ビデオFPS設定成功テスト"""
        # 高FPS設定
        result_high = connected_drone.set_video_fps("high")
        assert result_high is True
        
        # 中FPS設定
        result_middle = connected_drone.set_video_fps("middle")
        assert result_middle is True
        
        # 低FPS設定
        result_low = connected_drone.set_video_fps("low")
        assert result_low is True
    
    def test_set_video_fps_invalid(self, connected_drone):
        """無効なビデオFPS設定テスト"""
        result = connected_drone.set_video_fps("invalid")
        assert result is False
    
    def test_set_video_fps_not_connected(self, drone):
        """未接続時のビデオFPS設定テスト"""
        result = drone.set_video_fps("high")
        assert result is False
    
    def test_set_video_bitrate_success(self, connected_drone):
        """ビデオビットレート設定成功テスト"""
        # 境界値テスト
        for bitrate in range(1, 6):
            result = connected_drone.set_video_bitrate(bitrate)
            assert result is True
    
    def test_set_video_bitrate_boundary_values(self, connected_drone):
        """ビデオビットレート境界値テスト"""
        # 最小値
        result_min = connected_drone.set_video_bitrate(1)
        assert result_min is True
        
        # 最大値
        result_max = connected_drone.set_video_bitrate(5)
        assert result_max is True
    
    def test_set_video_bitrate_invalid(self, connected_drone):
        """無効なビデオビットレート設定テスト"""
        # 最小値未満
        result_too_low = connected_drone.set_video_bitrate(0)
        assert result_too_low is False
        
        # 最大値超過
        result_too_high = connected_drone.set_video_bitrate(6)
        assert result_too_high is False
        
        # 負の値
        result_negative = connected_drone.set_video_bitrate(-1)
        assert result_negative is False
    
    def test_set_video_bitrate_not_connected(self, drone):
        """未接続時のビデオビットレート設定テスト"""
        result = drone.set_video_bitrate(3)
        assert result is False


class TestCameraSequence:
    """カメラ操作シーケンステストクラス"""
    
    def test_complete_camera_sequence(self, connected_drone):
        """完全なカメラ操作シーケンステスト"""
        # 設定変更
        connected_drone.set_video_resolution("high")
        connected_drone.set_video_fps("middle")
        connected_drone.set_video_bitrate(4)
        
        # ストリーミング開始
        stream_result = connected_drone.streamon()
        assert stream_result is True
        
        # 写真撮影
        photo_result = connected_drone.take_picture()
        assert photo_result is True
        
        # 動画録画開始
        video_start_result = connected_drone.start_video_capture()
        assert video_start_result is True
        
        # 動画録画停止
        video_stop_result = connected_drone.stop_video_capture()
        assert video_stop_result is True
        
        # ストリーミング停止
        stream_stop_result = connected_drone.streamoff()
        assert stream_stop_result is True
    
    def test_streaming_state_management(self, connected_drone):
        """ストリーミング状態管理テスト"""
        # 初期状態
        assert connected_drone._streaming is False
        
        # ストリーミング開始
        connected_drone.streamon()
        assert connected_drone._streaming is True
        
        # ストリーミング停止
        connected_drone.streamoff()
        assert connected_drone._streaming is False
    
    def test_camera_settings_combinations(self, connected_drone):
        """カメラ設定組み合わせテスト"""
        # 各設定の組み合わせテスト
        resolutions = ["high", "low"]
        fps_settings = ["high", "middle", "low"]
        bitrates = [1, 3, 5]
        
        for resolution in resolutions:
            for fps in fps_settings:
                for bitrate in bitrates:
                    res_result = connected_drone.set_video_resolution(resolution)
                    fps_result = connected_drone.set_video_fps(fps)
                    bit_result = connected_drone.set_video_bitrate(bitrate)
                    
                    assert res_result is True
                    assert fps_result is True
                    assert bit_result is True
    
    def test_camera_error_recovery(self, connected_drone):
        """カメラエラー回復テスト"""
        # エラー設定
        connected_drone.set_simulate_command_error(True)
        
        # エラー状態での操作
        stream_error = connected_drone.streamon()
        photo_error = connected_drone.take_picture()
        video_error = connected_drone.start_video_capture()
        
        assert stream_error is False
        assert photo_error is False
        assert video_error is False
        
        # エラー解除後の正常動作
        connected_drone.set_simulate_command_error(False)
        
        stream_success = connected_drone.streamon()
        photo_success = connected_drone.take_picture()
        video_success = connected_drone.start_video_capture()
        
        assert stream_success is True
        assert photo_success is True
        assert video_success is True