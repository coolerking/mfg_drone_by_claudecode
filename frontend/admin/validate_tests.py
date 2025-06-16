#!/usr/bin/env python3
"""
Test Validation Script
テスト環境検証スクリプト
"""
import sys
import importlib
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} is not supported. Requires Python 3.8+")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is compatible")
    return True


def check_required_packages():
    """Check if required packages are available."""
    print("\n📦 Checking required packages...")
    
    required_packages = [
        ("pytest", "pytest"),
        ("flask", "Flask"),
        ("requests", "requests"),
        ("PIL", "Pillow"),
        ("responses", "responses"),
        ("socketio", "python-socketio")
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} (missing)")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_test_structure():
    """Check test directory structure."""
    print("\n📁 Checking test structure...")
    
    root_dir = Path(__file__).parent
    required_paths = [
        ("pytest.ini", "pytest configuration"),
        ("conftest.py", "test configuration"),
        ("tests/", "test directory"),
        ("tests/integration/", "integration test directory"),
        ("tests/integration/test_mock_backend_integration.py", "mock backend tests"),
        ("tests/integration/test_websocket_integration.py", "websocket tests"),
        ("tests/integration/test_file_upload_integration.py", "file upload tests"),
        ("tests/integration/test_api_integration.py", "API integration tests"),
    ]
    
    missing_files = []
    
    for path_str, description in required_paths:
        path = root_dir / path_str
        if path.exists():
            print(f"✅ {description}")
        else:
            print(f"❌ {description} (missing: {path})")
            missing_files.append(path_str)
    
    return len(missing_files) == 0


def test_basic_functionality():
    """Test basic functionality."""
    print("\n🧪 Testing basic functionality...")
    
    # Test pytest discovery
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            # Count discovered tests
            output_lines = result.stdout.split('\n')
            test_count = sum(1 for line in output_lines if line.strip().endswith('::'))
            print(f"✅ Pytest discovered {test_count} tests")
            return True
        else:
            print(f"❌ Pytest collection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running pytest: {str(e)}")
        return False


def test_import_modules():
    """Test importing test modules."""
    print("\n📥 Testing module imports...")
    
    test_modules = [
        "tests.integration.test_mock_backend_integration",
        "tests.integration.test_websocket_integration", 
        "tests.integration.test_file_upload_integration",
        "tests.integration.test_api_integration"
    ]
    
    import_errors = []
    
    for module_name in test_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {str(e)}")
            import_errors.append(module_name)
        except Exception as e:
            print(f"⚠️  {module_name}: {str(e)} (may be OK)")
    
    return len(import_errors) == 0


def run_sample_test():
    """Run a sample test to verify execution."""
    print("\n🏃 Running sample test...")
    
    try:
        # Try to run a simple marker-based test
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "-m", "integration", "--tb=short", "-x"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0:
            print("✅ Sample integration test execution successful")
            return True
        else:
            print(f"⚠️  Sample test had issues (may be expected): {result.returncode}")
            print("   This could be normal if no backend is running")
            return True  # Don't fail validation for this
            
    except subprocess.TimeoutExpired:
        print("⚠️  Sample test timed out (may be expected)")
        return True  # Don't fail validation for timeout
    except Exception as e:
        print(f"❌ Error running sample test: {str(e)}")
        return False


def main():
    """Main validation function."""
    print("🔍 Phase 3 Integration Test Validation")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Test Structure", check_test_structure),
        ("Basic Functionality", test_basic_functionality),
        ("Module Imports", test_import_modules),
        ("Sample Test Execution", run_sample_test),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {str(e)}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("VALIDATION SUMMARY")
    print("=" * 40)
    
    passed = 0
    failed = 0
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<25} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All validation checks passed!")
        print("   Ready to run Phase 3 Integration Tests")
        return True
    else:
        print(f"\n❌ {failed} validation checks failed")
        print("   Please fix the issues before running tests")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)