"""
Phase 6: Real-Simulation Drone Switching Tests
Tests for API compatibility and seamless switching between real and simulation drones
"""

import asyncio
import pytest
import logging
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from api_server.core.drone_manager import DroneManager
from api_server.core.drone_factory import DroneFactory, DroneMode, DroneConfig
from api_server.core.tello_edu_controller import TelloEDUController
from src.core.drone_simulator import DroneSimulator
from api_server.models.drone_models import DroneStatus

logger = logging.getLogger(__name__)


class TestRealSimulationSwitching:
    """Test real-simulation drone switching functionality"""
    
    @pytest.fixture
    def mock_config_data(self):
        """Mock configuration data for testing"""
        return {
            "global": {
                "space_bounds": [20.0, 20.0, 10.0]
            },
            "drones": [
                {
                    "id": "hybrid_drone_001",
                    "name": "Hybrid Test Drone #1",
                    "mode": "auto",
                    "ip_address": "192.168.1.100",
                    "auto_detect": True
                },
                {
                    "id": "simulation_drone_001", 
                    "name": "Simulation Test Drone #1",
                    "mode": "simulation",
                    "position": [0, 0, 0]
                },
                {
                    "id": "real_drone_001",
                    "name": "Real Test Drone #1", 
                    "mode": "real",
                    "ip_address": "192.168.1.101",
                    "auto_detect": False
                }
            ]
        }
    
    @pytest.fixture
    async def drone_manager(self, mock_config_data):
        """Create DroneManager with mock configuration"""
        with patch('api_server.core.config_service.ConfigService') as mock_config_service:
            mock_config_service.return_value.get_all_config.return_value = mock_config_data
            
            manager = DroneManager()
            yield manager
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_api_compatibility_between_real_and_simulation(self, drone_manager):
        """Test that API responses are compatible between real and simulation drones"""
        
        # Test simulation drone first
        await drone_manager.connect_drone("simulation_drone_001")
        sim_status = await drone_manager.get_drone_status("simulation_drone_001")
        
        # Mock real drone connection
        with patch.object(TelloEDUController, '__init__', return_value=None), \
             patch.object(TelloEDUController, 'connect', return_value=True), \
             patch.object(TelloEDUController, 'get_statistics', return_value={
                 "battery_level": 85,
                 "flight_state": "idle",
                 "total_flight_time": 120
             }), \
             patch.object(TelloEDUController, 'get_current_position', return_value=(0.0, 0.0, 0.0)), \
             patch.object(TelloEDUController, 'get_current_velocity', return_value=(0.0, 0.0, 0.0)), \
             patch.object(TelloEDUController, 'get_real_drone_info', return_value={
                 "height": 0,
                 "temperature": 24.5,
                 "wifi_signal": 95,
                 "attitude": {"pitch": 0.0, "roll": 0.0, "yaw": 0.0},
                 "speed": {"x": 0.0, "y": 0.0, "z": 0.0}
             }):
            
            await drone_manager.connect_drone("real_drone_001")
            real_status = await drone_manager.get_drone_status("real_drone_001")
        
        # Verify API compatibility - both should have same structure
        assert isinstance(sim_status, DroneStatus)
        assert isinstance(real_status, DroneStatus)
        
        # Check required fields are present in both
        required_fields = ['drone_id', 'connection_status', 'flight_status', 'battery_level', 'last_updated']
        for field in required_fields:
            assert hasattr(sim_status, field), f"Simulation status missing field: {field}"
            assert hasattr(real_status, field), f"Real status missing field: {field}"
        
        # Check optional fields are handled gracefully
        optional_fields = ['flight_time', 'height', 'temperature', 'speed', 'wifi_signal', 'attitude']
        for field in optional_fields:
            sim_value = getattr(sim_status, field, None)
            real_value = getattr(real_status, field, None)
            
            # Both should either have the field or handle its absence gracefully
            assert sim_value is not None or real_value is not None, f"Both missing optional field: {field}"
        
        logger.info("✅ API compatibility verified between real and simulation drones")
    
    @pytest.mark.asyncio
    async def test_seamless_mode_switching(self, drone_manager):
        """Test seamless switching between real and simulation modes"""
        
        drone_id = "hybrid_drone_001"
        
        # Start with simulation mode (fallback)
        await drone_manager.connect_drone(drone_id)
        initial_status = await drone_manager.get_drone_status(drone_id)
        
        # Verify initial connection
        assert initial_status.connection_status == "connected"
        initial_drone_instance = drone_manager.connected_drones[drone_id]
        
        # Disconnect and simulate real drone becoming available
        await drone_manager.disconnect_drone(drone_id)
        
        # Mock real drone detection and connection
        with patch.object(TelloEDUController, '__init__', return_value=None), \
             patch.object(TelloEDUController, 'connect', return_value=True), \
             patch.object(drone_manager.drone_factory, 'create_drone') as mock_create:
            
            # Mock factory to return real drone
            mock_real_drone = Mock(spec=TelloEDUController)
            mock_real_drone.ip_address = "192.168.1.100"
            mock_real_drone.get_statistics.return_value = {"battery_level": 90, "flight_state": "idle"}
            mock_real_drone.get_current_position.return_value = (0.0, 0.0, 0.0)
            mock_real_drone.get_current_velocity.return_value = (0.0, 0.0, 0.0)
            mock_real_drone.get_real_drone_info.return_value = {"height": 0, "temperature": 25.0}
            mock_create.return_value = mock_real_drone
            
            # Reconnect - should now use real drone
            await drone_manager.connect_drone(drone_id)
            
            # Verify switch to real drone
            new_status = await drone_manager.get_drone_status(drone_id)
            assert new_status.connection_status == "connected"
            
            new_drone_instance = drone_manager.connected_drones[drone_id]
            
            # Verify drone type switched from simulation to real
            assert type(initial_drone_instance) != type(new_drone_instance)
            assert isinstance(new_drone_instance, Mock)  # Our mock real drone
        
        logger.info("✅ Seamless mode switching verified")
    
    @pytest.mark.asyncio
    async def test_control_commands_compatibility(self, drone_manager):
        """Test that control commands work identically for real and simulation drones"""
        
        # Test with simulation drone
        await drone_manager.connect_drone("simulation_drone_001")
        
        # Test takeoff command
        sim_takeoff_result = await drone_manager.takeoff_drone("simulation_drone_001")
        assert sim_takeoff_result.message is not None
        
        # Test movement command
        sim_move_result = await drone_manager.move_drone("simulation_drone_001", "forward", 100)
        assert sim_move_result.message is not None
        
        # Test rotation command
        sim_rotate_result = await drone_manager.rotate_drone("simulation_drone_001", "clockwise", 90)
        assert sim_rotate_result.message is not None
        
        # Test land command
        sim_land_result = await drone_manager.land_drone("simulation_drone_001")
        assert sim_land_result.message is not None
        
        # Mock real drone and test same commands
        with patch.object(TelloEDUController, '__init__', return_value=None), \
             patch.object(TelloEDUController, 'takeoff', return_value=True), \
             patch.object(TelloEDUController, 'move_to_position', return_value=True), \
             patch.object(TelloEDUController, 'rotate_to_yaw', return_value=True), \
             patch.object(TelloEDUController, 'land', return_value=True), \
             patch.object(TelloEDUController, 'get_battery_level', return_value=85), \
             patch.object(TelloEDUController, 'get_current_position', return_value=(0, 0, 0)):
            
            await drone_manager.connect_drone("real_drone_001")
            
            # Test same commands with real drone
            real_takeoff_result = await drone_manager.takeoff_drone("real_drone_001")
            assert real_takeoff_result.message is not None
            
            real_move_result = await drone_manager.move_drone("real_drone_001", "forward", 100)
            assert real_move_result.message is not None
            
            real_rotate_result = await drone_manager.rotate_drone("real_drone_001", "clockwise", 90)
            assert real_rotate_result.message is not None
            
            real_land_result = await drone_manager.land_drone("real_drone_001")
            assert real_land_result.message is not None
            
        # Verify response structure compatibility
        assert type(sim_takeoff_result) == type(real_takeoff_result)
        assert type(sim_move_result) == type(real_move_result)
        assert type(sim_rotate_result) == type(real_rotate_result)
        assert type(sim_land_result) == type(real_land_result)
        
        logger.info("✅ Control commands compatibility verified")
    
    @pytest.mark.asyncio
    async def test_error_handling_consistency(self, drone_manager):
        """Test that error handling is consistent between real and simulation drones"""
        
        # Test error cases with simulation drone
        await drone_manager.connect_drone("simulation_drone_001")
        
        # Test invalid commands
        with pytest.raises(ValueError, match="Invalid direction"):
            await drone_manager.move_drone("simulation_drone_001", "invalid_direction", 100)
        
        with pytest.raises(ValueError, match="Invalid direction"):
            await drone_manager.rotate_drone("simulation_drone_001", "invalid_rotation", 90)
        
        # Test low battery scenario
        with patch.object(drone_manager.connected_drones["simulation_drone_001"], 'get_battery_level', return_value=5):
            with pytest.raises(ValueError, match="バッテリー残量不足"):
                await drone_manager.takeoff_drone("simulation_drone_001")
        
        # Test with real drone - should have same error behavior
        with patch.object(TelloEDUController, '__init__', return_value=None), \
             patch.object(TelloEDUController, 'get_battery_level', return_value=5):
            
            await drone_manager.connect_drone("real_drone_001")
            
            # Test same error cases
            with pytest.raises(ValueError, match="Invalid direction"):
                await drone_manager.move_drone("real_drone_001", "invalid_direction", 100)
            
            with pytest.raises(ValueError, match="Invalid direction"):
                await drone_manager.rotate_drone("real_drone_001", "invalid_rotation", 90)
            
            with pytest.raises(ValueError, match="バッテリー残量不足"):
                await drone_manager.takeoff_drone("real_drone_001")
        
        logger.info("✅ Error handling consistency verified")
    
    @pytest.mark.asyncio
    async def test_network_detection_and_fallback(self, drone_manager):
        """Test network detection and automatic fallback to simulation"""
        
        # Test scanning for real drones
        with patch.object(drone_manager.network_service, 'scan_network', return_value=[]):
            detected_drones = await drone_manager.scan_for_real_drones(timeout=1.0)
            assert isinstance(detected_drones, list)
        
        # Test network status retrieval
        network_status = await drone_manager.get_network_status()
        assert isinstance(network_status, dict)
        assert "total_connected_drones" in network_status
        assert "real_connected_count" in network_status
        assert "simulation_connected_count" in network_status
        
        # Test verification of real drone connection
        verification_result = await drone_manager.verify_real_drone_connection("192.168.1.100")
        assert isinstance(verification_result, dict)
        assert "ip_address" in verification_result
        assert "is_reachable" in verification_result
        
        logger.info("✅ Network detection and fallback verified")
    
    @pytest.mark.asyncio
    async def test_drone_type_information_consistency(self, drone_manager):
        """Test that drone type information is consistently provided"""
        
        # Connect different types of drones
        await drone_manager.connect_drone("simulation_drone_001")
        
        with patch.object(TelloEDUController, '__init__', return_value=None), \
             patch.object(TelloEDUController, 'get_connection_state') as mock_connection_state:
            
            mock_connection_state.return_value = Mock()
            mock_connection_state.return_value.value = "connected"
            
            await drone_manager.connect_drone("real_drone_001")
        
        # Get type information for both
        sim_type_info = drone_manager.get_drone_type_info("simulation_drone_001")
        real_type_info = drone_manager.get_drone_type_info("real_drone_001")
        
        # Verify required fields
        required_fields = ["drone_id", "name", "type", "is_connected", "connection_status"]
        for field in required_fields:
            assert field in sim_type_info, f"Simulation type info missing: {field}"
            assert field in real_type_info, f"Real type info missing: {field}"
        
        # Verify type-specific fields
        assert "drone_class" in sim_type_info
        assert "drone_class" in real_type_info
        assert "is_real_drone" in sim_type_info
        assert "is_real_drone" in real_type_info
        
        # Verify values are correct
        assert sim_type_info["is_real_drone"] == False
        assert real_type_info["is_real_drone"] == True
        assert sim_type_info["drone_class"] == "simulation"
        assert real_type_info["drone_class"] == "real"
        
        logger.info("✅ Drone type information consistency verified")
    
    @pytest.mark.asyncio
    async def test_concurrent_real_simulation_operations(self, drone_manager):
        """Test concurrent operations with both real and simulation drones"""
        
        # Connect both types simultaneously
        await drone_manager.connect_drone("simulation_drone_001")
        
        with patch.object(TelloEDUController, '__init__', return_value=None), \
             patch.object(TelloEDUController, 'takeoff', return_value=True), \
             patch.object(TelloEDUController, 'get_battery_level', return_value=85), \
             patch.object(TelloEDUController, 'get_current_position', return_value=(0, 0, 0)):
            
            await drone_manager.connect_drone("real_drone_001")
            
            # Perform concurrent operations
            sim_task = asyncio.create_task(drone_manager.takeoff_drone("simulation_drone_001"))
            real_task = asyncio.create_task(drone_manager.takeoff_drone("real_drone_001"))
            
            # Wait for both to complete
            sim_result, real_result = await asyncio.gather(sim_task, real_task)
            
            # Verify both operations succeeded
            assert sim_result.message is not None
            assert real_result.message is not None
            
            # Test concurrent status retrieval
            sim_status_task = asyncio.create_task(drone_manager.get_drone_status("simulation_drone_001"))
            real_status_task = asyncio.create_task(drone_manager.get_drone_status("real_drone_001"))
            
            sim_status, real_status = await asyncio.gather(sim_status_task, real_status_task)
            
            # Verify both statuses retrieved successfully
            assert sim_status.drone_id == "simulation_drone_001"
            assert real_status.drone_id == "real_drone_001"
        
        logger.info("✅ Concurrent real-simulation operations verified")


class TestAPIBackwardCompatibility:
    """Test backward compatibility of APIs with previous phases"""
    
    @pytest.fixture
    async def legacy_drone_manager(self):
        """Create DroneManager in legacy mode (Phase 1-5 compatibility)"""
        with patch('api_server.core.config_service.ConfigService') as mock_config_service:
            mock_config_service.return_value.get_all_config.return_value = {
                "global": {"space_bounds": [20.0, 20.0, 10.0]},
                "drones": []  # Empty - should fall back to defaults
            }
            
            manager = DroneManager()
            yield manager
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_legacy_api_compatibility(self, legacy_drone_manager):
        """Test that legacy API calls still work with Phase 6 system"""
        
        # Test getting available drones (should have defaults)
        drones = await legacy_drone_manager.get_available_drones()
        assert len(drones) > 0
        
        # Test connecting to first available drone
        first_drone = drones[0]
        connect_result = await legacy_drone_manager.connect_drone(first_drone.id)
        assert connect_result.message is not None
        
        # Test legacy status retrieval
        status = await legacy_drone_manager.get_drone_status(first_drone.id)
        assert status.drone_id == first_drone.id
        assert status.connection_status == "connected"
        
        # Test legacy control commands
        takeoff_result = await legacy_drone_manager.takeoff_drone(first_drone.id)
        assert takeoff_result.message is not None
        
        land_result = await legacy_drone_manager.land_drone(first_drone.id)
        assert land_result.message is not None
        
        logger.info("✅ Legacy API compatibility verified")
    
    @pytest.mark.asyncio
    async def test_phase5_dashboard_compatibility(self, legacy_drone_manager):
        """Test compatibility with Phase 5 dashboard functionality"""
        
        # Test getting available drones for dashboard
        drones = await legacy_drone_manager.get_available_drones()
        assert isinstance(drones, list)
        
        for drone in drones:
            # Test that drone objects have expected fields for dashboard
            assert hasattr(drone, 'id')
            assert hasattr(drone, 'name')
            assert hasattr(drone, 'type')
            assert hasattr(drone, 'status')
        
        # Test camera operations (Phase 3 compatibility)
        if drones:
            drone_id = drones[0].id
            await legacy_drone_manager.connect_drone(drone_id)
            
            # Test camera stream start/stop
            camera_start = await legacy_drone_manager.start_camera_stream(drone_id)
            assert camera_start.message is not None
            
            camera_stop = await legacy_drone_manager.stop_camera_stream(drone_id)
            assert camera_stop.message is not None
            
            # Test photo capture
            photo = await legacy_drone_manager.capture_photo(drone_id)
            assert photo.id is not None
        
        logger.info("✅ Phase 5 dashboard compatibility verified")


if __name__ == "__main__":
    # Run tests with asyncio
    import sys
    import subprocess
    
    # Check if pytest is available
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("pytest not available, running basic test...")
        # Basic test without pytest
        asyncio.run(basic_test())


async def basic_test():
    """Basic test without pytest"""
    print("Running basic real-simulation switching test...")
    
    # Create a simple test
    try:
        manager = DroneManager()
        drones = await manager.get_available_drones()
        print(f"✅ Found {len(drones)} configured drones")
        
        if drones:
            first_drone = drones[0]
            await manager.connect_drone(first_drone.id)
            status = await manager.get_drone_status(first_drone.id)
            print(f"✅ Connected to drone {first_drone.id}, status: {status.connection_status}")
            await manager.disconnect_drone(first_drone.id)
        
        await manager.shutdown()
        print("✅ Basic test completed successfully")
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        raise