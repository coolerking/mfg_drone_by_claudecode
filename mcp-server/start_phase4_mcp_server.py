#!/usr/bin/env python3
"""
Phase 4 Enhanced MCP Server Startup Script
Advanced camera and vision features with OpenCV integration
"""

import argparse
import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    import uvicorn
    from config.settings import settings
    from config.logging import setup_logging, get_logger
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Phase 4 Enhanced MCP Server - Advanced Camera & Vision Features"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default=settings.host,
        help=f"Host to bind to (default: {settings.host})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port + 1,  # Use different port for Phase 4
        help=f"Port to bind to (default: {settings.port + 1})"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.debug,
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["debug", "info", "warning", "error"],
        default=settings.log_level.lower(),
        help=f"Log level (default: {settings.log_level.lower()})"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--enhanced",
        action="store_true",
        default=True,
        help="Enable Phase 4 enhanced features (default: True)"
    )
    
    parser.add_argument(
        "--vision-only",
        action="store_true",
        help="Run only vision-related endpoints"
    )
    
    parser.add_argument(
        "--config-check",
        action="store_true",
        help="Check configuration and exit"
    )
    
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with mock services"
    )
    
    return parser.parse_args()


def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic",
        "numpy",
        "opencv-python"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Error: Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_configuration(args):
    """Check and display configuration"""
    print("=== Phase 4 Enhanced MCP Server Configuration ===")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Log Level: {args.log_level}")
    print(f"Reload: {args.reload}")
    print(f"Workers: {args.workers}")
    print(f"Enhanced Features: {args.enhanced}")
    print(f"Vision Only: {args.vision_only}")
    print(f"Test Mode: {args.test_mode}")
    print()
    
    print("=== Environment Settings ===")
    print(f"Backend API URL: {settings.backend_api_url}")
    print(f"Backend API Timeout: {settings.backend_api_timeout}")
    print(f"Debug Mode: {settings.debug}")
    print(f"CORS Origins: {settings.cors_origins}")
    print()
    
    # Check backend connectivity
    try:
        import httpx
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{settings.backend_api_url}/health")
            if response.status_code == 200:
                print("✅ Backend API is accessible")
            else:
                print(f"⚠️  Backend API returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend API is not accessible: {str(e)}")
    
    print()


def setup_environment(args):
    """Setup environment for Phase 4 server"""
    # Setup logging
    setup_logging(
        level=args.log_level.upper(),
        format_type="detailed" if args.log_level == "debug" else "standard"
    )
    
    logger = get_logger(__name__)
    
    # Set environment variables for Phase 4
    os.environ["MCP_PHASE"] = "4"
    os.environ["MCP_ENHANCED"] = str(args.enhanced)
    os.environ["MCP_VISION_ONLY"] = str(args.vision_only)
    os.environ["MCP_TEST_MODE"] = str(args.test_mode)
    
    logger.info("Phase 4 Enhanced MCP Server environment configured")
    
    return logger


async def health_check():
    """Perform startup health check"""
    logger = get_logger(__name__)
    
    try:
        # Import services to check initialization
        from src.core.enhanced_nlp_engine import EnhancedNLPEngine
        from src.core.backend_client import BackendClient
        from src.core.phase4_vision_processor import Phase4VisionProcessor
        
        logger.info("✅ All Phase 4 services imported successfully")
        
        # Test backend connectivity
        async with BackendClient() as client:
            await client.health_check()
            logger.info("✅ Backend connectivity verified")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return False


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Check configuration and exit if requested
    if args.config_check:
        check_configuration(args)
        return
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    logger = setup_environment(args)
    
    try:
        logger.info("Starting Phase 4 Enhanced MCP Server...")
        logger.info(f"Phase 4 Features: Advanced Camera & Vision Processing")
        logger.info(f"Server will be available at: http://{args.host}:{args.port}")
        
        # Perform health check
        health_ok = asyncio.run(health_check())
        if not health_ok:
            logger.warning("Health check failed, but continuing startup...")
        
        # Configure uvicorn
        uvicorn_config = {
            "app": "src.phase4_main:app",
            "host": args.host,
            "port": args.port,
            "log_level": args.log_level,
            "reload": args.reload,
            "workers": args.workers if not args.reload else 1,
            "access_log": args.log_level == "debug",
        }
        
        # Add SSL configuration if available
        ssl_keyfile = os.environ.get("SSL_KEYFILE")
        ssl_certfile = os.environ.get("SSL_CERTFILE")
        
        if ssl_keyfile and ssl_certfile:
            uvicorn_config.update({
                "ssl_keyfile": ssl_keyfile,
                "ssl_certfile": ssl_certfile
            })
            logger.info("SSL configuration enabled")
        
        # Start server
        logger.info("Phase 4 Enhanced MCP Server startup complete")
        uvicorn.run(**uvicorn_config)
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Phase 4 Enhanced MCP Server shutdown complete")


if __name__ == "__main__":
    main()