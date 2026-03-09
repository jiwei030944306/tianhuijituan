"""
数据库查询相关Pydantic模型
用于请求和响应的数据验证
"""

from typing import List, Any, Optional
from pydantic import BaseModel, Field, field_validator
import re


class QueryRequest(BaseModel):
    """
    SQL查询请求模型

    用于执行SQL SELECT查询的数据验证

    Attributes:
        sql: SQL查询语句（仅限SELECT）
        limit: 返回结果数量限制
    """
    sql: str = Field(..., min_length=1, max_length=10000, description="SQL查询语句")
    limit: int = Field(default=100, ge=1, le=1000, description="返回结果数量限制")

    @field_validator('sql')
    @classmethod
    def validate_sql(cls, v: str) -> str:
        """验证 SQL 只允许 SELECT 查询"""
        sql_upper = v.strip().upper()

        # 必须以 SELECT 开头
        if not sql_upper.startswith('SELECT'):
            raise ValueError('只允许执行 SELECT 查询')

        # 禁止的关键字
        forbidden_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE',
            'ALTER', 'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
        ]

        for keyword in forbidden_keywords:
            if re.search(rf'\b{keyword}\b', sql_upper):
                raise ValueError(f'禁止使用 {keyword} 关键字')

        # 禁止多条语句
        statements = [s.strip() for s in v.split(';') if s.strip()]
        if len(statements) > 1:
            raise ValueError('禁止执行多条 SQL 语句')

        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "sql": "SELECT * FROM questions LIMIT 10",
                "limit": 100
            }
        }


class QueryResult(BaseModel):
    """
    查询结果模型

    Attributes:
        columns: 列名列表
        rows: 数据行列表
        total: 总行数
        truncated: 是否被截断
    """
    columns: List[str] = Field(..., description="列名列表")
    rows: List[dict] = Field(default_factory=list, description="数据行列表")
    total: int = Field(..., ge=0, description="总行数")
    truncated: bool = Field(default=False, description="是否被截断")


class QueryResponse(BaseModel):
    """
    查询响应模型

    Attributes:
        success: 是否成功
        result: 查询结果（成功时）
        error: 错误信息（失败时）
        execution_time_ms: 执行时间（毫秒）
    """
    success: bool = Field(..., description="是否成功")
    result: Optional[QueryResult] = Field(None, description="查询结果")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time_ms: float = Field(..., description="执行时间（毫秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "result": {
                    "columns": ["id", "title", "content"],
                    "rows": [{"id": 1, "title": "题目1", "content": "内容1"}],
                    "total": 1,
                    "truncated": False
                },
                "error": None,
                "execution_time_ms": 12.5
            }
        }