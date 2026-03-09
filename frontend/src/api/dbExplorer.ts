/**
 * 数据库查询 API 服务
 */
import { apiClient } from './base';
import type { QueryResponse } from '@/types/dbExplorer';

export const dbExplorerApi = {
  /**
   * 执行 SQL 查询
   * @param sql SQL 查询语句
   * @param limit 结果数量限制
   */
  async executeQuery(sql: string, limit: number = 100): Promise<QueryResponse> {
    const response = await apiClient.post<QueryResponse>(
      '/api/v1/db-explorer/query',
      { sql, limit }
    );
    return response.data;
  }
};