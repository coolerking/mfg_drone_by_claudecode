"""
Phase 4 Enhanced MCP Server
Advanced camera and vision features with OpenCV integration and enhanced natural language processing
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import existing modules
from .core.enhanced_nlp_engine import EnhancedNLPEngine
from .core.enhanced_command_router import EnhancedCommandRouter
from .core.backend_client import BackendClient
from .core.phase4_vision_processor import Phase4VisionProcessor

# Import API routers
from .api.phase4_vision import router as phase4_vision_router

# Import models
from .models.command_models import (
    NaturalLanguageCommand, CommandResponse, BatchCommand, BatchCommandResponse
)
from .models.phase4_vision_models import (
    VisionCommandAnalysis, BatchVisionCommand, BatchVisionResult
)
from .models.drone_models import OperationResponse
from .models.system_models import SystemStatusResponse, HealthResponse

# Import configuration
from config.settings import settings
from config.logging import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Server - Phase 4 Enhanced",
    description="Phase 4 Enhanced MCP Server with advanced camera and vision capabilities",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
enhanced_nlp_engine: EnhancedNLPEngine = None
enhanced_command_router: EnhancedCommandRouter = None
backend_client: BackendClient = None
vision_processor: Phase4VisionProcessor = None

# API Key verification
async def verify_api_key():
    """Verify API key for protected endpoints"""
    # For development, we'll skip API key verification
    # In production, implement proper API key validation
    return True


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global enhanced_nlp_engine, enhanced_command_router, backend_client, vision_processor
    
    try:
        logger.info("Starting MCP Server Phase 4...")
        
        # Initialize backend client
        backend_client = BackendClient()
        
        # Initialize enhanced NLP engine
        enhanced_nlp_engine = EnhancedNLPEngine()
        
        # Initialize enhanced command router
        enhanced_command_router = EnhancedCommandRouter(enhanced_nlp_engine, backend_client)
        
        # Initialize Phase 4 vision processor
        vision_processor = Phase4VisionProcessor(enhanced_nlp_engine, backend_client)
        
        logger.info("MCP Server Phase 4 started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start MCP Server Phase 4: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global backend_client
    
    try:
        logger.info("Shutting down MCP Server Phase 4...")
        
        if backend_client:
            await backend_client.close()
        
        logger.info("MCP Server Phase 4 shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Include Phase 4 vision router
app.include_router(phase4_vision_router)


# ===== Enhanced Command Processing Endpoints =====

@app.post("/mcp/command/vision/analyze", response_model=VisionCommandAnalysis, tags=["phase4-commands"])
async def analyze_vision_command(
    command: str = Body(..., description="Natural language vision command"),
    auth: bool = Depends(verify_api_key)
):
    """
    Analyze vision command and provide detailed analysis
    
    ビジョンコマンドを分析し、詳細な解析結果を提供
    """
    try:
        analysis = await vision_processor.analyze_vision_command(command)
        logger.info(f"Vision command analyzed: {analysis.detected_intent} (confidence: {analysis.confidence:.3f})")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing vision command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/command/vision/execute", response_model=CommandResponse, tags=["phase4-commands"])
async def execute_vision_command(
    command: str = Body(..., description="Natural language vision command"),
    analyze: bool = Body(default=True, description="Enable detailed analysis"),
    auto_optimize: bool = Body(default=True, description="Enable automatic optimization"),
    auth: bool = Depends(verify_api_key)
):
    """
    Execute vision command with enhanced processing
    
    強化された処理によるビジョンコマンド実行
    """
    try:
        start_time = datetime.now()
        
        # Analyze command if requested
        analysis = None
        if analyze:
            analysis = await vision_processor.analyze_vision_command(command)
        
        # Execute using enhanced command router
        nl_command = NaturalLanguageCommand(
            command=command,
            options={"auto_optimize": auto_optimize, "vision_mode": True}
        )
        
        result = await enhanced_command_router.route_command_enhanced(nl_command)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Enhance response with vision analysis
        enhanced_result = {
            **result.dict(),
            "vision_analysis": analysis.dict() if analysis else None,
            "execution_time": execution_time,
            "phase4_enhanced": True
        }
        
        logger.info(f"Vision command executed successfully in {execution_time:.3f}s")
        return CommandResponse(**enhanced_result)
        
    except Exception as e:
        logger.error(f"Error executing vision command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/command/vision/batch", response_model=BatchVisionResult, tags=["phase4-commands"])
async def execute_batch_vision_commands(
    batch_request: BatchVisionCommand,
    auth: bool = Depends(verify_api_key)
):
    """
    Execute multiple vision commands in batch with advanced optimization
    
    高度な最適化による複数ビジョンコマンドのバッチ実行
    """
    try:
        result = await vision_processor.process_batch_vision_commands(batch_request)
        
        logger.info(f"Batch vision commands executed: {result.performance_metrics.get('successful_commands', 0)}/{len(batch_request.commands)} successful")
        return result
        
    except Exception as e:
        logger.error(f"Error executing batch vision commands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Enhanced Command Suggestions =====

@app.post("/mcp/command/vision/suggestions", response_model=Dict[str, Any], tags=["phase4-commands"])
async def get_vision_command_suggestions(
    partial_command: str = Body(..., description="Partial command text"),
    max_suggestions: int = Body(default=5, description="Maximum number of suggestions"),
    auth: bool = Depends(verify_api_key)
):
    """
    Get intelligent vision command suggestions
    
    インテリジェントなビジョンコマンド提案を取得
    """
    try:
        # Generate suggestions based on partial command
        suggestions = await _generate_vision_suggestions(partial_command, max_suggestions)
        
        return {
            "partial_command": partial_command,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error generating vision suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_vision_suggestions(partial_command: str, max_suggestions: int) -> List[Dict[str, Any]]:
    """Generate vision command suggestions"""
    suggestions = []
    
    # Basic suggestions based on partial command
    vision_commands = [
        {
            "command": "ドローンAAで写真を撮って",
            "description": "Take a photo with drone AA",
            "category": "camera",
            "complexity": "simple"
        },
        {
            "command": "物体を検出して追跡を開始して",
            "description": "Detect objects and start tracking",
            "category": "vision",
            "complexity": "advanced"
        },
        {
            "command": "学習データを多角度で収集して",
            "description": "Collect learning data from multiple angles",
            "category": "learning",
            "complexity": "complex"
        },
        {
            "command": "高画質でストリーミングを開始して",
            "description": "Start high-quality streaming",
            "category": "streaming",
            "complexity": "simple"
        },
        {
            "command": "ビジョンシステムの分析を表示して",
            "description": "Display vision system analytics",
            "category": "analytics",
            "complexity": "simple"
        }
    ]
    
    # Filter suggestions based on partial command
    partial_lower = partial_command.lower()
    
    for cmd in vision_commands[:max_suggestions]:
        if any(word in cmd["command"].lower() for word in partial_lower.split()):
            suggestions.append(cmd)
    
    # If no matches, return most relevant suggestions
    if not suggestions:
        suggestions = vision_commands[:max_suggestions]
    
    return suggestions


# ===== Enhanced System Status =====

@app.get("/mcp/system/status/phase4", response_model=Dict[str, Any], tags=["phase4-system"])
async def get_phase4_system_status(auth: bool = Depends(verify_api_key)):
    """
    Get Phase 4 enhanced system status
    
    Phase 4強化版システムステータスを取得
    """
    try:
        # Get vision analytics
        vision_analytics = await backend_client._request("GET", "/api/vision/analytics")
        
        # Get enhanced NLP engine status
        nlp_status = {
            "total_commands_processed": enhanced_nlp_engine.total_commands_processed,
            "average_confidence": enhanced_nlp_engine.total_confidence / max(enhanced_nlp_engine.total_commands_processed, 1),
            "context_memory_size": len(enhanced_nlp_engine.context_memory),
            "conversation_history_size": len(enhanced_nlp_engine.conversation_history)
        }
        
        # Get enhanced command router status
        router_stats = enhanced_command_router.get_execution_statistics()
        
        status = {
            "phase4_status": "active",
            "enhanced_features": [
                "Advanced Vision Processing",
                "OpenCV Integration",
                "Enhanced Learning Data Collection",
                "Intelligent Command Analysis",
                "Batch Command Optimization"
            ],
            "vision_analytics": vision_analytics,
            "nlp_engine_status": nlp_status,
            "command_router_stats": router_stats,
            "uptime": (datetime.now() - datetime.now()).total_seconds(),  # TODO: Implement proper uptime
            "timestamp": datetime.now()
        }
        
        logger.debug("Phase 4 system status retrieved")
        return status
        
    except Exception as e:
        logger.error(f"Error getting Phase 4 system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Legacy Compatibility Endpoints =====

@app.post("/mcp/command", response_model=CommandResponse, tags=["legacy-compatibility"])
async def execute_command_legacy(
    command: NaturalLanguageCommand,
    auth: bool = Depends(verify_api_key)
):
    """
    Legacy command execution with Phase 4 enhancements
    
    Phase 4強化版によるレガシーコマンド実行
    """
    try:
        # Use enhanced router for legacy commands
        result = await enhanced_command_router.route_command_enhanced(command)
        
        # Add Phase 4 enhancement indicator
        enhanced_result = result.dict()
        enhanced_result["phase4_enhanced"] = True
        
        return CommandResponse(**enhanced_result)
        
    except Exception as e:
        logger.error(f"Error executing legacy command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/command/batch", response_model=BatchCommandResponse, tags=["legacy-compatibility"])
async def execute_batch_commands_legacy(
    batch_command: BatchCommand,
    auth: bool = Depends(verify_api_key)
):
    """
    Legacy batch command execution with Phase 4 enhancements
    
    Phase 4強化版によるレガシーバッチコマンド実行
    """
    try:
        # Convert to Phase 4 batch format
        vision_batch = BatchVisionCommand(
            commands=[cmd.command for cmd in batch_command.commands],
            execution_mode="optimized" if batch_command.execution_mode == "parallel" else "sequential",
            error_recovery="continue" if not batch_command.stop_on_error else "stop"
        )
        
        result = await vision_processor.process_batch_vision_commands(vision_batch)
        
        # Convert back to legacy format
        legacy_results = []
        for i, cmd_result in enumerate(result.results):
            legacy_results.append(CommandResponse(
                success=cmd_result.get("success", False),
                message=cmd_result.get("message", "Command executed"),
                parsed_intent={"action": cmd_result.get("action", "unknown")},
                execution_details={"phase4_enhanced": True},
                timestamp=datetime.now()
            ))
        
        return BatchCommandResponse(
            success=result.success,
            message="Batch commands executed with Phase 4 enhancements",
            results=legacy_results,
            summary={
                "total_commands": len(batch_command.commands),
                "successful_commands": result.performance_metrics.get("successful_commands", 0),
                "failed_commands": result.performance_metrics.get("failed_commands", 0),
                "total_execution_time": result.total_execution_time
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error executing legacy batch commands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Root Endpoint =====

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint"""
    return {
        "name": "MCP Server - Phase 4 Enhanced",
        "version": "4.0.0",
        "status": "running",
        "features": [
            "Advanced Camera & Vision Processing",
            "OpenCV Integration",
            "Enhanced Learning Data Collection",
            "Intelligent Natural Language Processing",
            "Batch Command Optimization",
            "Real-time Object Detection & Tracking"
        ],
        "phase": 4,
        "timestamp": datetime.now()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "phase4_main:app",
        host=settings.host,
        port=settings.port + 1,  # Use different port for Phase 4
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )