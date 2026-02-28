"""
性能数据内存存储

用于存储最近的请求性能指标，支持快速统计查询
"""
from collections import deque
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
import threading
import time


@dataclass
class RequestMetric:
    """请求性能指标"""
    request_id: str
    method: str
    path: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    error_message: Optional[str] = None


@dataclass
class EndpointStats:
    """端点统计"""
    path: str
    method: str
    count: int = 0
    total_ms: float = 0.0
    max_ms: float = 0.0
    min_ms: float = float('inf')
    error_count: int = 0
    
    @property
    def avg_ms(self) -> float:
        return self.total_ms / self.count if self.count > 0 else 0.0


class PerformanceStore:
    """
    性能数据存储
    
    特点：
    - 线程安全
    - 内存存储，快速查询
    - 自动清理过期数据
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._requests: deque[RequestMetric] = deque(maxlen=1000)  # 最近1000次请求
        self._endpoint_stats: dict[str, EndpointStats] = {}
        self._data_lock = threading.Lock()
        self._start_time = time.time()
    
    def record(self, metric: RequestMetric) -> None:
        """
        记录请求性能指标
        """
        with self._data_lock:
            # 添加到请求队列
            self._requests.append(metric)
            
            # 更新端点统计
            key = f"{metric.method}:{metric.path}"
            if key not in self._endpoint_stats:
                self._endpoint_stats[key] = EndpointStats(
                    path=metric.path,
                    method=metric.method
                )
            
            stats = self._endpoint_stats[key]
            stats.count += 1
            stats.total_ms += metric.response_time_ms
            stats.max_ms = max(stats.max_ms, metric.response_time_ms)
            stats.min_ms = min(stats.min_ms, metric.response_time_ms)
            
            if metric.status_code >= 400:
                stats.error_count += 1
    
    def get_summary(self, hours: int = 1) -> dict:
        """
        获取性能摘要
        """
        with self._data_lock:
            cutoff = datetime.now() - timedelta(hours=hours)
            
            # 过滤时间范围内的请求
            recent_requests = [
                r for r in self._requests 
                if r.timestamp >= cutoff
            ]
            
            if not recent_requests:
                return {
                    "total_requests": 0,
                    "avg_response_time_ms": 0.0,
                    "error_rate_percent": 0.0,
                    "slow_requests_count": 0
                }
            
            total = len(recent_requests)
            total_time = sum(r.response_time_ms for r in recent_requests)
            errors = sum(1 for r in recent_requests if r.status_code >= 400)
            slow = sum(1 for r in recent_requests if r.response_time_ms > 1000)  # 超过1秒为慢请求
            
            return {
                "total_requests": total,
                "avg_response_time_ms": round(total_time / total, 2),
                "error_rate_percent": round(errors / total * 100, 2) if total > 0 else 0.0,
                "slow_requests_count": slow
            }
    
    def get_endpoint_stats(self, hours: int = 1) -> list[dict]:
        """
        获取端点统计列表
        """
        with self._data_lock:
            cutoff = datetime.now() - timedelta(hours=hours)
            
            # 重新计算时间范围内的统计
            result = []
            for key, stats in self._endpoint_stats.items():
                # 过滤该端点在时间范围内的请求
                endpoint_requests = [
                    r for r in self._requests
                    if r.timestamp >= cutoff 
                    and r.method == stats.method 
                    and r.path == stats.path
                ]
                
                if not endpoint_requests:
                    continue
                
                total_time = sum(r.response_time_ms for r in endpoint_requests)
                errors = sum(1 for r in endpoint_requests if r.status_code >= 400)
                
                result.append({
                    "path": stats.path,
                    "method": stats.method,
                    "count": len(endpoint_requests),
                    "avg_ms": round(total_time / len(endpoint_requests), 2),
                    "max_ms": round(max(r.response_time_ms for r in endpoint_requests), 2),
                    "min_ms": round(min(r.response_time_ms for r in endpoint_requests), 2),
                    "error_count": errors
                })
            
            # 按请求数排序
            result.sort(key=lambda x: x["count"], reverse=True)
            return result
    
    def get_slow_requests(self, threshold_ms: float = 1000, limit: int = 10) -> list[dict]:
        """
        获取慢请求列表
        """
        with self._data_lock:
            slow = [
                {
                    "path": r.path,
                    "method": r.method,
                    "response_time_ms": round(r.response_time_ms, 2),
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self._requests
                if r.response_time_ms >= threshold_ms
            ]
            
            # 按响应时间排序
            slow.sort(key=lambda x: x["response_time_ms"], reverse=True)
            return slow[:limit]
    
    def get_uptime_seconds(self) -> float:
        """
        获取服务运行时间（秒）
        """
        return time.time() - self._start_time
    
    def clear(self) -> None:
        """
        清空所有数据
        """
        with self._data_lock:
            self._requests.clear()
            self._endpoint_stats.clear()


# 全局单例
performance_store = PerformanceStore()