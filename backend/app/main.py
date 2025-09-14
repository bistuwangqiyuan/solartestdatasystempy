"""
FastAPI主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import db_client
from app.api.v1 import api_router
from app.websocket import websocket_router


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add("logs/app_{time}.log", rotation="500 MB", retention="30 days")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting up application...")
    
    # 初始化数据库
    try:
        await db_client.init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    yield
    
    # 关闭时执行
    logger.info("Shutting down application...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    openapi_url="/api/v1/openapi.json" if settings.debug else None,
    docs_url="/api/v1/docs" if settings.debug else None,
    redoc_url="/api/v1/redoc" if settings.debug else None,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

# 注册WebSocket路由
app.include_router(websocket_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/api/v1/docs" if settings.debug else None
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        db_client.client.table("test_records").select("id").limit(1).execute()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "components": {
            "api": "healthy",
            "database": db_status
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )