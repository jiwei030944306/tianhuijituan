/**
 * 监控系统类型定义
 * 
 * 定义后端监控相关的数据结构
 */

// ==================== 枚举类型 ====================

/** 健康状态 */
export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy';

/** 日志类型 */
export type LogType = 'error' | 'performance' | 'event';

// ==================== 健康检查相关 ====================

/** 数据库检查结果 */
export interface DatabaseCheck {
  status: string;
  latency_ms: number;
  message?: string;
}

/** 磁盘检查结果 */
export interface DiskCheck {
  status: string;
  used_percent: number;
  free_gb: number;
  message?: string;
}

/** 内存检查结果 */
export interface MemoryCheck {
  status: string;
  used_percent: number;
  message?: string;
}

/** 健康检查响应 */
export interface HealthResponse {
  status: HealthStatus;
  timestamp: string;
  checks: {
    database: DatabaseCheck;
    disk: DiskCheck;
    memory: MemoryCheck;
  };
  uptime_seconds: number;
  version: string;
}

// ==================== 性能统计相关 ====================

/** 端点统计 */
export interface EndpointStats {
  path: string;
  method: string;
  count: number;
  avg_ms: number;
  max_ms: number;
  min_ms: number;
  error_count: number;
}

/** 慢请求记录 */
export interface SlowRequest {
  path: string;
  method: string;
  response_time_ms: number;
  timestamp: string;
}

/** 性能摘要 */
export interface PerformanceSummary {
  total_requests: number;
  avg_response_time_ms: number;
  error_rate_percent: number;
  slow_requests_count: number;
}

/** 性能统计响应 */
export interface PerformanceResponse {
  period: {
    start: string;
    end: string;
  };
  summary: PerformanceSummary;
  endpoints: EndpointStats[];
  slow_requests: SlowRequest[];
}

// ==================== 错误日志相关 ====================

/** 错误日志条目 */
export interface ErrorLogItem {
  id: string;
  timestamp: string;
  path: string;
  method: string;
  status_code: number;
  error_message: string;
  error_stack?: string;
  request_params?: string;
}

/** 错误日志响应 */
export interface ErrorLogResponse {
  total: number;
  items: ErrorLogItem[];
  pagination: {
    skip: number;
    limit: number;
  };
}

// ==================== 数据库状态相关 ====================

/** 表统计 */
export interface TableStats {
  name: string;
  row_count: number;
  size_kb: number;
}

/** 数据库状态响应 */
export interface DatabaseResponse {
  status: string;
  latency_ms: number;
  tables: TableStats[];
  db_size_mb: number;
  error?: string;
}

// ==================== 监控面板状态 ====================

/** 监控面板状态 */
export interface MonitorState {
  health: HealthResponse | null;
  performance: PerformanceResponse | null;
  errors: ErrorLogResponse | null;
  database: DatabaseResponse | null;
  loading: boolean;
  error: string | null;
  lastRefresh: string | null;
}

/** 监控卡片数据 */
export interface MonitorCard {
  title: string;
  value: string | number;
  unit?: string;
  status: 'success' | 'warning' | 'danger' | 'info';
  icon?: string;
  description?: string;
}