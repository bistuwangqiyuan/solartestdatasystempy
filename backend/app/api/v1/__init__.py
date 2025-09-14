"""
API v1路由聚合
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, test_records, devices, imports, statistics

api_router = APIRouter()

# 注册各个端点路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(test_records.router, prefix="/records", tags=["测试记录"])
api_router.include_router(devices.router, prefix="/devices", tags=["设备管理"])
api_router.include_router(imports.router, prefix="/imports", tags=["数据导入"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["统计分析"])