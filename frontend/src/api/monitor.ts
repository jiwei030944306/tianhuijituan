/**
 * 监控API服务
 * 
 * 封装后端监控相关的API调用
 */

import { apiClient } from './base';
import type {
  HealthResponse,
  PerformanceResponse,
  ErrorLogResponse,
  DatabaseResponse
} from '@/types/monitor';

/**
 * 监控API服务对象
 */
export const monitorApi = {
  /**
   * 获取服务健康状态
   */
  async getHealth(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/api/v1/monitor/health');
    return response.data;
  },

  /**
   * 获取API性能统计
   * @param hours 统计最近N小时的数据，默认1小时
   */
  async getPerformance(hours: number = 1): Promise<PerformanceResponse> {
    const response = await apiClient.get<PerformanceResponse>('/api/v1/monitor/performance', {
      params: { hours }
    });
    return response.data;
  },

  /**
   * 获取错误日志列表
   * @param skip 跳过记录数
   * @param limit 返回记录数
   * @param hours 查询最近N小时的日志
   */
  async getErrors(
    skip: number = 0,
    limit: number = 20,
    hours: number = 24
  ): Promise<ErrorLogResponse> {
    const response = await apiClient.get<ErrorLogResponse>('/api/v1/monitor/errors', {
      params: { skip, limit, hours }
    });
    return response.data;
  },

  /**
   * 获取数据库状态
   */
  async getDatabase(): Promise<DatabaseResponse> {
    const response = await apiClient.get<DatabaseResponse>('/api/v1/monitor/database');
    return response.data;
  },

  /**
   * 清理过期日志
   * @param days 保留最近N天的日志
   */
  async clearLogs(days: number = 7): Promise<{ success: boolean; deleted_count: number; message: string }> {
    const response = await apiClient.delete('/api/v1/monitor/logs/clear', {
      params: { days }
    });
    return response.data;
  },

  /**
   * 获取所有监控数据（并发请求）
   */
  async getAll(hours: number = 1): Promise<{
    health: HealthResponse;
    performance: PerformanceResponse;
    errors: ErrorLogResponse;
    database: DatabaseResponse;
  }> {
    const [health, performance, errors, database] = await Promise.all([
      this.getHealth(),
      this.getPerformance(hours),
      this.getErrors(0, 10, hours),
      this.getDatabase()
    ]);

    return { health, performance, errors, database };
  }
};