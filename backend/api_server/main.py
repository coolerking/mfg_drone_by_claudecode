"""
MFG Drone Backend API Server - Main Application
FastAPI application with drone control, vision, model management, and dashboard APIs
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from .core.drone_manager import DroneManager
from .core.vision_service import VisionService
from .core.dataset_service import DatasetService
from .core.model_service import ModelService
from .core.system_service import SystemService
from .core.alert_service import AlertService
from .core.performance_service import PerformanceService

from .api.drones import router as drones_router
from .api.vision import router as vision_router, initialize_vision_router
from .api.models import router as models_router, initialize_models_router
from .api.dashboard import router as dashboard_router, initialize_dashboard_router
from .api.phase4 import router as phase4_router, initialize_phase4_router
from .api.websocket import (
    manager as websocket_manager, 
    WebSocketHandler, 
    start_status_broadcaster
)
from .security import (
    limiter, 
    get_rate_limiter, 
    SECURITY_HEADERS, 
    security_middleware,
    api_key_manager
)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# グローバル管理インスタンス
drone_manager: DroneManager = None
vision_service: VisionService = None
dataset_service: DatasetService = None
model_service: ModelService = None
system_service: SystemService = None
alert_service: AlertService = None
performance_service: PerformanceService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    global drone_manager, vision_service, dataset_service, model_service, system_service, alert_service, performance_service
    
    # 起動時処理
    logger.info("Starting MFG Drone Backend API Server...")
    
    # Initialize all services
    drone_manager = DroneManager()
    logger.info("Drone Manager initialized")
    
    vision_service = VisionService()
    logger.info("Vision Service initialized")
    
    dataset_service = DatasetService()
    logger.info("Dataset Service initialized")
    
    model_service = ModelService()
    logger.info("Model Service initialized")
    
    system_service = SystemService()
    logger.info("System Service initialized")
    
    # Phase 4: Initialize new services
    alert_service = AlertService()
    logger.info("Alert Service initialized")
    
    performance_service = PerformanceService()
    logger.info("Performance Service initialized")
    
    # Initialize API routers with service instances
    initialize_vision_router(vision_service, dataset_service)
    initialize_models_router(model_service, dataset_service)
    initialize_dashboard_router(system_service, drone_manager, vision_service, model_service, dataset_service)
    initialize_phase4_router(alert_service, performance_service)
    logger.info("API routers initialized")
    
    # WebSocket状態ブロードキャスターを開始
    status_broadcaster_task = asyncio.create_task(start_status_broadcaster(drone_manager))
    logger.info("WebSocket status broadcaster started")
    
    # Phase 4: Start monitoring services
    alert_monitoring_task = asyncio.create_task(alert_service.start_monitoring(30))
    performance_monitoring_task = asyncio.create_task(performance_service.start_monitoring(60))
    logger.info("Phase 4 monitoring services started")
    
    yield
    
    # 終了時処理
    logger.info("Shutting down MFG Drone Backend API Server...")
    
    # 状態ブロードキャスターを停止
    status_broadcaster_task.cancel()
    try:
        await status_broadcaster_task
    except asyncio.CancelledError:
        pass
    
    # Phase 4: Stop monitoring services
    alert_monitoring_task.cancel()
    performance_monitoring_task.cancel()
    try:
        await alert_monitoring_task
        await performance_monitoring_task
    except asyncio.CancelledError:
        pass
    
    # Shutdown all services
    if alert_service:
        await alert_service.shutdown()
    if performance_service:
        await performance_service.shutdown()
    if vision_service:
        await vision_service.shutdown()
    if dataset_service:
        await dataset_service.shutdown()
    if model_service:
        await model_service.shutdown()
    if system_service:
        await system_service.shutdown()
    if drone_manager:
        await drone_manager.shutdown()
    
    logger.info("Server shutdown complete")


# FastAPIアプリケーション作成
app = FastAPI(
    title="MFG Drone Backend API",
    description="""
    Tello EDU ドローンを使った自動追従撮影システムのバックエンドAPI。
    ドローン制御、物体認識・追跡、モデル管理、ダッシュボード機能を提供します。
    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "drones",
            "description": "ドローン制御API"
        },
        {
            "name": "vision",
            "description": "物体認識・追跡API"
        },
        {
            "name": "models",
            "description": "モデル管理API"
        },
        {
            "name": "dashboard",
            "description": "ダッシュボードAPI"
        }
    ]
)

# CORS設定 - Phase 5: Enhanced for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:8080", 
        "https://localhost:3000", 
        "https://localhost:8080",
        "http://localhost:8000",  # For dashboard
        "https://localhost:8000"   # For secure dashboard
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-API-Key"]
)

# Phase 5: Static files for dashboard
dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web_dashboard")
if os.path.exists(dashboard_path):
    app.mount("/static", StaticFiles(directory=dashboard_path), name="static")
    logger.info(f"Dashboard static files mounted from: {dashboard_path}")
else:
    logger.warning(f"Dashboard directory not found: {dashboard_path}")

# Phase 4: Security middleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Add security headers
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    
    return response

# APIルーター登録
app.include_router(drones_router, prefix="/api", tags=["drones"])
app.include_router(vision_router, prefix="/api", tags=["vision"])
app.include_router(models_router, prefix="/api", tags=["models"])
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
app.include_router(phase4_router, prefix="/api", tags=["phase4"])

# WebSocketエンドポイント
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocketエンドポイント
    
    リアルタイムドローン状態更新とコマンド送信用
    """
    websocket_handler = WebSocketHandler(drone_manager)
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # メッセージを受信
            data = await websocket.receive_text()
            
            try:
                import json
                message = json.loads(data)
                await websocket_handler.handle_message(websocket, message)
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message(websocket, {
                    "type": "error",
                    "error_code": "INVALID_JSON",
                    "message": "Invalid JSON format",
                    "timestamp": drone_manager.get_current_timestamp().isoformat() if drone_manager else None
                })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket_manager.send_personal_message(websocket, {
                    "type": "error",
                    "error_code": "MESSAGE_HANDLING_ERROR", 
                    "message": f"Error handling message: {str(e)}",
                    "timestamp": drone_manager.get_current_timestamp().isoformat() if drone_manager else None
                })
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

# 基本ヘルスチェックエンドポイント
@app.get("/")
@limiter.limit("100/minute")
async def root(request):
    """ルートエンドポイント"""
    return {
        "message": "MFG Drone Backend API Server",
        "version": "1.0.0",
        "status": "running",
        "security": "API Key authentication enabled",
        "features": ["drones", "vision", "models", "dashboard", "alerts", "performance"]
    }


@app.get("/health")
@limiter.limit("200/minute")
async def health_check(request):
    """ヘルスチェックエンドポイント"""
    global drone_manager, alert_service, performance_service
    
    health_status = {
        "status": "healthy",
        "timestamp": drone_manager.get_current_timestamp() if drone_manager else None,
        "services": {
            "drone_manager": drone_manager is not None,
            "alert_service": alert_service is not None,
            "performance_service": performance_service is not None,
            "monitoring_active": alert_service.monitoring_active if alert_service else False
        },
        "phase": "Phase 5 - Web Dashboard Ready",
        "security_enabled": True
    }
    
    return health_status


# Phase 5: Dashboard routes
@app.get("/dashboard", response_class=HTMLResponse)
@limiter.limit("50/minute")
async def dashboard(request: Request):
    """ダッシュボードHTMLページを提供"""
    dashboard_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web_dashboard", "index.html")
    
    if os.path.exists(dashboard_file):
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        raise HTTPException(status_code=404, detail="Dashboard not found")


@app.get("/ui", response_class=HTMLResponse)
@limiter.limit("50/minute") 
async def dashboard_ui(request: Request):
    """ダッシュボードUI（/dashboardのエイリアス）"""
    return await dashboard(request)


# エラーハンドラー
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP例外ハンドラー"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "timestamp": drone_manager.get_current_timestamp() if drone_manager else None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """一般例外ハンドラー"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "内部サーバーエラーが発生しました",
            "timestamp": drone_manager.get_current_timestamp() if drone_manager else None
        }
    )


def get_drone_manager() -> DroneManager:
    """ドローンマネージャーインスタンスを取得"""
    global drone_manager
    if drone_manager is None:
        raise HTTPException(status_code=503, detail="Drone manager not initialized")
    return drone_manager


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )