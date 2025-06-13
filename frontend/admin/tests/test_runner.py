"""
Test runner for Admin Frontend tests
"""
import os
import sys
import pytest
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if test dependencies are installed"""
    missing_deps = []
    
    required_packages = [
        'pytest',
        'requests',
        'flask',
        'pillow'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_deps.append(package)
    
    if missing_deps:
        print(f"Missing dependencies: {missing_deps}")
        print("Please install test dependencies:")
        print("pip install -r test_requirements.txt")
        return False
    
    return True

def run_unit_tests():
    """Run unit tests only"""
    print("Running unit tests...")
    
    args = [
        '-m', 'pytest',
        'tests/unit/',
        '-v',
        '--tb=short',
        '-m', 'unit'
    ]
    
    result = pytest.main(args)
    return result == 0

def run_mock_backend_tests():
    """Run integration tests with mock backend"""
    print("Running integration tests with mock backend...")
    
    args = [
        '-m', 'pytest', 
        'tests/integration/mock_backend/',
        '-v',
        '--tb=short',
        '-m', 'mock_backend'
    ]
    
    result = pytest.main(args)
    return result == 0

def run_all_safe_tests():
    """Run all tests that don't require hardware"""
    print("Running all safe tests (no hardware required)...")
    
    args = [
        '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '-m', 'not requires_hardware'
    ]
    
    result = pytest.main(args)
    return result == 0

def run_coverage_report():
    """Run tests with coverage report"""
    print("Running tests with coverage...")
    
    args = [
        '-m', 'pytest',
        'tests/',
        '--cov=.',
        '--cov-report=html',
        '--cov-report=term-missing',
        '-m', 'not requires_hardware'
    ]
    
    result = pytest.main(args)
    
    if result == 0:
        print("\\nCoverage report generated in htmlcov/index.html")
    
    return result == 0

def validate_test_structure():
    """Validate test directory structure"""
    print("Validating test structure...")
    
    required_dirs = [
        'tests',
        'tests/unit',
        'tests/integration',
        'tests/integration/mock_backend',
        'tests/integration/real_backend',
        'tests/ui',
        'tests/fixtures',
        'tests/mocks',
        'tests/utils'
    ]
    
    required_files = [
        'pytest.ini',
        'conftest.py',
        'test_requirements.txt',
        'tests/__init__.py',
        'tests/fixtures/api_responses.py',
        'tests/mocks/backend_server.py'
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            missing_dirs.append(dir_path)
    
    for file_path in required_files:
        if not os.path.isfile(file_path):
            missing_files.append(file_path)
    
    if missing_dirs or missing_files:
        print("Test structure validation failed!")
        if missing_dirs:
            print(f"Missing directories: {missing_dirs}")
        if missing_files:
            print(f"Missing files: {missing_files}")
        return False
    
    print("Test structure validation passed!")
    return True

def main():
    """Main test runner"""
    print("Admin Frontend Test Runner")
    print("=" * 40)
    
    if not validate_test_structure():
        return 1
    
    if not check_dependencies():
        return 1
    
    # Change to admin directory
    admin_dir = Path(__file__).parent.parent
    os.chdir(admin_dir)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Run Admin Frontend tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--all', action='store_true', help='Run all safe tests')
    
    args = parser.parse_args()
    
    success = True
    
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_mock_backend_tests()
    elif args.coverage:
        success = run_coverage_report()
    elif args.all:
        success = run_all_safe_tests()
    else:
        # Default: run unit tests then mock backend tests
        print("Running default test suite...")
        success = run_unit_tests()
        if success:
            success = run_mock_backend_tests()
    
    if success:
        print("\\n✅ All tests passed!")
        return 0
    else:
        print("\\n❌ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())