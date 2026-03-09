/**
 * 数据库查询相关类型定义
 */

export interface QueryResult {
  columns: string[];
  rows: Record<string, any>[];
  total: number;
  truncated: boolean;
}

export interface QueryResponse {
  success: boolean;
  result?: QueryResult;
  error?: string;
  execution_time_ms: number;
}