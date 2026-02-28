/**
 * 日志上报工具类
 * 用于异步上报错误和警告日志到服务器
 */

import type { DebugEntry, LogUserInfo, LogReportResult } from '@/types/log';

/**
 * 日志上报配置常量
 */
const LOG_REPORT_CONFIG = {
  // 上报接口地址
  REPORT_ENDPOINT: '/api/logs/report',

  // 自动上报的日志级别
  REPORT_LEVELS: ['error', 'warning'] as const,
} as const;

/**
 * 日志上报工具类
 */
export class LogReporter {
  /**
   * 上报日志到服务器
   * @param debugEntries 调试日志列表
   * @param userInfo 用户信息
   * @param auto 自动上报（仅上报 error 和 warning）
   * @returns 上报结果
   */
  static async report(
    debugEntries: DebugEntry[],
    userInfo: LogUserInfo,
    auto: boolean = true
  ): Promise<LogReportResult> {
    try {
      // 1. 过滤日志级别
      const logsToReport = auto
        ? debugEntries.filter(entry =>
            LOG_REPORT_CONFIG.REPORT_LEVELS.includes(entry.level as any)
          )
        : debugEntries;

      if (logsToReport.length === 0) {
        return { success: true, message: '没有需要上报的日志' };
      }

      // 2. 构建上报数据
      const data = {
        logs: logsToReport,
        userInfo,
        environment: {
          userAgent: navigator.userAgent,
          url: window.location.href,
          timestamp: new Date().toISOString(),
        },
      };

      // 3. 发送请求
      const response = await fetch(LOG_REPORT_CONFIG.REPORT_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      return { success: true, message: result.message || '上报成功' };
    } catch (error: unknown) {
      console.error('上报日志失败:', error);
      return {
        success: false,
        message: `上报失败: ${error instanceof Error ? error.message : String(error)}`,
      };
    }
  }

  /**
   * 上报单个错误日志
   * @param entry 调试日志条目
   * @param userInfo 用户信息
   * @returns 上报结果
   */
  static async reportError(
    entry: DebugEntry,
    userInfo: LogUserInfo
  ): Promise<LogReportResult> {
    if (entry.level !== 'error') {
      return { success: false, message: '仅支持上报 error 级别日志' };
    }
    return await this.report([entry], userInfo, false);
  }

  /**
   * 获取配置常量（用于测试）
   */
  static getConfig() {
    return LOG_REPORT_CONFIG;
  }
}