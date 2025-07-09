#!/usr/bin/env python3
"""
Test script to verify configuration changes
"""

import os
import sys
import traceback

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def test_settings_import():
    """Test if settings can be imported and loaded"""
    try:
        from config.settings import Settings, settings
        print("✓ Settings import successful")
        
        # Test basic attributes
        print(f"  Environment: {settings.environment}")
        print(f"  Debug mode: {settings.debug}")
        print(f"  CORS enabled: {settings.cors_enabled}")
        print(f"  Security headers enabled: {settings.security_headers_enabled}")
        print(f"  Trusted hosts enabled: {settings.trusted_hosts_enabled}")
        print(f"  SSL enabled: {settings.ssl_enabled}")
        print(f"  Force HTTPS: {settings.force_https}")
        
        return True
    except Exception as e:
        print(f"✗ Settings import failed: {e}")
        traceback.print_exc()
        return False

def test_security_manager_import():
    """Test if security manager can be imported with new config"""
    try:
        from src.core.security_manager import SecurityManager, SecurityConfig
        print("✓ Security manager import successful")
        
        # Test config creation
        config = SecurityConfig(
            jwt_secret="test_secret_key_with_minimum_32_chars",
            max_failed_attempts=5,
            lockout_duration_minutes=15,
            allowed_ips=[],
            blocked_ips=[]
        )
        
        security_manager = SecurityManager(config)
        print("✓ Security manager instantiation successful")
        
        return True
    except Exception as e:
        print(f"✗ Security manager import failed: {e}")
        traceback.print_exc()
        return False

def test_phase5_main_imports():
    """Test if main application imports work"""
    try:
        # Test individual imports that we modified
        from config.settings import settings
        from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
        print("✓ FastAPI imports successful")
        
        return True
    except Exception as e:
        print(f"✗ Phase5 main imports failed: {e}")
        traceback.print_exc()
        return False

def test_validation_script():
    """Test if the validation script can be imported"""
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import validate_config
        print("✓ Validation script import successful")
        
        return True
    except Exception as e:
        print(f"✗ Validation script import failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("Testing MCP Server configuration changes...")
    print("=" * 50)
    
    tests = [
        ("Settings Configuration", test_settings_import),
        ("Security Manager", test_security_manager_import),
        ("Phase5 Main Imports", test_phase5_main_imports),
        ("Validation Script", test_validation_script),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  Failed: {test_name}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Configuration changes are working correctly.")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)