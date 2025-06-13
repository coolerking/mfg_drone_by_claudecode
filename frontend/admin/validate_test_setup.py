#!/usr/bin/env python3
"""
Validate test setup for Admin Frontend
"""
import os
import sys
import importlib.util
import tempfile
import json
from pathlib import Path

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_required_packages():
    """Check if required packages can be imported"""
    packages = {
        'flask': 'Flask',
        'pytest': 'pytest',
        'requests': 'requests',
        'PIL': 'Pillow',
        'json': 'built-in'
    }
    
    all_ok = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} not found")
            all_ok = False
    
    return all_ok

def check_file_structure():
    """Check test file structure"""
    required_files = [
        'pytest.ini',
        'conftest.py', 
        'test_requirements.txt',
        'tests/__init__.py',
        'tests/unit/__init__.py',
        'tests/integration/__init__.py',
        'tests/fixtures/__init__.py',
        'tests/mocks/__init__.py',
        'tests/utils/__init__.py'
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_ok = False
    
    return all_ok

def check_main_app():
    """Check main app can be imported"""
    try:
        import main
        print("✅ main.py imports successfully")
        
        app = main.app
        print("✅ Flask app created")
        
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint works")
                return True
            else:
                print(f"❌ Health endpoint returned {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        return False

def test_mock_backend():
    """Test mock backend can start"""
    try:
        sys.path.append('tests/mocks')
        from backend_server import MockBackendServer
        
        # Create server on different port for testing
        server = MockBackendServer('localhost', 8999)
        server.start()
        
        import time
        time.sleep(0.5)
        
        import requests
        try:
            response = requests.get('http://localhost:8999/health', timeout=2)
            if response.status_code == 200:
                print("✅ Mock backend server works")
                success = True
            else:
                print(f"❌ Mock backend returned {response.status_code}")
                success = False
        except requests.RequestException as e:
            print(f"❌ Mock backend connection failed: {e}")
            success = False
        
        server.stop()
        return success
        
    except Exception as e:
        print(f"❌ Mock backend test failed: {e}")
        return False

def test_fixtures():
    """Test fixtures can be imported"""
    try:
        sys.path.append('tests/fixtures')
        import api_responses
        import mock_data
        
        # Test data generation
        drone_status = mock_data.generate_drone_status()
        if 'battery' in drone_status and 'height' in drone_status:
            print("✅ Mock data generation works")
        else:
            print("❌ Mock data generation failed")
            return False
        
        # Test API responses
        if hasattr(api_responses, 'SUCCESS_RESPONSE'):
            print("✅ API responses available")
        else:
            print("❌ API responses missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Fixtures test failed: {e}")
        return False

def test_pytest_config():
    """Test pytest configuration"""
    try:
        import pytest
        
        # Check if pytest.ini exists and is valid
        if os.path.exists('pytest.ini'):
            with open('pytest.ini', 'r') as f:
                content = f.read()
                if '[tool:pytest]' in content:
                    print("✅ pytest.ini configured")
                    return True
                else:
                    print("❌ pytest.ini invalid format")
                    return False
        else:
            print("❌ pytest.ini missing")
            return False
            
    except Exception as e:
        print(f"❌ pytest config test failed: {e}")
        return False

def create_test_image():
    """Create a test image to verify PIL works"""
    try:
        from PIL import Image
        import numpy as np
        
        # Create temporary test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(tmp.name)
            
            # Verify image can be opened
            with Image.open(tmp.name) as test_img:
                if test_img.size == (100, 100):
                    print("✅ Image creation/processing works")
                    success = True
                else:
                    print("❌ Image processing failed")
                    success = False
            
            # Cleanup
            os.unlink(tmp.name)
            return success
            
    except Exception as e:
        print(f"❌ Image test failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🔧 Validating Admin Frontend Test Setup")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("File Structure", check_file_structure),
        ("Main Application", check_main_app),
        ("Mock Backend", test_mock_backend),
        ("Test Fixtures", test_fixtures),
        ("Pytest Config", test_pytest_config),
        ("Image Processing", create_test_image)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\\n📋 {check_name}:")
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {e}")
            all_passed = False
    
    print("\\n" + "=" * 50)
    if all_passed:
        print("🎉 All validation checks passed!")
        print("\\nNext steps:")
        print("1. Install test dependencies: pip install -r test_requirements.txt")
        print("2. Run unit tests: python tests/test_runner.py --unit")
        print("3. Run integration tests: python tests/test_runner.py --integration")
        return 0
    else:
        print("❌ Some validation checks failed!")
        print("\\nPlease fix the issues above before running tests.")
        return 1

if __name__ == '__main__':
    sys.exit(main())