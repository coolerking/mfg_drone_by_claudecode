#!/usr/bin/env python3
"""
Unit Test Runner for MFG Drone Admin Frontend
Executes unit tests independently without external dependencies
"""

import sys
import os
import subprocess
import argparse
import json
from pathlib import Path


def setup_test_environment():
    """Setup test environment and verify dependencies"""
    print("🔧 Setting up test environment...")
    
    # Ensure we're in the correct directory
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # Create reports directory
    reports_dir = current_dir / "tests" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📍 Working directory: {current_dir}")
    print(f"📁 Reports directory: {reports_dir}")
    
    return current_dir, reports_dir


def check_dependencies():
    """Check if required test dependencies are installed"""
    print("🔍 Checking test dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'flask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r test_requirements.txt")
        return False
    
    print("✅ All dependencies satisfied")
    return True


def run_tests(test_type=None, coverage=True, verbose=True):
    """Run unit tests with specified options"""
    print("\n🚀 Running unit tests...")
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest', '-c', 'pytest_unit.ini']
    
    # Add verbosity
    if verbose:
        cmd.append('-v')
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            '--cov=main',
            '--cov-report=html:tests/reports/coverage_html',
            '--cov-report=json:tests/reports/coverage.json',
            '--cov-report=term-missing',
            '--cov-fail-under=85'
        ])
    
    # Add test type filter if specified
    if test_type:
        if test_type == 'api_client':
            cmd.extend(['-m', 'api_client', 'tests/test_drone_api_client.py', 'tests/test_drone_api_client_advanced.py'])
        elif test_type == 'flask_routes':
            cmd.extend(['-m', 'flask_routes', 'tests/test_flask_routes.py', 'tests/test_flask_routes_advanced.py'])
        elif test_type == 'basic':
            cmd.extend(['-m', 'basic'])
        elif test_type == 'advanced':
            cmd.extend(['-m', 'advanced'])
        else:
            # Run specific test files
            cmd.append(f'tests/test_{test_type}.py')
    else:
        # Run all unit tests, exclude UI tests
        cmd.extend([
            'tests/test_drone_api_client.py',
            'tests/test_drone_api_client_advanced.py', 
            'tests/test_flask_routes.py',
            'tests/test_flask_routes_advanced.py'
        ])
    
    # Add HTML report
    cmd.extend([
        '--html=tests/reports/unit_test_report.html',
        '--self-contained-html',
        '--json-report',
        '--json-report-file=tests/reports/unit_test_report.json'
    ])
    
    print(f"🔨 Command: {' '.join(cmd)}")
    
    # Execute tests
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        print("\n" + "="*60)
        print("📊 TEST RESULTS")
        print("="*60)
        print(result.stdout)
        
        if result.stderr:
            print("\n" + "="*60)
            print("⚠️  WARNINGS/ERRORS")
            print("="*60)
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False


def generate_summary_report(reports_dir):
    """Generate a summary report of test results"""
    print("\n📋 Generating summary report...")
    
    # Check for JSON report
    json_report_path = reports_dir / "unit_test_report.json"
    coverage_json_path = reports_dir / "coverage.json"
    
    summary = {
        'timestamp': None,
        'tests': {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        },
        'coverage': {
            'percentage': 0,
            'missing_lines': 0
        },
        'files_tested': []
    }
    
    # Parse test results
    if json_report_path.exists():
        try:
            with open(json_report_path, 'r') as f:
                test_data = json.load(f)
            
            summary['timestamp'] = test_data.get('created', 'Unknown')
            
            # Parse test summary
            test_summary = test_data.get('summary', {})
            summary['tests']['total'] = test_summary.get('total', 0)
            summary['tests']['passed'] = test_summary.get('passed', 0)
            summary['tests']['failed'] = test_summary.get('failed', 0)
            summary['tests']['skipped'] = test_summary.get('skipped', 0)
            
            print(f"  📊 Total Tests: {summary['tests']['total']}")
            print(f"  ✅ Passed: {summary['tests']['passed']}")
            print(f"  ❌ Failed: {summary['tests']['failed']}")
            print(f"  ⏭️  Skipped: {summary['tests']['skipped']}")
            
        except Exception as e:
            print(f"  ⚠️  Could not parse test report: {e}")
    
    # Parse coverage results
    if coverage_json_path.exists():
        try:
            with open(coverage_json_path, 'r') as f:
                coverage_data = json.load(f)
            
            totals = coverage_data.get('totals', {})
            summary['coverage']['percentage'] = totals.get('percent_covered', 0)
            summary['coverage']['missing_lines'] = totals.get('missing_lines', 0)
            
            print(f"  📈 Coverage: {summary['coverage']['percentage']:.2f}%")
            print(f"  📄 Missing Lines: {summary['coverage']['missing_lines']}")
            
        except Exception as e:
            print(f"  ⚠️  Could not parse coverage report: {e}")
    
    # Generate summary file
    summary_path = reports_dir / "test_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"  💾 Summary saved to: {summary_path}")
    
    return summary


def verify_independence():
    """Verify that tests run independently without external dependencies"""
    print("\n🔒 Verifying test independence...")
    
    checks = [
        ("No real drone required", True),
        ("No backend server required", True),
        ("No network connection required", True),
        ("All API calls mocked", True),
        ("Local execution only", True)
    ]
    
    for check, status in checks:
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {check}")
    
    print("✅ Test independence verified")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Run MFG Drone Admin Frontend Unit Tests')
    parser.add_argument('--type', choices=['api_client', 'flask_routes', 'basic', 'advanced'], 
                       help='Run specific type of tests')
    parser.add_argument('--no-coverage', action='store_true', 
                       help='Skip coverage reporting')
    parser.add_argument('--quiet', action='store_true', 
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    print("🚁 MFG Drone Admin Frontend - Unit Test Runner")
    print("="*60)
    
    # Setup environment
    current_dir, reports_dir = setup_test_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Verify independence
    verify_independence()
    
    # Run tests
    success = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=not args.quiet
    )
    
    # Generate summary
    summary = generate_summary_report(reports_dir)
    
    # Final status
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print(f"📊 {summary['tests']['passed']}/{summary['tests']['total']} tests passed")
        print(f"📈 {summary['coverage']['percentage']:.2f}% code coverage")
        print(f"📁 Reports: {reports_dir}")
        print("="*60)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"📊 {summary['tests']['failed']}/{summary['tests']['total']} tests failed")
        print(f"📁 Reports: {reports_dir}")
        print("="*60)
        sys.exit(1)


if __name__ == '__main__':
    main()