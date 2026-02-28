"""
监控数据验证模型

定义监控相关的 Pydantic Schema
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class LogType(str, Enum):
    """日志类型枚举"""
    ERROR = "error"
    PERFORMANCE = "performance"
    EVENT = "event"


class HealthStatus(str, Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# ==================== 健康检查相关 ====================

class DatabaseCheck(BaseModel):
    """数据库检查结果"""
    status: str = Field(..., description="状态: ok/error")
    latency_ms: float = Field(..., description="延迟(毫秒)")


class DiskCheck(BaseModel):
    """磁盘检查结果"""
    status: str = Field(..., description="状态: ok/warning/error")
    used_percent: float = Field(..., description="使用百分比")
    free_gb: float = Field(..., description="剩余空间(GB)")


class MemoryCheck(BaseModel):
    """内存检查结果"""
    status: str = Field(..., description="状态: ok/warning/error")
    used_percent: float = Field(..., description="使用百分比")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: HealthStatus = Field(..., description="整体状态")
    timestamp: datetime = Field(..., description="检查时间")
    checks: dict = Field(..., description="各项检查结果")
    uptime_seconds: float = Field(..., description="运行时间(秒)")
    version: str = Field(..., description="应用版本")


# ==================== 性能统计相关 ====================

class EndpointStats(BaseModel):
    """端点统计"""
    path: str = Field(..., description="接口路径")
    method: str = Field(..., description="HTTP方法")
    count: int = Field(..., description="请求次数")
    avg_ms: float = Field(..., description="平均响应时间(毫秒)")
    max_ms: float = Field(..., description="最大响应时间(毫秒)")
    min_ms: float = Field(..., description="最小响应时间(毫秒)")
    error_count: int = Field(..., description="错误次数")


class SlowRequest(BaseModel):
    """慢请求记录"""
    path: str = Field(..., description="接口路径")
    method: str = Field(..., description="HTTP方法")
    response_time_ms: float = Field(..., description="响应时间(毫秒)")
    timestamp: datetime = Field(..., description="时间")


class PerformanceSummary(BaseModel):
    """性能摘要"""
    total_requests: int = Field(..., description="总请求数")
    avg_response_time_ms: float = Field(..., description="平均响应时间(毫秒)")
    error_rate_percent: float = Field(..., description="错误率(%)")
    slow_requests_count: int = Field(..., description="慢请求数量")


class PerformanceResponse(BaseModel):
    """性能统计响应"""
    period: dict = Field(..., description="统计时间段")
    summary: PerformanceSummary = Field(..., description="性能摘要")
    endpoints: List[EndpointStats] = Field(default_factory=list, description="端点统计")
    slow_requests: List[SlowRequest] = Field(default_factory=list, description="慢请求")


# ==================== 错误日志相关 ====================

class ErrorLogItem(BaseModel):
    """错误日志条目"""
    id: str = Field(..., description="日志ID")
    timestamp: datetime = Field(..., description="时间")
    path: str = Field(..., description="请求路径")
    method: str = Field(..., description="HTTP方法")
    status_code: int = Field(..., description="状态码")
    error_message: str = Field(..., description="错误消息")
    error_stack: Optional[str] = Field(None, description="堆栈信息")
    request_params: Optional[str] = Field(None, description="请求参数")

    class Config:
        from_attributes = True


class ErrorLogResponse(BaseModel):
    """错误日志响应"""
    total: int = Field(..., description="总数")
    items: List[ErrorLogItem] = Field(default_factory=list, description="日志列表")
    pagination: dict = Field(..., description="分页信息")


# ==================== 数据库状态相关 ====================

class TableStats(BaseModel):
    """表统计"""
    name: str = Field(..., description="表名")
    row_count: int = Field(..., description="记录数")
    size_kb: float = Field(..., description="大小(KB)")


class DatabaseResponse(BaseModel):
    """数据库状态响应"""
    status: str = Field(..., description="状态: connected/disconnected")
    latency_ms: float = Field(..., description="连接延迟(毫秒)")
    tables: List[TableStats] = Field(default_factory=list, description="表统计")
    db_size_mb: float = Field(..., description="数据库大小(MB)")


# ==================== 创建日志相关 ====================

class MonitorLogCreate(BaseModel):
    """创建监控日志"""
    log_type: LogType = Field(..., description="日志类型")
    request_id: Optional[str] = Field(None, description="请求ID")
    method: Optional[str] = Field(None, description="HTTP方法")
    path: Optional[str] = Field(None, description="请求路径")
    status_code: Optional[int] = Field(None, description="状态码")
    response_time_ms: Optional[int] = Field(None, description="响应时间(毫秒)")
    error_message: Optional[str] = Field(None, description="错误消息")
    error_stack: Optional[str] = Field(None, description="堆栈信息")
    request_params: Optional[str] = Field(None, description="请求参数")
    user_id: Optional[str] = Field(None, description="用户ID")
    ip_address: Optional[str] = Field(None, description="IP地址")