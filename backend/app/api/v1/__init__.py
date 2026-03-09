"""
API v1版本主路由入口

整合所有v1版本的路由模块
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    base,
    db_explorer,
    images,
    logs,
    monitor,
    statistics,
    upload,
)

# 创建v1版本路由器
api_v1_router = APIRouter(prefix="/api/v1")

# 注册各模块路由
api_v1_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

api_v1_router.include_router(
    base.router,
    prefix="/questions",
    tags=["题目-基础"]
)

api_v1_router.include_router(
    images.router,
    prefix="/images",
    tags=["图片服务"]
)

api_v1_router.include_router(
    logs.router,
    prefix="/logs",
    tags=["日志"]
)

api_v1_router.include_router(
    statistics.router,
    prefix="/statistics",
    tags=["统计数据"]
)

api_v1_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["文件上传"]
)

api_v1_router.include_router(
    monitor.router,
    prefix="/monitor",
    tags=["系统监控"]
)

api_v1_router.include_router(
    db_explorer.router,
    prefix="/db-explorer",
    tags=["数据库查询"]
)