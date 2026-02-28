"""
监控日志CRUD操作
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.monitor_log import MonitorLog
from app.schemas.monitor import MonitorLogCreate, LogType


async def create_log(
    db: AsyncSession,
    log_data: MonitorLogCreate
) -> MonitorLog:
    """
    创建监控日志
    """
    log_id = str(uuid.uuid4())
    
    db_log = MonitorLog(
        id=log_id,
        log_type=log_data.log_type.value,
        request_id=log_data.request_id,
        method=log_data.method,
        path=log_data.path,
        status_code=log_data.status_code,
        response_time_ms=log_data.response_time_ms,
        error_message=log_data.error_message,
        error_stack=log_data.error_stack,
        request_params=log_data.request_params,
        user_id=log_data.user_id,
        ip_address=log_data.ip_address,
    )
    
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


async def get_error_logs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    hours: int = 24
) -> tuple[int, List[MonitorLog]]:
    """
    获取错误日志列表
    
    Args:
        db: 数据库会话
        skip: 跳过记录数
        limit: 返回记录数
        hours: 查询最近N小时的日志
    
    Returns:
        (总数, 日志列表)
    """
    # 计算时间范围
    start_time = datetime.now() - timedelta(hours=hours)
    
    # 查询总数
    count_query = select(func.count()).select_from(MonitorLog).where(
        MonitorLog.log_type == LogType.ERROR.value,
        MonitorLog.created_at >= start_time
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 查询列表
    query = select(MonitorLog).where(
        MonitorLog.log_type == LogType.ERROR.value,
        MonitorLog.created_at >= start_time
    ).order_by(MonitorLog.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    logs = list(result.scalars().all())
    
    return total, logs


async def get_log_by_id(
    db: AsyncSession,
    log_id: str
) -> Optional[MonitorLog]:
    """
    获取单条日志详情
    """
    result = await db.execute(
        select(MonitorLog).where(MonitorLog.id == log_id)
    )
    return result.scalar_one_or_none()


async def clear_old_logs(
    db: AsyncSession,
    days: int = 7
) -> int:
    """
    清理过期日志
    
    Args:
        db: 数据库会话
        days: 保留最近N天的日志
    
    Returns:
        删除的记录数
    """
    cutoff_time = datetime.now() - timedelta(days=days)
    
    stmt = delete(MonitorLog).where(MonitorLog.created_at < cutoff_time)
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount


async def get_log_stats(
    db: AsyncSession,
    hours: int = 24
) -> dict:
    """
    获取日志统计
    """
    start_time = datetime.now() - timedelta(hours=hours)
    
    # 按类型统计
    type_query = select(
        MonitorLog.log_type,
        func.count(MonitorLog.id).label('count')
    ).where(
        MonitorLog.created_at >= start_time
    ).group_by(MonitorLog.log_type)
    
    type_result = await db.execute(type_query)
    type_stats = {row.log_type: row.count for row in type_result.all()}
    
    # 按状态码统计（仅错误）
    status_query = select(
        MonitorLog.status_code,
        func.count(MonitorLog.id).label('count')
    ).where(
        MonitorLog.log_type == LogType.ERROR.value,
        MonitorLog.created_at >= start_time
    ).group_by(MonitorLog.status_code)
    
    status_result = await db.execute(status_query)
    status_stats = {str(row.status_code): row.count for row in status_result.all()}
    
    return {
        "by_type": type_stats,
        "by_status_code": status_stats
    }