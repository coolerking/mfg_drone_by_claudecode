#!/usr/bin/env python3
"""
Phase 4 Enhanced Vision Features Test Runner
Comprehensive testing of Phase 4 advanced camera and vision capabilities
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    import pytest
    from config.logging import setup_logging, get_logger
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Run Phase 4 tests"""
    # Setup logging
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    
    logger.info("Starting Phase 4 Enhanced Vision Features Tests...")
    
    # Test configuration
    test_args = [
        "tests/test_phase4_vision_features.py",
        "-v",
        "--tb=short",
        "--no-header",
        "--disable-warnings"
    ]
    
    # Add coverage if pytest-cov is available
    try:
        import pytest_cov
        test_args.extend([
            "--cov=src/core/phase4_vision_processor",
            "--cov=src/api/phase4_vision", 
            "--cov=src/models/phase4_vision_models",
            "--cov-report=term",
            "--cov-report=html:htmlcov/phase4"
        ])
        logger.info("Coverage reporting enabled")
    except ImportError:
        logger.warning("pytest-cov not available, running tests without coverage")
    
    # Run tests
    logger.info("Running Phase 4 tests...")
    exit_code = pytest.main(test_args)
    
    if exit_code == 0:
        logger.info("✅ All Phase 4 tests passed successfully!")
        print("\n" + "="*60)
        print("🎉 Phase 4 Enhanced Vision Features - ALL TESTS PASSED")
        print("="*60)
        print("\nPhase 4 Features Verified:")
        print("  ✅ Advanced Object Detection & Tracking")
        print("  ✅ Enhanced Camera Control")
        print("  ✅ Intelligent Learning Data Collection")
        print("  ✅ Natural Language Vision Processing")
        print("  ✅ Batch Command Optimization")
        print("  ✅ Comprehensive Vision Analytics")
        print("\nPhase 4 is ready for production use! 🚀")
    else:
        logger.error("❌ Some Phase 4 tests failed")
        print("\n" + "="*60)
        print("⚠️  Phase 4 Enhanced Vision Features - TESTS FAILED")
        print("="*60)
        print("\nPlease review the test output above and fix any issues.")
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)