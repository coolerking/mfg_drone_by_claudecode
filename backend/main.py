"""
MFG Drone Backend API Server
Tello EDU ドローン制御・物体認識・追跡システムのバックエンド
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
)

app = FastAPI(
    title="MFG Drone Backend API",
    description="Tello EDU自動追従撮影システム バックエンドAPI",
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

@app.get("/")
async def root():
    return {"message": "MFG Drone Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)