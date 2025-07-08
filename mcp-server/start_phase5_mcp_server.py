#!/usr/bin/env python3
"""
Phase 5: Enhanced MCP Server Startup Script
Features:
- Enhanced security configuration
- Monitoring service initialization
- Health checks and validation
- Production-ready deployment options
"""

import os
import sys
import asyncio
import argparse
import signal
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import uvicorn
import logging
from datetime import datetime

# Import configuration
from config.settings import settings
from config.logging import setup_logging, get_logger

# Import Phase 5 services
from core.security_manager import SecurityManager, SecurityConfig, SecurityLevel
from core.monitoring_service import MonitoringService

# Setup logging
setup_logging()
logger = get_logger(__name__)


class Phase5ServerManager:
    """Enhanced server manager for Phase 5 MCP Server"""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.config_override = config_override or {}
        self.security_manager = None
        self.monitoring_service = None
        self.server_process = None
        self.running = False
        
    def setup_security(self) -> SecurityManager:
        """Setup security manager with configuration"""
        jwt_secret = os.getenv("JWT_SECRET")
        if not jwt_secret:
            raise ValueError(
                "JWT_SECRET environment variable is required for security. "
                "Please set a strong, randomly generated secret of at least 32 characters."
            )
        
        security_config = SecurityConfig(
            jwt_secret=jwt_secret,
            jwt_expiry_minutes=int(os.getenv("JWT_EXPIRY_MINUTES", "60")),
            max_failed_attempts=int(os.getenv("MAX_FAILED_ATTEMPTS", "5")),
            lockout_duration_minutes=int(os.getenv("LOCKOUT_DURATION", "15")),
            rate_limiting=None,  # Will use default
            allowed_ips=os.getenv("ALLOWED_IPS", "").split(",") if os.getenv("ALLOWED_IPS") else [],
            blocked_ips=os.getenv("BLOCKED_IPS", "").split(",") if os.getenv("BLOCKED_IPS") else [],
            enable_audit_logging=os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
        )
        
        self.security_manager = SecurityManager(security_config)
        logger.info("Security manager configured")
        
        return self.security_manager
    
    def setup_monitoring(self) -> MonitoringService:
        """Setup monitoring service"""
        self.monitoring_service = MonitoringService()
        
        # Start monitoring if enabled
        if os.getenv("ENABLE_MONITORING", "true").lower() == "true":
            monitoring_interval = int(os.getenv("MONITORING_INTERVAL", "30"))
            self.monitoring_service.start_monitoring(interval_seconds=monitoring_interval)
            logger.info(f"Monitoring service started with {monitoring_interval}s interval")
        
        return self.monitoring_service
    
    def validate_environment(self) -> bool:
        """Validate environment configuration"""
        required_vars = ["JWT_SECRET"]
        missing_vars = []
        
        # Check critical environment variables
        if os.getenv("ENVIRONMENT") == "production":
            required_vars.extend([
                "ADMIN_USERNAME", "ADMIN_PASSWORD",
                "OPERATOR_USERNAME", "OPERATOR_PASSWORD"
            ])
        else:
            # For development, we still need at least one user
            auth_vars = [
                ("ADMIN_USERNAME", "ADMIN_PASSWORD"),
                ("OPERATOR_USERNAME", "OPERATOR_PASSWORD"),
                ("READONLY_USERNAME", "READONLY_PASSWORD")
            ]
            has_user = any(os.getenv(user) and os.getenv(pwd) for user, pwd in auth_vars)
            if not has_user:
                logger.error(
                    "At least one user must be configured. Set username/password pairs: "
                    "ADMIN_USERNAME/ADMIN_PASSWORD, OPERATOR_USERNAME/OPERATOR_PASSWORD, or "
                    "READONLY_USERNAME/READONLY_PASSWORD"
                )
                return False
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
        
        # Validate JWT secret strength
        jwt_secret = os.getenv("JWT_SECRET", "")
        if len(jwt_secret) < 32:
            logger.error("JWT secret must be at least 32 characters long for security")
            return False
        
        # Check for weak JWT secrets
        weak_secrets = [
            "your-secret-key",
            "your-secure-secret-key", 
            "your-secure-secret-key-change-in-production",
            "secret",
            "password",
            "admin",
            "test"
        ]
        if jwt_secret.lower() in [s.lower() for s in weak_secrets]:
            logger.error("JWT secret cannot be a default or weak value. Use a strong, randomly generated secret.")
            return False
        
        # Validate backend API URL
        if not settings.backend_api_url:
            logger.error("Backend API URL not configured")
            return False
        
        return True
    
    def create_default_users(self):
        """Create default users for initial setup"""
        if not self.security_manager:
            return
        
        # Create admin user API key
        admin_key = self.security_manager.generate_api_key("admin", SecurityLevel.ADMIN)
        logger.info("Generated admin API key")
        
        # Create operator user API key
        operator_key = self.security_manager.generate_api_key("operator", SecurityLevel.OPERATOR)
        logger.info("Generated operator API key")
        
        # Create read-only user API key
        readonly_key = self.security_manager.generate_api_key("readonly", SecurityLevel.READ_ONLY)
        logger.info("Generated read-only API key")
        
        # Save keys to file for reference (in development only)
        if os.getenv("ENVIRONMENT") != "production":
            keys_file = Path("api_keys.json")
            keys_data = {
                "admin": admin_key,
                "operator": operator_key,
                "readonly": readonly_key,
                "generated_at": datetime.utcnow().isoformat(),
                "note": "These keys are for development only. In production, manage keys securely."
            }
            
            try:
                with open(keys_file, "w") as f:
                    json.dump(keys_data, f, indent=2)
                logger.info(f"API keys saved to {keys_file}")
            except Exception as e:
                logger.error(f"Failed to save API keys: {str(e)}")
    
    def run_health_checks(self) -> bool:
        """Run comprehensive health checks"""
        logger.info("Running system health checks...")
        
        checks_passed = 0
        total_checks = 4
        
        # Check 1: Python version
        if sys.version_info >= (3, 8):
            logger.info("✓ Python version check passed")
            checks_passed += 1
        else:
            logger.error("✗ Python 3.8+ required")
        
        # Check 2: Required packages
        try:
            import fastapi
            import uvicorn
            import psutil
            import jwt
            logger.info("✓ Required packages check passed")
            checks_passed += 1
        except ImportError as e:
            logger.error(f"✗ Missing required package: {str(e)}")
        
        # Check 3: Configuration validation
        if self.validate_environment():
            logger.info("✓ Environment configuration check passed")
            checks_passed += 1
        else:
            logger.error("✗ Environment configuration check failed")
        
        # Check 4: File system permissions
        try:
            test_file = Path("test_write.tmp")
            test_file.write_text("test")
            test_file.unlink()
            logger.info("✓ File system permissions check passed")
            checks_passed += 1
        except Exception as e:
            logger.error(f"✗ File system permissions check failed: {str(e)}")
        
        success_rate = (checks_passed / total_checks) * 100
        logger.info(f"Health checks completed: {checks_passed}/{total_checks} passed ({success_rate:.1f}%)")
        
        return checks_passed == total_checks
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.shutdown()
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def start_server(self, host: str = None, port: int = None, workers: int = 1, 
                    reload: bool = False, ssl_keyfile: str = None, ssl_certfile: str = None):
        """Start the Phase 5 MCP server"""
        # Use provided values or fall back to settings
        host = host or settings.host
        port = port or (settings.port + 2)  # Default to port 8003 for Phase 5
        
        # Setup services
        self.setup_security()
        self.setup_monitoring()
        
        # Create default users
        self.create_default_users()
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Configure SSL if provided
        ssl_config = {}
        if ssl_keyfile and ssl_certfile:
            ssl_config = {
                "ssl_keyfile": ssl_keyfile,
                "ssl_certfile": ssl_certfile
            }
            logger.info("SSL configuration enabled")
        
        # Log startup information
        logger.info("=" * 60)
        logger.info("Starting Enhanced MCP Server (Phase 5)")
        logger.info("=" * 60)
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        logger.info(f"Workers: {workers}")
        logger.info(f"Reload: {reload}")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info("Phase 5 Features:")
        logger.info("  ✓ Enhanced Security & Authentication")
        logger.info("  ✓ Real-time Monitoring & Alerting")
        logger.info("  ✓ Performance Analytics")
        logger.info("  ✓ System Health Monitoring")
        logger.info("  ✓ Security Auditing")
        logger.info("=" * 60)
        
        # Start server
        self.running = True
        
        try:
            uvicorn.run(
                "phase5_main:app",
                host=host,
                port=port,
                workers=workers,
                reload=reload,
                log_level=settings.log_level.lower(),
                access_log=True,
                **ssl_config
            )
        except Exception as e:
            logger.error(f"Server startup failed: {str(e)}")
            raise
    
    def shutdown(self):
        """Graceful shutdown"""
        if not self.running:
            return
        
        logger.info("Shutting down Phase 5 MCP Server...")
        
        # Stop monitoring service
        if self.monitoring_service:
            self.monitoring_service.stop_monitoring()
            logger.info("Monitoring service stopped")
        
        # Log shutdown event
        if self.security_manager:
            self.security_manager.log_security_event(
                "SERVER_SHUTDOWN",
                self.security_manager.ThreatLevel.INFO,
                description="Phase 5 MCP Server shutdown"
            )
        
        self.running = False
        logger.info("Phase 5 MCP Server shutdown complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced MCP Server (Phase 5) with Security and Monitoring"
    )
    
    parser.add_argument(
        "--host",
        default=None,
        help=f"Host to bind to (default: {settings.host})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=f"Port to bind to (default: {settings.port + 2})"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--ssl-keyfile",
        help="SSL key file path"
    )
    
    parser.add_argument(
        "--ssl-certfile", 
        help="SSL certificate file path"
    )
    
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run health checks and exit"
    )
    
    parser.add_argument(
        "--create-users",
        action="store_true",
        help="Create default users and API keys"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Create server manager
    server_manager = Phase5ServerManager()
    
    # Handle special commands
    if args.health_check:
        success = server_manager.run_health_checks()
        sys.exit(0 if success else 1)
    
    if args.validate_config:
        valid = server_manager.validate_environment()
        if valid:
            logger.info("Configuration validation passed")
        else:
            logger.error("Configuration validation failed")
        sys.exit(0 if valid else 1)
    
    if args.create_users:
        server_manager.setup_security()
        server_manager.create_default_users()
        logger.info("Default users created")
        sys.exit(0)
    
    # Run health checks before starting
    if not server_manager.run_health_checks():
        logger.error("Health checks failed. Aborting startup.")
        sys.exit(1)
    
    # Start server
    try:
        server_manager.start_server(
            host=args.host,
            port=args.port,
            workers=args.workers,
            reload=args.reload,
            ssl_keyfile=args.ssl_keyfile,
            ssl_certfile=args.ssl_certfile
        )
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        server_manager.shutdown()


if __name__ == "__main__":
    main()