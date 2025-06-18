"""
MFG Drone Backend API Server
Tello EDU ドローン制御・物体認識・追跡システムのバックエンド

Enhanced with MCP (Model Context Protocol) support for AI integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import logging

# Import all routers
from routers import (
    connection_router,
    flight_control_router,
    movement_router,
    advanced_movement_router,
    camera_router,
    sensors_router,
    settings_router,
    mission_pad_router,
    tracking_router,
    model_router,
    mcp_bridge,
)

# Import services for initialization
from services.event_service import initialize_event_service, shutdown_event_service
from services.websocket_service import initialize_websocket_service, shutdown_websocket_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MFG Drone Backend API",
    description="Tello EDU自動追従撮影システム バックエンドAPI with MCP Integration",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(connection_router)
app.include_router(flight_control_router)
app.include_router(movement_router)
app.include_router(advanced_movement_router)
app.include_router(camera_router)
app.include_router(sensors_router)
app.include_router(settings_router)
app.include_router(mission_pad_router)
app.include_router(tracking_router)
app.include_router(model_router)
app.include_router(mcp_bridge.router)  # MCP Bridge router

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        logger.info("Starting MFG Drone Backend API with MCP support...")
        
        # Initialize event service
        await initialize_event_service()
        logger.info("Event service initialized")
        
        # Initialize WebSocket service
        await initialize_websocket_service()
        logger.info("WebSocket service initialized")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown."""
    try:
        logger.info("Shutting down MFG Drone Backend API...")
        
        # Shutdown WebSocket service
        await shutdown_websocket_service()
        logger.info("WebSocket service shut down")
        
        # Shutdown event service
        await shutdown_event_service()
        logger.info("Event service shut down")
        
        logger.info("All services shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    return {
        "message": "MFG Drone Backend API with MCP Integration",
        "version": "1.0.0",
        "features": [
            "Drone Control API",
            "MCP Bridge for AI Integration", 
            "Real-time WebSocket Communication",
            "Event Notification System"
        ],
        "endpoints": {
            "api_docs": "/docs",
            "health": "/health",
            "mcp_bridge": "/mcp",
            "websocket": "/mcp/ws/bridge"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with MCP service status."""
    try:
        from services.event_service import get_event_service
        from services.websocket_service import get_websocket_service
        
        # Get service instances (if available)
        try:
            event_service = get_event_service()
            event_stats = event_service.get_statistics()
            event_status = "healthy"
        except Exception:
            event_stats = None
            event_status = "not_initialized"
        
        try:
            ws_service = get_websocket_service()
            ws_stats = ws_service.get_statistics()
            ws_status = "healthy"
        except Exception:
            ws_stats = None
            ws_status = "not_initialized"
        
        return {
            "status": "healthy",
            "timestamp": "2025-06-18T05:45:00Z",  # Would be dynamic
            "version": "1.0.0",
            "services": {
                "api": {
                    "status": "healthy",
                    "endpoints": 44,  # Number of API endpoints
                },
                "event_service": {
                    "status": event_status,
                    "stats": event_stats,
                },
                "websocket_service": {
                    "status": ws_status,
                    "stats": ws_stats,
                },
                "mcp_bridge": {
                    "status": "healthy",
                    "endpoints": ["/mcp/health", "/mcp/ws/bridge", "/mcp/metrics"],
                }
            },
            "features": {
                "drone_control": True,
                "mcp_integration": True,
                "websocket_support": True,
                "real_time_events": True,
                "performance_monitoring": True,
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": "2025-06-18T05:45:00Z",  # Would be dynamic
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)