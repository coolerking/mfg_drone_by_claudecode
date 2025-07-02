"""
MFG Drone Backend API Server - Main Application
FastAPI application with drone control, vision, model management, and dashboard APIs
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.drone_manager import DroneManager
from .core.vision_service import VisionService
from .core.dataset_service import DatasetService
from .core.model_service import ModelService
from .core.system_service import SystemService

from .api.drones import router as drones_router
from .api.vision import router as vision_router, initialize_vision_router
from .api.models import router as models_router, initialize_models_router
from .api.dashboard import router as dashboard_router, initialize_dashboard_router
from .api.websocket import (
    manager as websocket_manager, 
    WebSocketHandler, 
    start_status_broadcaster
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    global drone_manager, vision_service, dataset_service, model_service, system_service
    
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
    
    # Initialize API routers with service instances
    initialize_vision_router(vision_service, dataset_service)
    initialize_models_router(model_service, dataset_service)
    initialize_dashboard_router(system_service, drone_manager, vision_service, model_service, dataset_service)
    logger.info("API routers initialized")
    
    # WebSocket状態ブロードキャスターを開始
    status_broadcaster_task = asyncio.create_task(start_status_broadcaster(drone_manager))
    logger.info("WebSocket status broadcaster started")
    
    yield
    
    # 終了時処理
    logger.info("Shutting down MFG Drone Backend API Server...")
    
    # 状態ブロードキャスターを停止
    status_broadcaster_task.cancel()
    try:
        await status_broadcaster_task
    except asyncio.CancelledError:
        pass
    
    # Shutdown all services
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

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーター登録
app.include_router(drones_router, prefix="/api", tags=["drones"])
app.include_router(vision_router, prefix="/api", tags=["vision"])
app.include_router(models_router, prefix="/api", tags=["models"])
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])

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
async def root():
    """ルートエンドポイント"""
    return {
        "message": "MFG Drone Backend API Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    global drone_manager
    
    health_status = {
        "status": "healthy",
        "timestamp": drone_manager.get_current_timestamp() if drone_manager else None,
        "services": {
            "drone_manager": drone_manager is not None
        }
    }
    
    return health_status


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