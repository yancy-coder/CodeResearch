"""
CoderResearch API - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from routers import codes, import_data, categories, sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="CoderResearch API",
    description="质性研究编码系统 API",
    version="3.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(codes.router, prefix="/api/codes", tags=["codes"])
app.include_router(import_data.router, prefix="/api/import", tags=["import"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "3.0.0"}
