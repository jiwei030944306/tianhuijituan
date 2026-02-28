"""
监控日志数据模型

用于存储后端运行时的错误日志、性能指标和系统事件
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base


class MonitorLog(Base):
    """监控日志模型"""
    __tablename__ = "monitor_logs"

    id = Column(String(36), primary_key=True, comment="日志ID (UUID)")

    # 日志类型
    log_type = Column(String(20), nullable=False, comment="日志类型: error/performance/event")

    # 请求信息
    request_id = Column(String(36), comment="请求唯一标识")
    method = Column(String(10), comment="HTTP方法")
    path = Column(String(500), comment="请求路径")
    status_code = Column(Integer, comment="HTTP状态码")

    # 性能数据
    response_time_ms = Column(Integer, comment="响应时间(毫秒)")

    # 错误信息
    error_message = Column(Text, comment="错误消息")
    error_stack = Column(Text, comment="堆栈信息")
    request_params = Column(Text, comment="请求参数(JSON)")

    # 元数据
    user_id = Column(String(100), comment="操作用户ID")
    ip_address = Column(String(50), comment="客户端IP")

    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    __table_args__ = (
        Index('idx_monitor_logs_type', 'log_type'),
        Index('idx_monitor_logs_created_at', 'created_at'),
        Index('idx_monitor_logs_path', 'path'),
        Index('idx_monitor_logs_status_code', 'status_code'),
    )

    def __repr__(self):
        return f"<MonitorLog(id={self.id}, type={self.log_type}, path={self.path})>"