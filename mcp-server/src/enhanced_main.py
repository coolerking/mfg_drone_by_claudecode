"""
Enhanced Main FastAPI application for MCP Server - Phase 2
Integrates advanced NLP, command routing, and batch processing
"""

import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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

# Import enhanced components
from core.backend_client import BackendClient, BackendClientError
from core.enhanced_nlp_engine import EnhancedNLPEngine, ParsedCommand, ConfidenceLevel
from core.enhanced_command_router import EnhancedCommandRouter
from core.batch_processor import (
    AdvancedBatchProcessor, BatchExecutionContext, 
    BatchExecutionMode, ErrorRecoveryStrategy
)

# Import config
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from config.settings import settings
from config.logging import setup_logging, get_logger


# Setup logging
setup_logging()
logger = get_logger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Global instances
backend_client = BackendClient()
enhanced_nlp_engine = EnhancedNLPEngine()
enhanced_command_router = EnhancedCommandRouter(backend_client)
batch_processor = AdvancedBatchProcessor(enhanced_nlp_engine, enhanced_command_router)


# Enhanced request models for Phase 2
class EnhancedNaturalLanguageCommand(BaseModel):
    """Enhanced natural language command with analysis options"""
    command: str
    context: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    analyze: bool = False  # Whether to return detailed analysis
    confidence_threshold: Optional[float] = None


class AdvancedBatchCommand(BaseModel):
    """Advanced batch command with execution options"""
    commands: List[NaturalLanguageCommand]
    execution_mode: str = "optimized"  # sequential, parallel, optimized, priority_based
    error_recovery: str = "smart_recovery"  # stop_on_error, continue_on_error, retry_and_continue, smart_recovery
    max_retries: int = 2
    timeout_per_command: float = 30.0
    max_parallel_commands: int = 5


class CommandAnalysisRequest(BaseModel):
    """Request for command analysis"""
    command: str
    context: Optional[Dict[str, Any]] = None


class CommandSuggestionsRequest(BaseModel):
    """Request for command suggestions"""
    partial_command: str
    max_suggestions: int = 5


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Enhanced MCP Server (Phase 2)")
    yield
    logger.info("Shutting down Enhanced MCP Server")
    await backend_client.close()


# Create Enhanced FastAPI app
app = FastAPI(
    title=f"{settings.api_title} - Enhanced",
    version=f"{settings.api_version}-phase2",
    description=f"{settings.api_description} - Phase 2 with Advanced NLP and Batch Processing",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure as needed
)


# Security dependency
async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify API key"""
    if settings.api_key:
        if not credentials or credentials.credentials != settings.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    return True


# Exception handlers
@app.exception_handler(BackendClientError)
async def backend_client_error_handler(request, exc: BackendClientError):
    """Handle backend client errors"""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ApiError(
            error_code=exc.error_code,
            message=exc.message,
            timestamp=datetime.now()
        ).dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """Handle value errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiError(
            error_code=ErrorCodes.INVALID_COMMAND,
            message=str(exc),
            timestamp=datetime.now()
        ).dict()
    )


# Enhanced Natural Language Command Processing Endpoints

@app.post("/mcp/command/enhanced", response_model=CommandResponse, tags=["enhanced-command"])
async def execute_enhanced_natural_language_command(
    command: EnhancedNaturalLanguageCommand,
    auth: bool = Depends(verify_api_key)
):
    """Execute enhanced natural language command with detailed analysis"""
    try:
        logger.info(f"Processing enhanced command: {command.command}")
        
        # Parse command with enhanced engine
        parsed_command = enhanced_nlp_engine.parse_command(command.command, command.context)
        
        # Check confidence threshold
        threshold = command.confidence_threshold or settings.nlp_confidence_threshold
        if parsed_command.primary_intent.confidence < threshold:
            return CommandResponse(
                success=False,
                message=f"Low confidence parsing ({parsed_command.primary_intent.confidence:.2f}). Please rephrase your command.",
                parsed_intent=parsed_command.primary_intent,
                result={
                    "confidence_level": parsed_command.confidence_level.value,
                    "suggestions": parsed_command.suggestions,
                    "alternatives": [alt.action for alt in parsed_command.alternative_intents],
                    "missing_parameters": parsed_command.missing_parameters
                }
            )
        
        # Execute command with enhanced router
        response = await enhanced_command_router.execute_enhanced_command(parsed_command)
        
        # Add analysis information if requested
        if command.analyze:
            analysis = enhanced_nlp_engine.analyze_command_complexity(command.command)
            response.result["analysis"] = analysis
        
        logger.info(f"Enhanced command executed: success={response.success}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing enhanced command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/mcp/command/batch/advanced", response_model=BatchCommandResponse, tags=["enhanced-command"])
async def execute_advanced_batch_commands(
    batch_command: AdvancedBatchCommand,
    auth: bool = Depends(verify_api_key)
):
    """Execute advanced batch commands with optimization and dependency analysis"""
    logger.info(f"Processing advanced batch of {len(batch_command.commands)} commands")
    
    try:
        # Create batch execution context
        execution_context = BatchExecutionContext(
            execution_mode=BatchExecutionMode(batch_command.execution_mode),
            error_recovery=ErrorRecoveryStrategy(batch_command.error_recovery),
            max_retries=batch_command.max_retries,
            timeout_per_command=batch_command.timeout_per_command,
            max_parallel_commands=batch_command.max_parallel_commands
        )
        
        # Process batch with advanced processor
        response = await batch_processor.process_batch(batch_command.commands, execution_context)
        
        logger.info(f"Advanced batch execution completed: {response.summary.successful_commands}/{response.summary.total_commands} successful")
        return response
        
    except Exception as e:
        logger.error(f"Error processing advanced batch commands: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Enhanced Analysis and Utility Endpoints

@app.post("/mcp/command/analyze", tags=["enhanced-analysis"])
async def analyze_command(
    request: CommandAnalysisRequest,
    auth: bool = Depends(verify_api_key)
):
    """Analyze command complexity and provide detailed breakdown"""
    try:
        analysis = enhanced_nlp_engine.analyze_command_complexity(request.command)
        return {
            "command": request.command,
            "analysis": analysis,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error analyzing command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/mcp/command/suggestions", tags=["enhanced-analysis"])
async def get_command_suggestions(
    request: CommandSuggestionsRequest,
    auth: bool = Depends(verify_api_key)
):
    """Get command suggestions based on partial input"""
    try:
        suggestions = enhanced_nlp_engine.get_command_suggestions(request.partial_command)
        return {
            "partial_command": request.partial_command,
            "suggestions": suggestions[:request.max_suggestions],
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting command suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/mcp/analytics/execution", tags=["enhanced-analysis"])
async def get_execution_analytics(auth: bool = Depends(verify_api_key)):
    """Get execution analytics and statistics"""
    try:
        stats = enhanced_command_router.get_execution_statistics()
        return {
            "execution_statistics": stats,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting execution analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Original endpoints (maintaining backward compatibility)

@app.post("/mcp/command", response_model=CommandResponse, tags=["command"])
async def execute_natural_language_command(
    command: NaturalLanguageCommand,
    auth: bool = Depends(verify_api_key)
):
    """Execute natural language command (backward compatibility)"""
    try:
        logger.info(f"Processing legacy command: {command.command}")
        
        # Use enhanced engine but return simple response
        parsed_command = enhanced_nlp_engine.parse_command(command.command, command.context)
        
        # Check confidence threshold
        if parsed_command.primary_intent.confidence < settings.nlp_confidence_threshold:
            raise ValueError(
                f"Low confidence parsing ({parsed_command.primary_intent.confidence:.2f}). "
                f"Please rephrase your command."
            )
        
        # Execute command
        response = await enhanced_command_router.execute_enhanced_command(parsed_command)
        
        logger.info(f"Legacy command executed: success={response.success}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing legacy command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/mcp/command/batch", response_model=BatchCommandResponse, tags=["command"])
async def execute_batch_commands(
    batch_command: BatchCommand,
    auth: bool = Depends(verify_api_key)
):
    """Execute multiple natural language commands (backward compatibility)"""
    logger.info(f"Processing legacy batch of {len(batch_command.commands)} commands")
    
    try:
        # Convert to advanced batch format
        advanced_batch = AdvancedBatchCommand(
            commands=batch_command.commands,
            execution_mode="sequential" if batch_command.execution_mode.value == "sequential" else "parallel",
            error_recovery="stop_on_error" if batch_command.stop_on_error else "continue_on_error"
        )
        
        # Use advanced processor
        execution_context = BatchExecutionContext(
            execution_mode=BatchExecutionMode(advanced_batch.execution_mode),
            error_recovery=ErrorRecoveryStrategy(advanced_batch.error_recovery)
        )
        
        response = await batch_processor.process_batch(batch_command.commands, execution_context)
        
        logger.info(f"Legacy batch execution completed: {response.summary.successful_commands}/{response.summary.total_commands} successful")
        return response
        
    except Exception as e:
        logger.error(f"Error processing legacy batch commands: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# All other original endpoints remain the same for backward compatibility
# (Drone Information, Drone Control, Camera, Vision, System endpoints)

@app.get("/mcp/drones", response_model=DroneListResponse, tags=["drone-query"])
async def get_drones(auth: bool = Depends(verify_api_key)):
    """Get all registered drones"""
    try:
        drones = await backend_client.get_drones()
        return DroneListResponse(
            drones=drones,
            count=len(drones),
            message="Drones retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting drones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/mcp/drones/available", response_model=DroneListResponse, tags=["drone-query"])
async def get_available_drones(auth: bool = Depends(verify_api_key)):
    """Get available drones"""
    try:
        drones = await backend_client.get_available_drones()
        return DroneListResponse(
            drones=drones,
            count=len(drones),
            message="Available drones retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting available drones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/mcp/drones/{drone_id}/status", response_model=DroneStatusResponse, tags=["drone-query"])
async def get_drone_status(drone_id: str, auth: bool = Depends(verify_api_key)):
    """Get drone status"""
    try:
        status_detail = await backend_client.get_drone_status(drone_id)
        return DroneStatusResponse(
            drone_id=drone_id,
            status=status_detail,
            message="Drone status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting drone status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# System status endpoints with enhanced information
@app.get("/mcp/system/status/enhanced", response_model=SystemStatusResponse, tags=["enhanced-system"])
async def get_enhanced_system_status(auth: bool = Depends(verify_api_key)):
    """Get enhanced system status with NLP and processing statistics"""
    try:
        backend_status = await backend_client.get_system_status()
        execution_stats = enhanced_command_router.get_execution_statistics()
        
        # Create enhanced MCP server status
        from models.system_models import McpServerStatus, BackendSystemStatus
        
        mcp_status = McpServerStatus(
            status="running",
            uptime=0,  # TODO: Implement uptime tracking
            version=f"{settings.api_version}-phase2",
            active_connections=0  # TODO: Implement connection tracking
        )
        
        backend_sys_status = BackendSystemStatus(
            connection_status="connected",
            api_endpoint=settings.backend_api_url,
            response_time=None  # TODO: Implement response time tracking
        )
        
        response = SystemStatusResponse(
            mcp_server=mcp_status,
            backend_system=backend_sys_status,
            connected_drones=0,  # TODO: Get from backend status
            active_operations=0,  # TODO: Implement operation tracking
            system_health="healthy"
        )
        
        # Add enhanced information
        response.result = {
            "enhanced_features": {
                "nlp_engine": "Enhanced NLP Engine v2.0",
                "command_router": "Enhanced Command Router v2.0",
                "batch_processor": "Advanced Batch Processor v2.0"
            },
            "execution_statistics": execution_stats,
            "feature_flags": {
                "enhanced_nlp": True,
                "dependency_analysis": True,
                "parallel_processing": True,
                "smart_error_recovery": True,
                "command_analytics": True
            }
        }
        
        return response
    except Exception as e:
        logger.error(f"Error getting enhanced system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Enhanced root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Enhanced root endpoint"""
    return {
        "name": f"{settings.api_title} - Enhanced",
        "version": f"{settings.api_version}-phase2",
        "status": "running",
        "features": [
            "Enhanced Natural Language Processing",
            "Advanced Batch Processing",
            "Dependency Analysis",
            "Parallel Execution",
            "Smart Error Recovery",
            "Command Analytics"
        ],
        "timestamp": datetime.now()
    }


# Health check with enhanced features
@app.get("/mcp/health/enhanced", tags=["enhanced-system"])
async def enhanced_health_check(auth: bool = Depends(verify_api_key)):
    """Enhanced health check including NLP and processing components"""
    try:
        # Check backend health
        backend_health = await backend_client.health_check()
        
        # Test NLP engine
        try:
            test_parsed = enhanced_nlp_engine.parse_command("テスト", {})
            nlp_status = "pass"
            nlp_message = "NLP engine is functioning"
        except Exception as e:
            nlp_status = "fail"
            nlp_message = f"NLP engine error: {str(e)}"
        
        # Test command router
        try:
            router_stats = enhanced_command_router.get_execution_statistics()
            router_status = "pass"
            router_message = "Command router is functioning"
        except Exception as e:
            router_status = "fail"
            router_message = f"Command router error: {str(e)}"
        
        from models.system_models import HealthCheck, HealthResponse
        
        checks = [
            HealthCheck(
                name="Enhanced MCP Server",
                status="pass",
                message="Enhanced MCP Server is running",
                response_time=None
            ),
            HealthCheck(
                name="Enhanced NLP Engine",
                status=nlp_status,
                message=nlp_message,
                response_time=None
            ),
            HealthCheck(
                name="Enhanced Command Router",
                status=router_status,
                message=router_message,
                response_time=None
            ),
            HealthCheck(
                name="Backend API",
                status="pass" if backend_health.get("status") == "healthy" else "fail",
                message="Backend API is accessible",
                response_time=None
            )
        ]
        
        overall_status = "healthy" if all(check.status == "pass" for check in checks) else "unhealthy"
        
        return HealthResponse(
            status=overall_status,
            checks=checks
        )
    except Exception as e:
        logger.error(f"Error performing enhanced health check: {str(e)}")
        
        from models.system_models import HealthCheck, HealthResponse
        checks = [
            HealthCheck(
                name="Enhanced MCP Server",
                status="fail",
                message=f"Enhanced health check failed: {str(e)}",
                response_time=None
            )
        ]
        
        return HealthResponse(
            status="unhealthy",
            checks=checks
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "enhanced_main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )