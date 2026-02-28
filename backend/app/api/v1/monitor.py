"""
监控API路由

提供系统健康检查、性能统计、错误日志、数据库状态等监控接口
"""
import os
import shutil
import time
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.monitor_store import performance_store
from app.crud import monitor as crud_monitor
from app.schemas.monitor import (
    HealthResponse, HealthStatus,
    PerformanceResponse, ErrorLogResponse
)


router = APIRouter()


# ==================== 健康检查 ====================

@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    服务健康检查
    
    检查项目：
    - 数据库连接
    - 磁盘空间
    - 内存使用
    - 服务运行时间
    """
    checks = {}
    overall_status = HealthStatus.HEALTHY
    
    # 数据库检查
    try:
        from app.core.database import AsyncSessionLocal
        start = time.time()
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        latency_ms = (time.time() - start) * 1000
        
        checks["database"] = {
            "status": "ok",
            "latency_ms": round(latency_ms, 2)
        }
    except Exception as e:
        checks["database"] = {
            "status": "error",
            "message": str(e)[:100]
        }
        overall_status = HealthStatus.UNHEALTHY
    
    # 磁盘检查
    try:
        disk_usage = shutil.disk_usage("/")
        used_percent = (disk_usage.used / disk_usage.total) * 100
        free_gb = disk_usage.free / (1024 ** 3)
        
        disk_status = "ok"
        if used_percent > 90:
            disk_status = "error"
            overall_status = HealthStatus.DEGRADED
        elif used_percent > 80:
            disk_status = "warning"
            if overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
        
        checks["disk"] = {
            "status": disk_status,
            "used_percent": round(used_percent, 1),
            "free_gb": round(free_gb, 2)
        }
    except Exception as e:
        checks["disk"] = {
            "status": "error",
            "message": str(e)[:100]
        }
    
    # 内存检查 (简化版，仅Linux)
    try:
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()
        
        # 解析内存信息
        mem_total = 0
        mem_available = 0
        for line in meminfo.split("\n"):
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1])
            elif line.startswith("MemAvailable:"):
                mem_available = int(line.split()[1])
        
        if mem_total > 0:
            used_percent = ((mem_total - mem_available) / mem_total) * 100
            
            mem_status = "ok"
            if used_percent > 90:
                mem_status = "error"
                overall_status = HealthStatus.DEGRADED
            elif used_percent > 80:
                mem_status = "warning"
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            
            checks["memory"] = {
                "status": mem_status,
                "used_percent": round(used_percent, 1)
            }
    except Exception:
        # 非 Linux 系统跳过内存检查
        checks["memory"] = {
            "status": "unknown",
            "message": "Memory check only available on Linux"
        }
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(),
        checks=checks,
        uptime_seconds=performance_store.get_uptime_seconds(),
        version="1.0.0"
    )


# ==================== 性能统计 ====================

@router.get("/performance", response_model=PerformanceResponse)
async def get_performance(
    hours: int = Query(1, ge=1, le=24, description="统计最近N小时")
):
    """
    获取API性能统计
    
    返回：
    - 请求总数、平均响应时间、错误率
    - 各端点的详细统计
    - 慢请求列表
    """
    now = datetime.now()
    start = datetime.fromtimestamp(
        now.timestamp() - hours * 3600
    )
    
    summary = performance_store.get_summary(hours=hours)
    endpoints = performance_store.get_endpoint_stats(hours=hours)
    slow_requests = performance_store.get_slow_requests(threshold_ms=1000, limit=10)
    
    return PerformanceResponse(
        period={
            "start": start.isoformat(),
            "end": now.isoformat()
        },
        summary=summary,
        endpoints=endpoints,
        slow_requests=slow_requests
    )


# ==================== 错误日志 ====================

@router.get("/errors", response_model=ErrorLogResponse)
async def get_errors(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    hours: int = Query(24, ge=1, le=168, description="查询最近N小时"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取错误日志列表
    
    支持分页和时间范围筛选
    """
    total, items = await crud_monitor.get_error_logs(
        db, skip=skip, limit=limit, hours=hours
    )
    
    return ErrorLogResponse(
        total=total,
        items=items,
        pagination={"skip": skip, "limit": limit}
    )


# ==================== 数据库状态 ====================

@router.get("/database")
async def get_database_status(
    db: AsyncSession = Depends(get_db)
):
    """
    获取数据库状态

    返回：
    - 连接状态
    - 各表记录数和大小
    - 数据库总大小
    """
    import time

    # 测量连接延迟
    start = time.time()
    try:
        await db.execute(text("SELECT 1"))
        latency_ms = (time.time() - start) * 1000
        status = "connected"
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e)[:100],
            "latency_ms": 0,
            "tables": [],
            "db_size_mb": 0
        }

    # 获取表统计
    tables = []
    try:
        # PostgreSQL 查询表信息
        result = await db.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """))
        table_names = [row[0] for row in result.fetchall()]

        for table_name in table_names:
            # 获取记录数
            count_result = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = count_result.scalar() or 0

            tables.append({
                "name": table_name,
                "row_count": row_count,
                "size_kb": 0  # 可通过 pg_relation_size 获取
            })
    except Exception:
        pass

    # 获取数据库大小
    db_size_mb = 0
    try:
        size_result = await db.execute(text(
            "SELECT pg_database_size(current_database()) / 1024 / 1024"
        ))
        db_size_mb = size_result.scalar() or 0
    except Exception:
        pass

    return {
        "status": status,
        "latency_ms": round(latency_ms, 2),
        "tables": tables,
        "db_size_mb": round(float(db_size_mb), 2)
    }


# ==================== 清理日志 ====================

@router.delete("/logs/clear")
async def clear_old_logs(
    days: int = Query(7, ge=1, le=30, description="保留最近N天的日志"),
    db: AsyncSession = Depends(get_db)
):
    """
    清理过期日志
    """
    deleted_count = await crud_monitor.clear_old_logs(db, days=days)
    
    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"已删除 {deleted_count} 条超过 {days} 天的日志"
    }