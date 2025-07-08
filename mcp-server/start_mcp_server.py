#!/usr/bin/env python3
"""
Startup script for MCP Server with Phase 2 Enhanced Features
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
    """Main startup function"""
    parser = argparse.ArgumentParser(
        description="MCP Server Startup Script - Choose Phase 1 or Phase 2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_mcp_server.py                    # Start original Phase 1 server
  python start_mcp_server.py --enhanced         # Start enhanced Phase 2 server
  python start_mcp_server.py --port 8002        # Start on custom port
        """
    )
    
    parser.add_argument(
        "--enhanced", "-e",
        action="store_true",
        help="Start enhanced Phase 2 server with advanced features"
    )
    
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host to bind to (default: {settings.host})"
    )
    
    parser.add_argument(
        "--port", "-p",
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
    
    # Determine which app to run
    if args.enhanced:
        app_module = "src.enhanced_main:app"
        server_type = "Enhanced MCP Server (Phase 2)"
        features = [
            "✨ Advanced Natural Language Processing",
            "🧠 Context-aware Command Understanding", 
            "🚀 Intelligent Batch Processing",
            "📊 Dependency Analysis & Optimization",
            "🔄 Smart Error Recovery",
            "📈 Execution Analytics"
        ]
    else:
        app_module = "src.main:app"
        server_type = "Original MCP Server (Phase 1)"
        features = [
            "📝 Basic Natural Language Processing",
            "🎯 Command Routing",
            "📦 Simple Batch Processing", 
            "🌐 Complete API Implementation"
        ]
    
    logger.info(f"Starting {server_type}")
    logger.info("Features:")
    for feature in features:
        logger.info(f"  {feature}")
    
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Debug mode: {args.reload}")
    logger.info(f"Backend API URL: {settings.backend_api_url}")
    logger.info(f"Server will be available at: http://{args.host}:{args.port}")
    logger.info(f"API documentation: http://{args.host}:{args.port}/docs")
    logger.info("-" * 50)
    
    try:
        uvicorn.run(
            app_module,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()