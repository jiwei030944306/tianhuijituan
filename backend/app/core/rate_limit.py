"""
请求限流中间件

简单的内存限流实现（生产环境应使用 Redis）
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict
import time


# 请求计数存储（生产环境应使用 Redis）
request_counts: dict[str, list[float]] = defaultdict(list)

# 限流配置
RATE_LIMIT = 100  # 每分钟最大请求数
TIME_WINDOW = 60  # 时间窗口（秒）


async def rate_limit_middleware(request: Request, call_next):
    """
    请求限流中间件
    
    对每个 IP 进行速率限制
    """
    # 获取客户端 IP
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    
    # 清理过期请求记录
    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if current_time - t < TIME_WINDOW
    ]
    
    # 检查是否超过限制
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "请求过于频繁，请稍后再试"}
        )
    
    # 记录请求
    request_counts[client_ip].append(current_time)
    
    # 继续处理请求
    response = await call_next(request)
    return response


def get_rate_stats() -> dict:
    """
    获取限流统计信息
    """
    return {
        "total_ips": len(request_counts),
        "requests_per_ip": {
            ip: len(requests) 
            for ip, requests in request_counts.items()
        }
    }
