"""
Main FastAPI application for MCP Server
"""

import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

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
nlp_engine = NLPEngine()
command_router = CommandRouter(backend_client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting MCP Server")
    yield
    logger.info("Shutting down MCP Server")
    await backend_client.close()


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
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


# Natural Language Command Processing Endpoints

@app.post("/mcp/command", response_model=CommandResponse, tags=["command"])
async def execute_natural_language_command(
    command: NaturalLanguageCommand,
    auth: bool = Depends(verify_api_key)
):
    """Execute natural language command"""
    try:
        logger.info(f"Processing command: {command.command}")
        
        # Parse command
        parsed_intent = nlp_engine.parse_command(command.command, command.context)
        
        # Check confidence threshold
        if parsed_intent.confidence < settings.nlp_confidence_threshold:
            raise ValueError(
                f"Low confidence parsing ({parsed_intent.confidence:.2f}). "
                f"Please rephrase your command."
            )
        
        # Execute command
        response = await command_router.execute_command(parsed_intent)
        
        logger.info(f"Command executed: success={response.success}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/mcp/command/batch", response_model=BatchCommandResponse, tags=["command"])
async def execute_batch_commands(
    batch_command: BatchCommand,
    auth: bool = Depends(verify_api_key)
):
    """Execute multiple natural language commands"""
    logger.info(f"Processing batch of {len(batch_command.commands)} commands")
    
    results = []
    successful_commands = 0
    failed_commands = 0
    start_time = datetime.now()
    
    try:
        if batch_command.execution_mode == "sequential":
            # Execute commands sequentially
            for cmd in batch_command.commands:
                try:
                    parsed_intent = nlp_engine.parse_command(cmd.command, cmd.context)
                    response = await command_router.execute_command(parsed_intent)
                    results.append(response)
                    
                    if response.success:
                        successful_commands += 1
                    else:
                        failed_commands += 1
                        if batch_command.stop_on_error:
                            break
                            
                except Exception as e:
                    failed_commands += 1
                    error_response = CommandResponse(
                        success=False,
                        message=f"Error: {str(e)}",
                        timestamp=datetime.now()
                    )
                    results.append(error_response)
                    
                    if batch_command.stop_on_error:
                        break
        else:
            # Execute commands in parallel
            import asyncio
            
            async def execute_single(cmd):
                try:
                    parsed_intent = nlp_engine.parse_command(cmd.command, cmd.context)
                    return await command_router.execute_command(parsed_intent)
                except Exception as e:
                    return CommandResponse(
                        success=False,
                        message=f"Error: {str(e)}",
                        timestamp=datetime.now()
                    )
            
            results = await asyncio.gather(*[execute_single(cmd) for cmd in batch_command.commands])
            successful_commands = sum(1 for r in results if r.success)
            failed_commands = len(results) - successful_commands
        
        # Calculate total execution time
        total_execution_time = (datetime.now() - start_time).total_seconds()
        
        # Create summary
        from models.command_models import BatchCommandSummary
        summary = BatchCommandSummary(
            total_commands=len(batch_command.commands),
            successful_commands=successful_commands,
            failed_commands=failed_commands,
            total_execution_time=total_execution_time
        )
        
        # Create response
        response = BatchCommandResponse(
            success=failed_commands == 0,
            message=f"Batch execution completed: {successful_commands}/{len(batch_command.commands)} successful",
            results=results,
            summary=summary
        )
        
        logger.info(f"Batch execution completed: {successful_commands}/{len(batch_command.commands)} successful")
        return response
        
    except Exception as e:
        logger.error(f"Error processing batch commands: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Drone Information Endpoints

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


# Drone Control Endpoints

@app.post("/mcp/drones/{drone_id}/connect", response_model=OperationResponse, tags=["drone-control"])
async def connect_drone(drone_id: str, auth: bool = Depends(verify_api_key)):
    """Connect to drone"""
    try:
        return await backend_client.connect_drone(drone_id)
    except Exception as e:
        logger.error(f"Error connecting to drone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/drones/{drone_id}/disconnect", response_model=OperationResponse, tags=["drone-control"])
async def disconnect_drone(drone_id: str, auth: bool = Depends(verify_api_key)):
    """Disconnect from drone"""
    try:
        return await backend_client.disconnect_drone(drone_id)
    except Exception as e:
        logger.error(f"Error disconnecting from drone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/drones/{drone_id}/takeoff", response_model=OperationResponse, tags=["drone-control"])
async def takeoff_drone(
    drone_id: str,
    command: Optional[TakeoffCommand] = None,
    auth: bool = Depends(verify_api_key)
):
    """Take off drone"""
    try:
        target_height = command.target_height if command else None
        return await backend_client.takeoff_drone(drone_id, target_height)
    except Exception as e:
        logger.error(f"Error taking off drone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/drones/{drone_id}/land", response_model=OperationResponse, tags=["drone-control"])
async def land_drone(drone_id: str, auth: bool = Depends(verify_api_key)):
    """Land drone"""
    try:
        return await backend_client.land_drone(drone_id)
    except Exception as e:
        logger.error(f"Error landing drone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/drones/{drone_id}/move", response_model=OperationResponse, tags=["drone-control"])
async def move_drone(
    drone_id: str,
    command: MoveCommand,
    auth: bool = Depends(verify_api_key)
):
    """Move drone"""
    try:
        return await backend_client.move_drone(
            drone_id, command.direction, command.distance, command.speed
        )
    except Exception as e:
        logger.error(f"Error moving drone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/drones/{drone_id}/rotate", response_model=OperationResponse, tags=["drone-control"])
async def rotate_drone(
    drone_id: str,
    command: RotateCommand,
    auth: bool = Depends(verify_api_key)
):
    """Rotate drone"""
    try:
        return await backend_client.rotate_drone(
            drone_id, command.direction, command.angle
        )
    except Exception as e:
        logger.error(f"Error rotating drone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/drones/{drone_id}/emergency", response_model=OperationResponse, tags=["drone-control"])
async def emergency_stop_drone(drone_id: str, auth: bool = Depends(verify_api_key)):
    """Emergency stop drone"""
    try:
        return await backend_client.emergency_stop(drone_id)
    except Exception as e:
        logger.error(f"Error emergency stopping drone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/drones/{drone_id}/altitude", response_model=OperationResponse, tags=["drone-control"])
async def set_drone_altitude(
    drone_id: str,
    command: AltitudeCommand,
    auth: bool = Depends(verify_api_key)
):
    """Set drone altitude"""
    try:
        return await backend_client.set_altitude(
            drone_id, command.target_height, command.mode
        )
    except Exception as e:
        logger.error(f"Error setting drone altitude: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Camera Endpoints

@app.post("/mcp/drones/{drone_id}/camera/photo", response_model=PhotoResponse, tags=["camera"])
async def take_photo(
    drone_id: str,
    command: Optional[PhotoCommand] = None,
    auth: bool = Depends(verify_api_key)
):
    """Take photo"""
    try:
        filename = command.filename if command else None
        quality = command.quality if command else "high"
        
        photo_info = await backend_client.take_photo(drone_id, filename, quality)
        return PhotoResponse(
            success=True,
            message="Photo taken successfully",
            photo=photo_info
        )
    except Exception as e:
        logger.error(f"Error taking photo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/drones/{drone_id}/camera/streaming", response_model=OperationResponse, tags=["camera"])
async def control_streaming(
    drone_id: str,
    command: StreamingCommand,
    auth: bool = Depends(verify_api_key)
):
    """Control camera streaming"""
    try:
        return await backend_client.control_streaming(
            drone_id, command.action, command.quality, command.resolution
        )
    except Exception as e:
        logger.error(f"Error controlling streaming: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/drones/{drone_id}/learning/collect", response_model=LearningDataResponse, tags=["camera"])
async def collect_learning_data(
    drone_id: str,
    command: LearningDataCommand,
    auth: bool = Depends(verify_api_key)
):
    """Collect learning data"""
    try:
        result = await backend_client.collect_learning_data(
            drone_id, command.object_name, **command.dict(exclude={"object_name"})
        )
        
        return LearningDataResponse(
            success=True,
            message="Learning data collected successfully",
            dataset=result.get("dataset"),
            execution_summary=result.get("execution_summary")
        )
    except Exception as e:
        logger.error(f"Error collecting learning data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Vision Endpoints

@app.post("/mcp/vision/detection", response_model=DetectionResponse, tags=["camera"])
async def detect_objects(
    command: DetectionCommand,
    auth: bool = Depends(verify_api_key)
):
    """Detect objects"""
    try:
        detections = await backend_client.detect_objects(
            command.drone_id, command.model_id, command.confidence_threshold
        )
        
        return DetectionResponse(
            success=True,
            message="Object detection completed",
            detections=detections
        )
    except Exception as e:
        logger.error(f"Error detecting objects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/mcp/vision/tracking", response_model=OperationResponse, tags=["camera"])
async def control_tracking(
    command: TrackingCommand,
    auth: bool = Depends(verify_api_key)
):
    """Control object tracking"""
    try:
        return await backend_client.control_tracking(
            command.action, command.drone_id, **command.dict(exclude={"action", "drone_id"})
        )
    except Exception as e:
        logger.error(f"Error controlling tracking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# System Endpoints

@app.get("/mcp/system/status", response_model=SystemStatusResponse, tags=["system"])
async def get_system_status(auth: bool = Depends(verify_api_key)):
    """Get system status"""
    try:
        backend_status = await backend_client.get_system_status()
        
        # Create MCP server status
        from models.system_models import McpServerStatus, BackendSystemStatus, SystemHealth
        
        mcp_status = McpServerStatus(
            status="running",
            uptime=0,  # TODO: Implement uptime tracking
            version=settings.api_version,
            active_connections=0  # TODO: Implement connection tracking
        )
        
        backend_sys_status = BackendSystemStatus(
            connection_status="connected",
            api_endpoint=settings.backend_api_url,
            response_time=None  # TODO: Implement response time tracking
        )
        
        return SystemStatusResponse(
            mcp_server=mcp_status,
            backend_system=backend_sys_status,
            connected_drones=0,  # TODO: Get from backend status
            active_operations=0,  # TODO: Implement operation tracking
            system_health="healthy"
        )
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/mcp/system/health", response_model=HealthResponse, tags=["system"])
async def health_check(auth: bool = Depends(verify_api_key)):
    """Perform health check"""
    try:
        # Check backend health
        backend_health = await backend_client.health_check()
        
        from models.system_models import HealthCheck, CheckStatus
        
        checks = [
            HealthCheck(
                name="MCP Server",
                status="pass",
                message="MCP Server is running",
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
        logger.error(f"Error performing health check: {str(e)}")
        
        from models.system_models import HealthCheck
        checks = [
            HealthCheck(
                name="MCP Server",
                status="pass",
                message="MCP Server is running",
                response_time=None
            ),
            HealthCheck(
                name="Backend API",
                status="fail",
                message=f"Backend API check failed: {str(e)}",
                response_time=None
            )
        ]
        
        return HealthResponse(
            status="unhealthy",
            checks=checks
        )


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "timestamp": datetime.now()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )