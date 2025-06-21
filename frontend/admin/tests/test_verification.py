"""
Test Structure Verification
Validates that all unit tests are properly structured and can be imported
"""

import sys
import os
import importlib.util

# Add the parent directory to sys.path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_test_imports():
    """Verify that all test files can be imported"""
    test_files = [
        'tests.test_drone_api_client',
        'tests.test_drone_api_client_advanced', 
        'tests.test_flask_routes',
        'tests.test_flask_routes_advanced'
    ]
    
    errors = []
    
    for test_module in test_files:
        try:
            spec = importlib.util.find_spec(test_module)
            if spec is None:
                errors.append(f"Module {test_module} not found")
            else:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ {test_module} - Import successful")
        except Exception as e:
            errors.append(f"Module {test_module} - Import failed: {e}")
            print(f"❌ {test_module} - Import failed: {e}")
    
    return errors

def verify_mock_structure():
    """Verify that mock structure is correct"""
    try:
        from tests.mocks.backend_mock import BackendAPIMock, create_mock_session, create_mock_requests
        print("✅ Backend mock imports successful")
        
        # Test mock functionality
        mock = BackendAPIMock()
        assert hasattr(mock, 'mock_request')
        assert hasattr(mock, 'set_failure_mode')
        print("✅ Backend mock structure valid")
        
        return []
    except Exception as e:
        error = f"Mock verification failed: {e}"
        print(f"❌ {error}")
        return [error]

def verify_main_module():
    """Verify that main module can be imported"""
    try:
        import main
        assert hasattr(main, 'DroneAPIClient')
        assert hasattr(main, 'app')
        print("✅ Main module imports successful")
        return []
    except Exception as e:
        error = f"Main module import failed: {e}"
        print(f"❌ {error}")
        return [error]

def count_test_functions():
    """Count test functions in each module"""
    test_counts = {}
    
    try:
        # Import test modules
        from tests import test_drone_api_client
        from tests import test_drone_api_client_advanced
        from tests import test_flask_routes
        from tests import test_flask_routes_advanced
        
        modules = {
            'test_drone_api_client': test_drone_api_client,
            'test_drone_api_client_advanced': test_drone_api_client_advanced,
            'test_flask_routes': test_flask_routes,
            'test_flask_routes_advanced': test_flask_routes_advanced
        }
        
        total_tests = 0
        
        for module_name, module in modules.items():
            count = 0
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, '__name__') and attr.__name__.startswith('Test'):
                    # Count methods in test class
                    class_methods = [method for method in dir(attr) if method.startswith('test_')]
                    count += len(class_methods)
            
            test_counts[module_name] = count
            total_tests += count
            print(f"📊 {module_name}: {count} test functions")
        
        print(f"📊 Total test functions: {total_tests}")
        return test_counts, total_tests
        
    except Exception as e:
        print(f"❌ Could not count test functions: {e}")
        return {}, 0

def main():
    """Main verification function"""
    print("🔍 Verifying Unit Test Structure")
    print("="*50)
    
    all_errors = []
    
    # Verify imports
    print("\n1. Verifying test imports...")
    errors = verify_test_imports()
    all_errors.extend(errors)
    
    # Verify main module
    print("\n2. Verifying main module...")
    errors = verify_main_module()
    all_errors.extend(errors)
    
    # Verify mock structure
    print("\n3. Verifying mock structure...")
    errors = verify_mock_structure()
    all_errors.extend(errors)
    
    # Count test functions
    print("\n4. Counting test functions...")
    test_counts, total_tests = count_test_functions()
    
    # Summary
    print("\n" + "="*50)
    print("📋 VERIFICATION SUMMARY")
    print("="*50)
    
    if all_errors:
        print("❌ Verification failed with errors:")
        for error in all_errors:
            print(f"   • {error}")
        return False
    else:
        print("✅ All verifications passed!")
        print(f"📊 Total test functions: {total_tests}")
        print("🚀 Unit tests are ready to run")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)