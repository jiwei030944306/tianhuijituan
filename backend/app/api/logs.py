"""
日志API路由 - 接收前端日志上报
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/logs", tags=["logs"])


class LogUserInfo(BaseModel):
    """用户信息"""
    userId: Optional[str] = None
    userName: Optional[str] = None
    folderCode: Optional[str] = None


class LogEnvironment(BaseModel):
    """环境信息"""
    userAgent: str
    url: str
    timestamp: str


class DebugEntry(BaseModel):
    """调试日志条目"""
    id: str
    timestamp: str
    level: str
    stage: str
    message: str
    details: Optional[Any] = None
    duration: Optional[int] = None


class LogReportRequest(BaseModel):
    """日志上报请求"""
    logs: List[DebugEntry]
    userInfo: LogUserInfo
    environment: LogEnvironment


class LogReportResponse(BaseModel):
    """日志上报响应"""
    success: bool
    message: str


@router.post("/report", response_model=LogReportResponse)
async def report_logs(request: LogReportRequest):
    """
    接收前端日志上报

    Args:
        request: 日志上报请求，包含日志列表、用户信息、环境信息

    Returns:
        LogReportResponse: 上报结果
    """
    try:
        # 记录日志上报信息
        logger.info(
            f"收到日志上报: 用户={request.userInfo.userName}, "
            f"文件夹={request.userInfo.folderCode}, "
            f"日志数量={len(request.logs)}"
        )

        # 统计各级别日志数量
        level_counts = {}
        for log in request.logs:
            level = log.level
            level_counts[level] = level_counts.get(level, 0) + 1

        # 记录统计信息
        logger.info(
            f"日志级别统计: {level_counts}, "
            f"环境={request.environment.userAgent[:50]}..."
        )

        # 记录 error 和 warning 级别的日志
        error_count = level_counts.get('error', 0)
        warning_count = level_counts.get('warning', 0)

        if error_count > 0:
            logger.error(
                f"发现 {error_count} 条错误日志，"
                f"用户={request.userInfo.userName}, "
                f"文件夹={request.userInfo.folderCode}"
            )

        if warning_count > 0:
            logger.warning(
                f"发现 {warning_count} 条警告日志，"
                f"用户={request.userInfo.userName}, "
                f"文件夹={request.userInfo.folderCode}"
            )

        # 这里可以添加将日志保存到数据库的逻辑
        # 目前仅记录到服务器日志文件

        return LogReportResponse(
            success=True,
            message=f"已接收 {len(request.logs)} 条日志，"
                   f"其中错误 {error_count} 条，警告 {warning_count} 条"
        )

    except Exception as e:
        logger.error(f"处理日志上报失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"日志上报失败: {str(e)}")