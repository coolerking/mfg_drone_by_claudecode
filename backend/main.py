"""
MFG Drone Backend API Server
Tello EDU ドローン制御・物体認識・追跡システムのバックエンド
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from routers import system, connection, flight_control, movement, sensors

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

# Include routers
app.include_router(system.router)
app.include_router(connection.router)
app.include_router(flight_control.router)
app.include_router(movement.router)
app.include_router(sensors.router)

@app.get("/")
async def root():
    return {"message": "MFG Drone Backend API", "status": "running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)