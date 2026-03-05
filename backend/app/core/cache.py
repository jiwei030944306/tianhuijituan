"""
缓存模块

支持 Redis 缓存，当 Redis 不可用时自动降级到内存缓存
"""
import json
import time
from typing import Optional, Any, Callable
from functools import wraps
import os
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 尝试导入 Redis
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# 内存缓存（降级方案）
_memory_cache: dict[str, tuple[Any, float]] = {}

# Redis 客户端
_redis_client: Optional[Any] = None


async def init_cache() -> None:
    """
    初始化缓存客户端

    优先使用 Redis，不可用时降级到内存缓存
    """
    global _redis_client

    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

    if REDIS_AVAILABLE:
        try:
            _redis_client = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # 测试连接
            await _redis_client.ping()
            logger.info("✓ Redis 缓存已连接")
        except Exception as e:
            logger.warning(f"⚠ Redis 连接失败，使用内存缓存: {e}")
            _redis_client = None
    else:
        logger.info("⚠ Redis 未安装，使用内存缓存")


async def close_cache() -> None:
    """关闭缓存连接"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def get_cache(key: str) -> Optional[Any]:
    """
    获取缓存值

    Args:
        key: 缓存键

    Returns:
        缓存值，不存在返回 None
    """
    if _redis_client:
        try:
            value = await _redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")

    # 内存缓存降级
    if key in _memory_cache:
        data, expire_at = _memory_cache[key]
        if time.time() < expire_at:
            return data
        else:
            del _memory_cache[key]

    return None


async def set_cache(key: str, value: Any, ttl: int = 300) -> bool:
    """
    设置缓存

    Args:
        key: 缓存键
        value: 缓存值
        ttl: 过期时间（秒），默认 5 分钟

    Returns:
        是否成功
    """
    if _redis_client:
        try:
            await _redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.warning(f"Redis set error: {e}")

    # 内存缓存降级
    _memory_cache[key] = (value, time.time() + ttl)
    return True


async def delete_cache(key: str) -> bool:
    """
    删除缓存

    Args:
        key: 缓存键

    Returns:
        是否成功
    """
    if _redis_client:
        try:
            await _redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")

    if key in _memory_cache:
        del _memory_cache[key]

    return True


async def clear_cache() -> bool:
    """
    清空所有缓存

    Returns:
        是否成功
    """
    global _memory_cache

    if _redis_client:
        try:
            await _redis_client.flushdb()
            return True
        except Exception as e:
            logger.warning(f"Redis flush error: {e}")

    _memory_cache.clear()
    return True


def cache_result(key_prefix: str, ttl: int = 300):
    """
    缓存装饰器
    
    用法:
        @cache_result("questions_list", ttl=60)
        async def get_questions(...):
            ...
    
    Args:
        key_prefix: 缓存键前缀
        ttl: 过期时间（秒）
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached = await get_cache(cache_key)
            if cached is not None:
                return cached
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            if result is not None:
                await set_cache(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def get_cache_stats() -> dict:
    """
    获取缓存统计信息
    """
    if _redis_client:
        return {
            "type": "redis",
            "connected": True
        }
    
    return {
        "type": "memory",
        "keys": len(_memory_cache),
        "keys_list": list(_memory_cache.keys())[:10]  # 最多显示 10 个
    }
