#!/usr/bin/env python3
"""
Startup script for MCP Server
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Add config to Python path
config_path = Path(__file__).parent / "config"
sys.path.insert(0, str(config_path))

from config.settings import settings
from config.logging import setup_logging, get_logger


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Start MCP Server")
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host to bind to (default: {settings.host})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port to bind to (default: {settings.port})"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.debug,
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        default=settings.log_level,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Log level (default: {settings.log_level})"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(log_level=args.log_level)
    logger = get_logger(__name__)
    
    logger.info("Starting MCP Server")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Debug mode: {args.reload}")
    logger.info(f"Backend API URL: {settings.backend_api_url}")
    
    try:
        uvicorn.run(
            "src.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()