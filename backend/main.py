"""
MFG Drone Backend API Server
Tello EDU ドローン制御・物体認識・追跡システムのバックエンド
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ルーターのインポート
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
)
from dependencies import get_health_info

# FastAPIアプリケーション作成
app = FastAPI(
    title="MFG Drone Backend API",
    description="Tello EDU自動追従撮影システム バックエンドAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では具体的なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
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

# ルートエンドポイント
@app.get("/")
async def root():
    """
    ルートエンドポイント
    
    Returns:
        dict: APIメッセージ
    """
    return {"message": "MFG Drone Backend API"}

@app.get("/health")
async def health_check():
    """
    ヘルスチェック
    
    Returns:
        dict: システム状態情報
    """
    return get_health_info()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)