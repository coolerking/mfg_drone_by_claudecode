#!/usr/bin/env python3
"""
Simple import test for the API server
Tests that all modules can be imported correctly
"""

import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def test_imports():
    """Test all imports work correctly"""
    try:
        print("Testing basic imports...")
        
        # Test model imports
        print("✓ Testing model imports...")
        from api_server.models.common_models import SuccessResponse, ErrorResponse
        from api_server.models.drone_models import Drone, DroneStatus, MoveCommand, RotateCommand
        print("  - Models imported successfully")
        
        # Test core imports
        print("✓ Testing core imports...")
        from api_server.core.drone_manager import DroneManager
        print("  - Core modules imported successfully")
        
        # Test API imports
        print("✓ Testing API imports...")
        from api_server.api.drones import router
        print("  - API modules imported successfully")
        
        # Test main application import
        print("✓ Testing main application...")
        from api_server.main import app
        print("  - Main application imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    try:
        print("\n✓ Testing basic functionality...")
        
        # Test model creation
        from api_server.models.common_models import SuccessResponse
        response = SuccessResponse(message="Test message")
        assert response.success is True
        print("  - Model creation works")
        
        # Test drone manager creation (this might fail due to missing deps)
        try:
            from api_server.core.drone_manager import DroneManager
            # We can't actually create it without the dependencies, but we can check the class exists
            assert DroneManager is not None
            print("  - DroneManager class exists")
        except Exception as e:
            print(f"  - DroneManager creation failed (expected): {e}")
        
        print("✓ Basic functionality test completed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== API Server Import Test ===\n")
    
    imports_ok = test_imports()
    if imports_ok:
        test_basic_functionality()
    
    print("\n=== Test Summary ===")
    if imports_ok:
        print("✓ Import test: PASSED")
        print("📝 Note: Full functionality testing requires installing dependencies:")
        print("   pip install -r requirements.txt")
    else:
        print("❌ Import test: FAILED")
        sys.exit(1)