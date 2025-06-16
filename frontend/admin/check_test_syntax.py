#!/usr/bin/env python3
"""
Simple test syntax validation
"""
import ast
import sys
from pathlib import Path


def check_python_syntax(file_path):
    """Check if Python file has valid syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source, filename=str(file_path))
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Check syntax of all test files."""
    root_dir = Path(__file__).parent
    
    # Files to check
    test_files = [
        "conftest.py",
        "validate_tests.py", 
        "run_integration_tests.py",
        "tests/integration/test_mock_backend_integration.py",
        "tests/integration/test_websocket_integration.py",
        "tests/integration/test_file_upload_integration.py",
        "tests/integration/test_api_integration.py"
    ]
    
    print("🔍 Checking Python syntax for test files...")
    print("-" * 50)
    
    all_valid = True
    
    for file_path_str in test_files:
        file_path = root_dir / file_path_str
        
        if not file_path.exists():
            print(f"❌ {file_path_str} - File not found")
            all_valid = False
            continue
        
        valid, error = check_python_syntax(file_path)
        
        if valid:
            print(f"✅ {file_path_str} - Syntax OK")
        else:
            print(f"❌ {file_path_str} - {error}")
            all_valid = False
    
    print("-" * 50)
    if all_valid:
        print("🎉 All test files have valid syntax!")
        return True
    else:
        print("❌ Some test files have syntax errors!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)