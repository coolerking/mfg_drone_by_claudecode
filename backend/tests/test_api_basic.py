"""
Basic API tests for MFG Drone Backend API Server
Tests basic drone control endpoints and integration with DroneSimulator
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime

from api_server.main import app
from api_server.core.drone_manager import DroneManager


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def drone_manager():
    """Test drone manager instance"""
    return DroneManager()


class TestBasicAPI:
    """基本API機能のテスト"""
    
    def test_root_endpoint(self, client):
        """ルートエンドポイントのテスト"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "MFG Drone Backend API Server"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_health_check(self, client):
        """ヘルスチェックエンドポイントのテスト"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data


class TestDroneAPI:
    """ドローンAPI機能のテスト"""
    
    def test_get_drones(self, client):
        """ドローン一覧取得のテスト"""
        response = client.get("/api/drones")
        assert response.status_code == 200
        
        drones = response.json()
        assert isinstance(drones, list)
        assert len(drones) >= 3  # ダミードローンが3台
        
        # 最初のドローンの構造をチェック
        drone = drones[0]
        required_fields = ["id", "name", "type", "status"]
        for field in required_fields:
            assert field in drone
        
        assert drone["type"] == "dummy"
        assert drone["status"] == "disconnected"
    
    def test_drone_connection_flow(self, client):
        """ドローン接続フローのテスト"""
        drone_id = "drone_001"
        
        # 1. 接続
        response = client.post(f"/api/drones/{drone_id}/connect")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert drone_id in data["message"]
        
        # 2. 状態確認
        response = client.get(f"/api/drones/{drone_id}/status")
        assert response.status_code == 200
        status = response.json()
        assert status["drone_id"] == drone_id
        assert status["connection_status"] == "connected"
        assert status["flight_status"] == "landed"
        assert 0 <= status["battery_level"] <= 100
        
        # 3. 切断
        response = client.post(f"/api/drones/{drone_id}/disconnect")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_drone_flight_basic_flow(self, client):
        """基本的な飛行フローのテスト"""
        drone_id = "drone_001"
        
        # 接続
        response = client.post(f"/api/drones/{drone_id}/connect")
        assert response.status_code == 200
        
        try:
            # 離陸
            response = client.post(f"/api/drones/{drone_id}/takeoff")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # 少し待機してから状態確認
            import time
            time.sleep(0.2)
            
            response = client.get(f"/api/drones/{drone_id}/status")
            assert response.status_code == 200
            status = response.json()
            # 離陸中または飛行中の状態
            assert status["flight_status"] in ["taking_off", "flying"]
            
            # 着陸
            response = client.post(f"/api/drones/{drone_id}/land")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
        finally:
            # クリーンアップ
            client.post(f"/api/drones/{drone_id}/disconnect")
    
    def test_drone_movement_commands(self, client):
        """ドローン移動コマンドのテスト"""
        drone_id = "drone_001"
        
        # 接続と離陸
        client.post(f"/api/drones/{drone_id}/connect")
        client.post(f"/api/drones/{drone_id}/takeoff")
        
        try:
            # 移動コマンドテスト
            move_commands = [
                {"direction": "forward", "distance": 50},
                {"direction": "right", "distance": 30},
                {"direction": "up", "distance": 20}
            ]
            
            for cmd in move_commands:
                response = client.post(f"/api/drones/{drone_id}/move", json=cmd)
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
            
            # 回転コマンドテスト
            rotate_commands = [
                {"direction": "clockwise", "angle": 90},
                {"direction": "counter_clockwise", "angle": 45}
            ]
            
            for cmd in rotate_commands:
                response = client.post(f"/api/drones/{drone_id}/rotate", json=cmd)
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                
        finally:
            # クリーンアップ
            client.post(f"/api/drones/{drone_id}/land")
            client.post(f"/api/drones/{drone_id}/disconnect")
    
    def test_drone_emergency_stop(self, client):
        """緊急停止のテスト"""
        drone_id = "drone_001"
        
        # 接続と離陸
        client.post(f"/api/drones/{drone_id}/connect")
        client.post(f"/api/drones/{drone_id}/takeoff")
        
        try:
            # 緊急停止
            response = client.post(f"/api/drones/{drone_id}/emergency")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
        finally:
            # クリーンアップ
            client.post(f"/api/drones/{drone_id}/disconnect")
    
    def test_camera_endpoints_basic(self, client):
        """カメラエンドポイントの基本テスト"""
        drone_id = "drone_001"
        
        # 接続
        client.post(f"/api/drones/{drone_id}/connect")
        
        try:
            # カメラストリーミング開始
            response = client.post(f"/api/drones/{drone_id}/camera/stream/start")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # カメラストリーミング停止
            response = client.post(f"/api/drones/{drone_id}/camera/stream/stop")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # 写真撮影
            response = client.post(f"/api/drones/{drone_id}/camera/photo")
            assert response.status_code == 200
            photo = response.json()
            assert "id" in photo
            assert "filename" in photo
            assert "path" in photo
            assert "timestamp" in photo
            assert photo["drone_id"] == drone_id
            
        finally:
            # クリーンアップ
            client.post(f"/api/drones/{drone_id}/disconnect")


class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def test_drone_not_found(self, client):
        """存在しないドローンに対するエラーハンドリング"""
        invalid_drone_id = "invalid_drone"
        
        response = client.post(f"/api/drones/{invalid_drone_id}/connect")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "指定されたドローンが見つかりません"
    
    def test_drone_not_connected_operations(self, client):
        """未接続ドローンに対する操作のエラーハンドリング"""
        drone_id = "drone_001"
        
        # 接続せずに離陸を試行
        response = client.post(f"/api/drones/{drone_id}/takeoff")
        assert response.status_code in [400, 404, 503]  # エラー応答
    
    def test_invalid_move_command(self, client):
        """無効な移動コマンドのテスト"""
        drone_id = "drone_001"
        client.post(f"/api/drones/{drone_id}/connect")
        
        try:
            # 無効な距離
            invalid_command = {"direction": "forward", "distance": 1000}  # 500cm超過
            response = client.post(f"/api/drones/{drone_id}/move", json=invalid_command)
            assert response.status_code == 422  # Validation error
            
        finally:
            client.post(f"/api/drones/{drone_id}/disconnect")
    
    def test_invalid_rotate_command(self, client):
        """無効な回転コマンドのテスト"""
        drone_id = "drone_001"
        client.post(f"/api/drones/{drone_id}/connect")
        
        try:
            # 無効な角度
            invalid_command = {"direction": "clockwise", "angle": 500}  # 360度超過
            response = client.post(f"/api/drones/{drone_id}/move", json=invalid_command)
            assert response.status_code == 422  # Validation error
            
        finally:
            client.post(f"/api/drones/{drone_id}/disconnect")


@pytest.mark.asyncio
class TestDroneManagerIntegration:
    """DroneManagerとの統合テスト"""
    
    async def test_drone_manager_initialization(self, drone_manager):
        """DroneManagerの初期化テスト"""
        assert drone_manager is not None
        assert drone_manager.multi_drone_simulator is not None
        
        # ダミードローンが初期化されていることを確認
        drones = await drone_manager.get_available_drones()
        assert len(drones) >= 3
        
        for drone in drones:
            assert drone.type == "dummy"
            assert drone.status == "disconnected"
    
    async def test_full_drone_lifecycle(self, drone_manager):
        """ドローンのライフサイクル全体テスト"""
        drone_id = "drone_001"
        
        try:
            # 接続
            result = await drone_manager.connect_drone(drone_id)
            assert result.success is True
            
            # 状態確認
            status = await drone_manager.get_drone_status(drone_id)
            assert status.connection_status == "connected"
            
            # 離陸
            result = await drone_manager.takeoff_drone(drone_id)
            assert result.success is True
            
            # 少し待機
            await asyncio.sleep(0.1)
            
            # 移動
            result = await drone_manager.move_drone(drone_id, "forward", 100)
            assert result.success is True
            
            # 回転
            result = await drone_manager.rotate_drone(drone_id, "clockwise", 90)
            assert result.success is True
            
            # 着陸
            result = await drone_manager.land_drone(drone_id)
            assert result.success is True
            
        finally:
            # クリーンアップ
            await drone_manager.disconnect_drone(drone_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])