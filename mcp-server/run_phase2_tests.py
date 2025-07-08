#!/usr/bin/env python3
"""
Test runner for MCP Server Phase 2 Enhanced Features
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests based on specified type"""
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Determine which tests to run
    if test_type == "all":
        test_paths = [
            "tests/test_enhanced_nlp_engine.py",
            "tests/test_enhanced_command_router.py", 
            "tests/test_batch_processor.py"
        ]
    elif test_type == "nlp":
        test_paths = ["tests/test_enhanced_nlp_engine.py"]
    elif test_type == "router":
        test_paths = ["tests/test_enhanced_command_router.py"]
    elif test_type == "batch":
        test_paths = ["tests/test_batch_processor.py"]
    elif test_type == "integration":
        test_paths = ["tests/test_api.py"]  # If exists
    else:
        print(f"Unknown test type: {test_type}")
        return False
    
    # Add test paths to command
    cmd.extend(test_paths)
    
    print("Running Phase 2 Enhanced MCP Server Tests")
    print("=" * 50)
    print(f"Test type: {test_type}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        # Run the tests
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    
    except FileNotFoundError:
        print("❌ pytest not found. Please install dependencies:")
        print("pip install -r requirements.txt")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import pytest
        import pytest_asyncio
        print("✅ Test dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing test dependency: {e}")
        print("Please install dependencies:")
        print("pip install -r requirements.txt")
        return False


def run_specific_test(test_file, test_name=None, verbose=False):
    """Run a specific test file or test function"""
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if test_name:
        cmd.append(f"{test_file}::{test_name}")
    else:
        cmd.append(test_file)
    
    print(f"Running specific test: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Test completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test failed with exit code {e.returncode}")
        return False


def generate_coverage_report():
    """Generate detailed coverage report"""
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    cmd = [
        "python", "-m", "pytest",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "tests/"
    ]
    
    print("Generating coverage report...")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Coverage report generated!")
        print("📊 HTML report available at: htmlcov/index.html")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Coverage generation failed with exit code {e.returncode}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test runner for MCP Server Phase 2 Enhanced Features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_phase2_tests.py                    # Run all tests
  python run_phase2_tests.py --type nlp         # Run only NLP tests
  python run_phase2_tests.py --coverage         # Run with coverage
  python run_phase2_tests.py --specific tests/test_enhanced_nlp_engine.py::TestEnhancedNLPEngine::test_basic_command_parsing
        """
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["all", "nlp", "router", "batch", "integration"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run tests with coverage report"
    )
    
    parser.add_argument(
        "--specific", "-s",
        help="Run a specific test file or test function (e.g., tests/test_nlp.py::test_function)"
    )
    
    parser.add_argument(
        "--coverage-only",
        action="store_true",
        help="Generate coverage report only"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check if test dependencies are installed"
    )
    
    args = parser.parse_args()
    
    # Check dependencies first
    if not check_dependencies():
        return False
    
    if args.check_deps:
        return True
    
    if args.coverage_only:
        return generate_coverage_report()
    
    if args.specific:
        # Parse specific test
        if "::" in args.specific:
            test_file, test_name = args.specific.split("::", 1)
        else:
            test_file, test_name = args.specific, None
        
        return run_specific_test(test_file, test_name, args.verbose)
    
    # Run regular tests
    return run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage
    )


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)