"""
Phase 5: Enhanced MCP Server with Integrated Security and Monitoring
Features:
- Enhanced security with comprehensive authentication and authorization
- Real-time monitoring and alerting
- Performance tracking and analytics
- Security auditing and threat detection
- System health monitoring
"""

import os
import sys
import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.background_tasks import BackgroundTasks
import uvicorn

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.command_models import (
    NaturalLanguageCommand, BatchCommand, CommandResponse, 
    BatchCommandResponse, CommandError
)
from models.drone_models import (
    DroneListResponse, DroneStatusResponse, TakeoffCommand,
    MoveCommand, RotateCommand, AltitudeCommand, OperationResponse
)
from models.camera_models import (
    PhotoCommand, StreamingCommand, LearningDataCommand,
    DetectionCommand, TrackingCommand, PhotoResponse,
    LearningDataResponse, DetectionResponse
)
from models.system_models import (
    SystemStatusResponse, HealthResponse, ApiError, ErrorCodes
)
from core.backend_client import BackendClient, BackendClientError
from core.nlp_engine import NLPEngine
from core.command_router import CommandRouter
from core.enhanced_nlp_engine import EnhancedNLPEngine
from core.enhanced_command_router import EnhancedCommandRouter
from core.security_manager import SecurityManager, SecurityLevel, SecurityConfig
from core.monitoring_service import MonitoringService, AlertSeverity

# Import config
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from config.settings import settings
from config.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Global services
backend_client = BackendClient()
nlp_engine = EnhancedNLPEngine()
command_router = EnhancedCommandRouter(backend_client)
def get_security_config() -> SecurityConfig:
    """Get security configuration with proper validation"""
    jwt_secret = settings.jwt_secret
    if not jwt_secret:
        raise ValueError(
            "JWT_SECRET environment variable is required for security. "
            "Please set a strong, randomly generated secret of at least 32 characters."
        )
    
    return SecurityConfig(
        jwt_secret=jwt_secret,
        max_failed_attempts=settings.max_failed_attempts,
        lockout_duration_minutes=settings.lockout_duration,
        allowed_ips=settings.allowed_ips,
        blocked_ips=settings.blocked_ips,
        enable_audit_logging=settings.audit_logging_enabled
    )

security_manager = SecurityManager(get_security_config())
monitoring_service = MonitoringService()

# Application startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Enhanced MCP Server (Phase 5)")
    
    # Start monitoring service
    monitoring_service.start_monitoring(interval_seconds=30)
    
    # Add alert callback
    def alert_callback(alert_instance):
        logger.warning(f"ALERT: {alert_instance.message}")
    
    monitoring_service.add_alert_callback(alert_callback)
    
    # Log startup
    security_manager.log_security_event(
        "SERVER_STARTUP", 
        security_manager.ThreatLevel.INFO,
        description="MCP Server started"
    )
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down Enhanced MCP Server")
    monitoring_service.stop_monitoring()
    await backend_client.close()
    
    security_manager.log_security_event(
        "SERVER_SHUTDOWN",
        security_manager.ThreatLevel.INFO,
        description="MCP Server shutdown"
    )

# Create FastAPI app
app = FastAPI(
    title=f"{settings.api_title} (Phase 5 Enhanced)",
    version=f"{settings.api_version}-phase5",
    description=f"{settings.api_description}\n\nPhase 5 Features:\n- Enhanced Security & Authentication\n- Real-time Monitoring & Alerting\n- Performance Analytics\n- System Health Monitoring",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add middleware
if settings.cors_enabled:
    # Configure CORS based on environment
    cors_origins = settings.allowed_origins
    if settings.is_production() and "*" in cors_origins:
        raise ValueError("CORS wildcard (*) is not allowed in production environment")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=settings.cors_max_age,
    )
    logger.info(f"CORS middleware configured with origins: {cors_origins}")

if settings.trusted_hosts_enabled:
    # Configure trusted hosts based on environment
    trusted_hosts = settings.trusted_hosts
    if settings.is_production() and "*" in trusted_hosts:
        raise ValueError("Trusted hosts wildcard (*) is not allowed in production environment")
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )
    logger.info(f"Trusted hosts middleware configured with hosts: {trusted_hosts}")

# HTTPS redirect middleware
@app.middleware("http")
async def https_redirect_middleware(request: Request, call_next):
    """Middleware to force HTTPS redirection in production"""
    if settings.force_https and not request.url.scheme == "https":
        # Check if this is a health check or internal request
        if request.url.path not in ["/health", "/metrics"]:
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(https_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)
    
    return await call_next(request)

# Request timing middleware
@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    """Middleware to track request timing and security"""
    start_time = time.time()
    client_ip = request.client.host
    
    # Check if IP is allowed
    if not security_manager.is_ip_allowed(client_ip):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "IP address not allowed"}
        )
    
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Record metrics
    monitoring_service.record_request(
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration=duration
    )
    
    # Add security headers
    if settings.security_headers_enabled:
        response.headers["X-Content-Type-Options"] = settings.x_content_type_options
        response.headers["X-Frame-Options"] = settings.x_frame_options
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = settings.referrer_policy
        response.headers["Content-Security-Policy"] = settings.content_security_policy
        
        # Add HSTS header if HTTPS is enabled
        if settings.ssl_enabled or settings.force_https:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add additional security headers for production
        if settings.is_production():
            response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
            response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    
    return response

# Authentication dependencies
async def get_current_user(
    bearer_token: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    request: Request = None
) -> tuple[str, SecurityLevel]:
    """Get current authenticated user"""
    client_ip = request.client.host if request else "unknown"
    user_id = None
    security_level = None
    
    # Try JWT token first
    if bearer_token:
        valid, user_id, security_level = security_manager.validate_jwt_token(bearer_token.credentials)
        if valid:
            # Check if account is locked
            if security_manager.is_account_locked(user_id):
                security_manager.record_access_attempt(
                    client_ip, user_id, request.url.path, False, "Account locked"
                )
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account is temporarily locked"
                )
            
            # Check rate limiting
            if not security_manager.check_rate_limit(user_id, client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            security_manager.record_access_attempt(
                client_ip, user_id, request.url.path, True
            )
            return user_id, security_level
    
    # Try API key
    if api_key:
        valid, user_id, security_level = security_manager.validate_api_key(api_key)
        if valid:
            # Check if account is locked
            if security_manager.is_account_locked(user_id):
                security_manager.record_access_attempt(
                    client_ip, user_id, request.url.path, False, "Account locked"
                )
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account is temporarily locked"
                )
            
            # Check rate limiting
            if not security_manager.check_rate_limit(user_id, client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            security_manager.record_access_attempt(
                client_ip, user_id, request.url.path, True
            )
            return user_id, security_level
    
    # No valid authentication
    security_manager.record_access_attempt(
        client_ip, None, request.url.path, False, "No valid authentication"
    )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

def require_security_level(required_level: SecurityLevel):
    """Dependency to require specific security level"""
    async def check_security_level(current_user: tuple = Depends(get_current_user)):
        user_id, user_level = current_user
        if not security_manager.check_authorization(user_level, required_level):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_level.value}"
            )
        return current_user
    return check_security_level

# Exception handlers
@app.exception_handler(BackendClientError)
async def backend_client_error_handler(request: Request, exc: BackendClientError):
    """Handle backend client errors"""
    monitoring_service.increment_counter("backend_errors")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ApiError(
            error_code=exc.error_code,
            message=exc.message,
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors"""
    monitoring_service.increment_counter("validation_errors")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiError(
            error_code=ErrorCodes.INVALID_COMMAND,
            message=str(exc),
            timestamp=datetime.now()
        ).dict()
    )

# Secure user authentication configuration
def get_user_credentials() -> Dict[str, Dict[str, str]]:
    """Get user credentials from environment variables or secure storage"""
    users = {}
    
    # Load admin credentials from settings
    if settings.admin_username and settings.admin_password:
        users[settings.admin_username] = {
            "password": settings.admin_password,
            "security_level": SecurityLevel.ADMIN.value
        }
    
    # Load operator credentials from settings
    if settings.operator_username and settings.operator_password:
        users[settings.operator_username] = {
            "password": settings.operator_password,
            "security_level": SecurityLevel.OPERATOR.value
        }
    
    # Load read-only credentials from settings
    if settings.readonly_username and settings.readonly_password:
        users[settings.readonly_username] = {
            "password": settings.readonly_password,
            "security_level": SecurityLevel.READ_ONLY.value
        }
    
    if not users:
        raise ValueError(
            "No user credentials configured. Please set environment variables: "
            "ADMIN_USERNAME, ADMIN_PASSWORD, OPERATOR_USERNAME, OPERATOR_PASSWORD, etc."
        )
    
    return users

# Authentication endpoints
@app.post("/auth/login", response_model=Dict[str, Any], tags=["authentication"])
async def login(username: str, password: str, background_tasks: BackgroundTasks, request: Request):
    """Login and get JWT token"""
    client_ip = request.client.host
    
    try:
        user_credentials = get_user_credentials()
        
        # Check if user exists and password matches
        if username not in user_credentials or user_credentials[username]["password"] != password:
            # Record failed attempt
            security_manager.record_access_attempt(
                client_ip, username, "/auth/login", False, "Invalid credentials"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if account is locked
        if security_manager.is_account_locked(username):
            security_manager.record_access_attempt(
                client_ip, username, "/auth/login", False, "Account locked"
            )
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to multiple failed attempts"
            )
        
        user_id = username
        security_level = SecurityLevel(user_credentials[username]["security_level"])
        
    except ValueError as e:
        # Configuration error
        logger.error(f"Authentication configuration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )
    
    # Generate JWT token
    jwt_token = security_manager.generate_jwt_token(user_id, security_level)
    
    # Log successful login
    security_manager.log_security_event(
        "USER_LOGIN",
        security_manager.ThreatLevel.LOW,
        user_id=user_id,
        description=f"User {user_id} logged in successfully"
    )
    
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user_id": user_id,
        "security_level": security_level.value,
        "expires_in": security_manager.config.jwt_expiry_minutes * 60
    }

@app.post("/auth/api-key", response_model=Dict[str, str], tags=["authentication"])
async def generate_api_key(
    user_id: str,
    security_level_str: str,
    current_user: tuple = Depends(require_security_level(SecurityLevel.ADMIN))
):
    """Generate API key (Admin only)"""
    try:
        security_level = SecurityLevel(security_level_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid security level: {security_level_str}"
        )
    
    api_key = security_manager.generate_api_key(user_id, security_level)
    
    security_manager.log_security_event(
        "API_KEY_GENERATED",
        security_manager.ThreatLevel.MEDIUM,
        user_id=current_user[0],
        description=f"API key generated for user {user_id} with level {security_level.value}"
    )
    
    return {"api_key": api_key}

# Enhanced command processing endpoints
@app.post("/mcp/command/enhanced", response_model=CommandResponse, tags=["command"])
async def execute_enhanced_natural_language_command(
    command: NaturalLanguageCommand,
    background_tasks: BackgroundTasks,
    current_user: tuple = Depends(require_security_level(SecurityLevel.OPERATOR))
):
    """Execute enhanced natural language command with security and monitoring"""
    user_id, user_level = current_user
    
    try:
        # Validate and sanitize command input
        valid, sanitized_command = security_manager.validate_command_input(command.command)
        if not valid:
            raise ValueError(f"Invalid command input: {sanitized_command}")
        
        # Update command with sanitized input
        command.command = sanitized_command
        
        logger.info(f"Processing enhanced command from user {user_id}: {command.command}")
        
        # Start timing
        start_time = time.time()
        
        # Parse command using enhanced NLP engine
        parsed_intent = nlp_engine.parse_command(command.command, command.context)
        
        nlp_duration = time.time() - start_time
        monitoring_service.record_nlp_processing(
            command.command, nlp_duration, parsed_intent.confidence, True
        )
        
        # Check confidence threshold
        if parsed_intent.confidence < settings.nlp_confidence_threshold:
            monitoring_service.increment_counter("low_confidence_commands")
            raise ValueError(
                f"Low confidence parsing ({parsed_intent.confidence:.2f}). "
                f"Please rephrase your command."
            )
        
        # Execute command using enhanced router
        response = await command_router.execute_command(parsed_intent)
        
        total_duration = time.time() - start_time
        
        # Record success metrics
        monitoring_service.increment_counter("successful_commands")
        monitoring_service.observe_histogram("command_execution_time", total_duration)
        
        logger.info(f"Enhanced command executed: success={response.success}, duration={total_duration:.2f}s")
        return response
        
    except Exception as e:
        error_duration = time.time() - start_time
        
        # Record error metrics
        monitoring_service.increment_counter("failed_commands")
        monitoring_service.observe_histogram("command_execution_time", error_duration)
        
        # Log security event for suspicious commands
        if "malicious" in str(e).lower() or "injection" in str(e).lower():
            security_manager.log_security_event(
                "MALICIOUS_COMMAND_ATTEMPT",
                security_manager.ThreatLevel.HIGH,
                user_id=user_id,
                description=f"Potential malicious command: {command.command[:100]}"
            )
        
        logger.error(f"Error processing enhanced command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# System monitoring endpoints
@app.get("/mcp/system/health/detailed", response_model=Dict[str, Any], tags=["monitoring"])
async def get_detailed_health_check(
    current_user: tuple = Depends(require_security_level(SecurityLevel.READ_ONLY))
):
    """Get detailed system health report"""
    health_report = monitoring_service.get_system_health_report()
    
    # Add security information
    security_summary = security_manager.get_security_summary()
    threat_analysis = security_manager.get_threat_analysis()
    
    return {
        "system_health": health_report,
        "security_summary": security_summary,
        "threat_analysis": threat_analysis,
        "timestamp": datetime.utcnow()
    }

@app.get("/mcp/system/performance", response_model=Dict[str, Any], tags=["monitoring"])
async def get_performance_metrics(
    time_window_minutes: int = 60,
    current_user: tuple = Depends(require_security_level(SecurityLevel.READ_ONLY))
):
    """Get performance metrics"""
    return monitoring_service.get_performance_summary(time_window_minutes)

@app.get("/mcp/system/alerts", response_model=List[Dict[str, Any]], tags=["monitoring"])
async def get_active_alerts(
    current_user: tuple = Depends(require_security_level(SecurityLevel.READ_ONLY))
):
    """Get active alerts"""
    active_alerts = monitoring_service.get_active_alerts()
    
    return [
        {
            "alert_id": alert.alert_id,
            "timestamp": alert.timestamp,
            "severity": alert.severity.value,
            "message": alert.message,
            "metric_value": alert.metric_value,
            "threshold": alert.threshold,
            "resolved": alert.resolved
        }
        for alert in active_alerts
    ]

@app.post("/mcp/system/alerts/{alert_id}/resolve", response_model=Dict[str, str], tags=["monitoring"])
async def resolve_alert(
    alert_id: str,
    current_user: tuple = Depends(require_security_level(SecurityLevel.OPERATOR))
):
    """Resolve an alert"""
    monitoring_service.resolve_alert(alert_id)
    
    security_manager.log_security_event(
        "ALERT_RESOLVED",
        security_manager.ThreatLevel.LOW,
        user_id=current_user[0],
        description=f"Alert {alert_id} resolved by user {current_user[0]}"
    )
    
    return {"message": f"Alert {alert_id} resolved"}

# Security management endpoints
@app.get("/mcp/security/summary", response_model=Dict[str, Any], tags=["security"])
async def get_security_summary(
    current_user: tuple = Depends(require_security_level(SecurityLevel.ADMIN))
):
    """Get security summary (Admin only)"""
    return security_manager.get_security_summary()

@app.get("/mcp/security/events", response_model=List[Dict[str, Any]], tags=["security"])
async def get_security_events(
    limit: int = 100,
    current_user: tuple = Depends(require_security_level(SecurityLevel.ADMIN))
):
    """Get recent security events (Admin only)"""
    recent_events = security_manager.security_events[-limit:]
    
    return [
        {
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "severity": event.severity.value,
            "source_ip": event.source_ip,
            "user_id": event.user_id,
            "description": event.description,
            "metadata": event.metadata
        }
        for event in recent_events
    ]

@app.post("/mcp/security/block-ip", response_model=Dict[str, str], tags=["security"])
async def block_ip_address(
    ip_address: str,
    current_user: tuple = Depends(require_security_level(SecurityLevel.ADMIN))
):
    """Block an IP address (Admin only)"""
    security_manager.config.blocked_ips.append(ip_address)
    
    security_manager.log_security_event(
        "IP_BLOCKED",
        security_manager.ThreatLevel.MEDIUM,
        user_id=current_user[0],
        description=f"IP address {ip_address} blocked by admin {current_user[0]}"
    )
    
    return {"message": f"IP address {ip_address} blocked"}

# Metrics export endpoints
@app.get("/metrics", response_class=PlainTextResponse, tags=["monitoring"])
async def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    return monitoring_service.export_metrics("prometheus")

@app.get("/metrics/json", response_model=Dict[str, Any], tags=["monitoring"])
async def get_json_metrics(
    current_user: tuple = Depends(require_security_level(SecurityLevel.READ_ONLY))
):
    """Get metrics in JSON format"""
    return json.loads(monitoring_service.export_metrics("json"))

# Enhanced system status endpoint
@app.get("/mcp/system/status/enhanced", response_model=Dict[str, Any], tags=["system"])
async def get_enhanced_system_status(
    current_user: tuple = Depends(require_security_level(SecurityLevel.READ_ONLY))
):
    """Get enhanced system status with Phase 5 features"""
    try:
        # Get standard system status
        backend_status = await backend_client.get_system_status()
        
        # Get enhanced monitoring data
        health_report = monitoring_service.get_system_health_report()
        security_summary = security_manager.get_security_summary()
        
        return {
            "mcp_server": {
                "status": "running",
                "version": f"{settings.api_version}-phase5",
                "uptime_hours": health_report.get("uptime_hours", 0),
                "active_connections": health_report["system_metrics"]["active_connections"],
                "features": [
                    "Enhanced Security & Authentication",
                    "Real-time Monitoring & Alerting", 
                    "Performance Analytics",
                    "System Health Monitoring",
                    "Security Auditing"
                ]
            },
            "backend_system": {
                "connection_status": "connected",
                "api_endpoint": settings.backend_api_url,
                "response_time": None  # TODO: Implement
            },
            "system_health": health_report,
            "security_status": security_summary,
            "connected_drones": backend_status.get("connected_drones", 0),
            "active_operations": backend_status.get("active_operations", 0),
            "phase5_features": {
                "security_enabled": True,
                "monitoring_enabled": True,
                "alerting_enabled": True,
                "analytics_enabled": True
            },
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting enhanced system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Inherit all other endpoints from the base implementation
# (The existing endpoints from main.py would be included here)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with Phase 5 information"""
    return {
        "name": f"{settings.api_title} (Phase 5 Enhanced)",
        "version": f"{settings.api_version}-phase5",
        "status": "running",
        "features": [
            "Enhanced Security & Authentication",
            "Real-time Monitoring & Alerting",
            "Performance Analytics", 
            "System Health Monitoring",
            "Security Auditing"
        ],
        "timestamp": datetime.utcnow(),
        "endpoints": {
            "documentation": "/docs",
            "health": "/mcp/system/health/detailed",
            "metrics": "/metrics",
            "security": "/mcp/security/summary"
        }
    }

# Background tasks
async def cleanup_task():
    """Background cleanup task"""
    while True:
        try:
            # Clean up expired sessions
            security_manager.cleanup_expired_sessions()
            
            # Clean up old performance data
            # This would be handled by the monitoring service automatically
            
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Error in cleanup task: {str(e)}")
            await asyncio.sleep(300)  # Wait 5 minutes on error

# Start background tasks
@app.on_event("startup")
async def start_background_tasks():
    """Start background tasks"""
    asyncio.create_task(cleanup_task())

if __name__ == "__main__":
    # Enhanced startup with Phase 5 features
    logger.info("Starting Enhanced MCP Server (Phase 5)")
    logger.info("Features: Enhanced Security, Real-time Monitoring, Performance Analytics")
    
    uvicorn.run(
        "phase5_main:app",
        host=settings.host,
        port=settings.port + 2,  # Use different port for Phase 5
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )