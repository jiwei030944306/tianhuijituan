"""
请求日志中间件

自动记录所有请求的性能指标和错误日志
"""
import time
import uuid
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.monitor_store import PerformanceStore, RequestMetric
from app.schemas.monitor import MonitorLogCreate, LogType


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    
    功能：
    - 记录每个请求的响应时间
    - 自动捕获错误并记录
    - 存储到内存用于实时统计
    """
    
    # 不记录的路径（健康检查等）
    SKIP_PATHS = {
        "/health",
        "/api/v1/monitor/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico",
    }
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.store = PerformanceStore()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # 跳过不需要记录的路径
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 记录开始时间
        start_time = time.time()
        
        # 初始化错误信息
        error_message = None
        status_code = 200
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
            
        except Exception as e:
            # 捕获未处理的异常
            status_code = 500
            error_message = str(e)
            raise
            
        finally:
            # 计算响应时间
            response_time_ms = (time.time() - start_time) * 1000
            
            # 创建性能指标
            metric = RequestMetric(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(),
                error_message=error_message
            )
            
            # 存储到内存
            self.store.record(metric)


# 导出中间件实例
request_logging_middleware = RequestLoggingMiddleware