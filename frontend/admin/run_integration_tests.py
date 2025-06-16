#!/usr/bin/env python3
"""
Integration Test Runner
フェーズ3結合テスト実行スクリプト
"""
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


class IntegrationTestRunner:
    """Integration test runner with comprehensive reporting."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.test_dir = self.root_dir / "tests"
        self.reports_dir = self.test_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_tests(self, test_type="all", verbose=False, coverage=False, html_report=False):
        """Run integration tests with specified options."""
        print(f"🚀 Starting Phase 3 Integration Tests...")
        print(f"   Test Type: {test_type}")
        print(f"   Verbose: {verbose}")
        print(f"   Coverage: {coverage}")
        print(f"   HTML Report: {html_report}")
        print("-" * 50)
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        # Add test paths based on type
        if test_type == "all":
            cmd.append("tests/integration/")
        elif test_type == "mock_backend":
            cmd.extend(["-m", "mock_backend"])
        elif test_type == "websocket":
            cmd.extend(["-m", "websocket"])
        elif test_type == "file_upload":
            cmd.extend(["-m", "file_upload"])
        elif test_type == "api_integration":
            cmd.extend(["-m", "api_integration"])
        else:
            cmd.append(f"tests/integration/test_{test_type}_integration.py")
        
        # Add verbosity
        if verbose:
            cmd.append("-v")
        
        # Add coverage
        if coverage:
            cmd.extend([
                "--cov=.",
                "--cov-report=term-missing",
                "--cov-report=xml:tests/reports/coverage.xml"
            ])
            if html_report:
                cmd.append("--cov-report=html:tests/reports/coverage")
        
        # Add HTML report
        if html_report:
            cmd.extend([
                "--html=tests/reports/integration_report.html",
                "--self-contained-html"
            ])
        
        # Add other options
        cmd.extend([
            "--strict-markers",
            "--tb=short"
        ])
        
        # Run tests
        start_time = time.time()
        try:
            result = subprocess.run(cmd, cwd=self.root_dir, capture_output=True, text=True)
            end_time = time.time()
            
            # Print results
            print("\n" + "=" * 50)
            print("TEST RESULTS")
            print("=" * 50)
            print(result.stdout)
            
            if result.stderr:
                print("\nERRORS/WARNINGS:")
                print("-" * 20)
                print(result.stderr)
            
            print(f"\nExecution Time: {end_time - start_time:.2f} seconds")
            print(f"Exit Code: {result.returncode}")
            
            # Generate summary
            self._generate_summary(result.stdout, result.returncode, end_time - start_time)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running tests: {str(e)}")
            return False
    
    def _generate_summary(self, stdout, exit_code, execution_time):
        """Generate test execution summary."""
        print("\n" + "=" * 50)
        print("EXECUTION SUMMARY")
        print("=" * 50)
        
        # Parse test results
        lines = stdout.split('\n')
        summary_line = None
        
        for line in lines:
            if "passed" in line or "failed" in line or "error" in line:
                if any(keyword in line for keyword in ["passed", "failed", "error", "skipped"]):
                    summary_line = line.strip()
                    break
        
        if summary_line:
            print(f"📊 Test Results: {summary_line}")
        
        print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        print(f"🏁 Exit Code: {exit_code}")
        
        if exit_code == 0:
            print("✅ All tests passed successfully!")
        else:
            print("❌ Some tests failed. Check the detailed output above.")
        
        # Report file locations
        print("\n📁 Reports generated:")
        if (self.reports_dir / "integration_report.html").exists():
            print(f"   HTML Report: {self.reports_dir / 'integration_report.html'}")
        if (self.reports_dir / "coverage.xml").exists():
            print(f"   Coverage XML: {self.reports_dir / 'coverage.xml'}")
        if (self.reports_dir / "coverage" / "index.html").exists():
            print(f"   Coverage HTML: {self.reports_dir / 'coverage' / 'index.html'}")
    
    def check_dependencies(self):
        """Check if all required dependencies are installed."""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            "pytest", "pytest-flask", "pytest-mock", "pytest-cov",
            "requests", "responses", "flask", "pillow"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print("❌ Missing required packages:")
            for package in missing_packages:
                print(f"   - {package}")
            print("\n💡 Install missing packages with:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
        
        print("✅ All dependencies are installed.")
        return True
    
    def list_available_tests(self):
        """List all available integration tests."""
        print("📋 Available Integration Tests:")
        print("-" * 30)
        
        test_files = list(self.test_dir.glob("integration/test_*.py"))
        
        for test_file in sorted(test_files):
            test_name = test_file.stem.replace("test_", "").replace("_integration", "")
            print(f"   - {test_name}")
            
            # Try to extract test methods
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    test_methods = [line.strip() for line in content.split('\n') 
                                  if line.strip().startswith('def test_')]
                    print(f"     ({len(test_methods)} test methods)")
            except Exception:
                pass
        
        print(f"\nTotal: {len(test_files)} test files")
    
    def validate_environment(self):
        """Validate test environment setup."""
        print("🔧 Validating test environment...")
        
        checks = []
        
        # Check test directory structure
        required_dirs = [
            self.test_dir,
            self.test_dir / "integration",
            self.reports_dir
        ]
        
        for dir_path in required_dirs:
            if dir_path.exists():
                checks.append(f"✅ {dir_path.name} directory exists")
            else:
                checks.append(f"❌ {dir_path.name} directory missing")
        
        # Check test files
        test_files = [
            "test_mock_backend_integration.py",
            "test_websocket_integration.py", 
            "test_file_upload_integration.py",
            "test_api_integration.py"
        ]
        
        for test_file in test_files:
            file_path = self.test_dir / "integration" / test_file
            if file_path.exists():
                checks.append(f"✅ {test_file} exists")
            else:
                checks.append(f"❌ {test_file} missing")
        
        # Check configuration files
        config_files = ["pytest.ini", "conftest.py"]
        for config_file in config_files:
            file_path = self.root_dir / config_file
            if file_path.exists():
                checks.append(f"✅ {config_file} exists")
            else:
                checks.append(f"❌ {config_file} missing")
        
        # Print results
        for check in checks:
            print(f"   {check}")
        
        failed_checks = [check for check in checks if "❌" in check]
        if failed_checks:
            print(f"\n❌ {len(failed_checks)} validation checks failed")
            return False
        
        print(f"\n✅ All {len(checks)} validation checks passed")
        return True


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Phase 3 Integration Test Runner")
    
    parser.add_argument(
        "--type", 
        choices=["all", "mock_backend", "websocket", "file_upload", "api_integration"],
        default="all",
        help="Type of integration tests to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML reports"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check dependencies only"
    )
    
    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="List available tests"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true", 
        help="Validate test environment"
    )
    
    args = parser.parse_args()
    
    runner = IntegrationTestRunner()
    
    # Handle special commands
    if args.check_deps:
        success = runner.check_dependencies()
        sys.exit(0 if success else 1)
    
    if args.list_tests:
        runner.list_available_tests()
        sys.exit(0)
    
    if args.validate:
        success = runner.validate_environment()
        sys.exit(0 if success else 1)
    
    # Check dependencies before running tests
    if not runner.check_dependencies():
        print("\n❌ Cannot run tests due to missing dependencies")
        sys.exit(1)
    
    # Validate environment
    if not runner.validate_environment():
        print("\n❌ Cannot run tests due to environment issues")
        sys.exit(1)
    
    # Run tests
    success = runner.run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage,
        html_report=args.html
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()