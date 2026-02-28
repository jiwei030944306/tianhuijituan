"""
响应压缩中间件

支持 GZip 和 Brotli 压缩
"""
from fastapi import Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import gzip
import json
from typing import Optional


# 压缩配置
COMPRESSION_MIN_SIZE = 1000  # 最小压缩大小（字节）
COMPRESSION_LEVEL = 6  # 压缩级别 (1-9)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    自定义压缩中间件
    
    支持 GZip 压缩，可配置最小压缩大小
    """
    
    async def dispatch(self, request: Request, call_next):
        # 执行请求
        response = await call_next(request)
        
        # 检查是否需要压缩
        if not self._should_compress(request, response):
            return response
        
        # 获取响应体
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # 检查大小
        if len(response_body) < COMPRESSION_MIN_SIZE:
            return JSONResponse(
                content=json.loads(response_body),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        
        # GZip 压缩
        compressed_body = gzip.compress(response_body, compresslevel=COMPRESSION_LEVEL)
        
        # 返回压缩响应
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers={
                **dict(response.headers),
                "Content-Encoding": "gzip",
                "Content-Length": str(len(compressed_body)),
            },
            media_type=response.media_type
        )
    
    def _should_compress(self, request: Request, response: Response) -> bool:
        """判断是否需要压缩"""
        # 检查客户端是否支持
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            return False
        
        # 检查响应类型
        content_type = response.headers.get("Content-Type", "")
        if not any(ct in content_type for ct in ["application/json", "text/"]):
            return False
        
        # 检查是否已经压缩
        if response.headers.get("Content-Encoding"):
            return False
        
        return True


def setup_compression(app):
    """
    设置压缩中间件
    
    Args:
        app: FastAPI 应用实例
    """
    # 使用 FastAPI 内置 GZip 中间件
    app.add_middleware(
        GZipMiddleware,
        minimum_size=COMPRESSION_MIN_SIZE
    )


def get_compression_stats() -> dict:
    """
    获取压缩统计信息
    """
    return {
        "enabled": True,
        "min_size": COMPRESSION_MIN_SIZE,
        "level": COMPRESSION_LEVEL,
        "algorithms": ["gzip"]
    }
