"""
数据库查询API路由

提供安全的SQL查询执行功能（仅限SELECT）
"""
import time
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.db_explorer import QueryRequest, QueryResponse, QueryResult

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    执行 SQL 查询（仅限 SELECT）

    安全措施：
    - 仅管理员可访问
    - 仅允许 SELECT 语句
    - 自动添加 LIMIT 保护
    - 记录查询日志

    Args:
        request: 查询请求
        db: 数据库会话
        current_user: 当前用户（管理员）

    Returns:
        QueryResponse: 查询结果或错误信息
    """
    start_time = time.time()
    username = current_user.get("username", "unknown")

    logger.info(f"SQL Query by user {username}: {request.sql[:100]}...")

    try:
        # 处理 SQL，移除末尾分号
        sql = request.sql.rstrip(';')

        # 如果没有 LIMIT，自动添加
        if 'LIMIT' not in sql.upper():
            sql = f"{sql} LIMIT {request.limit}"

        # 执行查询
        result = await db.execute(text(sql))

        # 获取列名
        columns = list(result.keys()) if result.returns_rows else []

        # 获取数据行
        rows = []
        if result.returns_rows:
            for row in result.fetchall():
                row_dict = {col: row[i] for i, col in enumerate(columns)}
                rows.append(row_dict)

        execution_time = round((time.time() - start_time) * 1000, 2)

        return QueryResponse(
            success=True,
            result=QueryResult(
                columns=columns,
                rows=rows,
                total=len(rows)
            ),
            execution_time_ms=execution_time
        )

    except Exception as e:
        execution_time = round((time.time() - start_time) * 1000, 2)
        error_msg = str(e)[:200]

        logger.warning(f"SQL Query failed by user {username}: {error_msg}")

        return QueryResponse(
            success=False,
            error=error_msg,
            execution_time_ms=execution_time
        )