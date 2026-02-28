/**
 * 日志存储工具类
 * 提供日志的持久化存储、读取、清理功能
 */

import type { UploadLog, DebugEntry, LogStorageData, LogStorageInfo } from '@/types/log';

/**
 * 日志存储配置常量
 */
const LOG_STORAGE_CONFIG = {
  // localStorage 键名
  STORAGE_KEY: 'zy_upload_logs',

  // 最大存储数量
  MAX_UPLOAD_LOGS: 500,          // 基础日志最大数量
  MAX_DEBUG_ENTRIES: 500,        // 调试日志最大数量

  // 过期时间（毫秒）
  EXPIRY_DAYS: 7,                // 7天过期
  EXPIRY_MS: 7 * 24 * 60 * 60 * 1000,

  // 存储版本
  VERSION: '1.0.0',
} as const;

/**
 * 日志存储工具类
 */
export class LogStorage {
  /**
   * 保存日志到 localStorage
   * @param uploadLogs 基础日志列表
   * @param debugEntries 调试日志列表
   */
  static save(uploadLogs: UploadLog[], debugEntries: DebugEntry[]): void {
    try {
      // 1. 限制数量
      const limitedUploadLogs = uploadLogs.slice(-LOG_STORAGE_CONFIG.MAX_UPLOAD_LOGS);
      const limitedDebugEntries = debugEntries.slice(-LOG_STORAGE_CONFIG.MAX_DEBUG_ENTRIES);

      // 2. 构建存储数据
      const data: LogStorageData = {
        version: LOG_STORAGE_CONFIG.VERSION,
        uploadLogs: limitedUploadLogs,
        debugEntries: limitedDebugEntries,
        lastUpdated: new Date().toISOString(),
        expiresAt: new Date(Date.now() + LOG_STORAGE_CONFIG.EXPIRY_MS).toISOString(),
      };

      // 3. 保存到 localStorage
      localStorage.setItem(LOG_STORAGE_CONFIG.STORAGE_KEY, JSON.stringify(data));
    } catch (error: unknown) {
      console.error('保存日志到 localStorage 失败:', error instanceof Error ? error.message : String(error));
    }
  }

  /**
   * 从 localStorage 加载日志
   * @returns 日志数据或 null
   */
  static load(): LogStorageData | null {
    try {
      const json = localStorage.getItem(LOG_STORAGE_CONFIG.STORAGE_KEY);
      if (!json) return null;

      const data: LogStorageData = JSON.parse(json);

      // 检查版本兼容性
      if (data.version !== LOG_STORAGE_CONFIG.VERSION) {
        console.warn('日志存储版本不匹配，已清除旧数据');
        this.clear();
        return null;
      }

      // 检查是否过期
      if (new Date(data.expiresAt) < new Date()) {
        console.log('日志已过期，已清除');
        this.clear();
        return null;
      }

      return data;
    } catch (error: unknown) {
      console.error('从 localStorage 加载日志失败:', error instanceof Error ? error.message : String(error));
      return null;
    }
  }

  /**
   * 清空日志
   */
  static clear(): void {
    try {
      localStorage.removeItem(LOG_STORAGE_CONFIG.STORAGE_KEY);
    } catch (error: unknown) {
      console.error('清空日志失败:', error instanceof Error ? error.message : String(error));
    }
  }

  /**
   * 检查日志是否过期
   * @returns 是否过期
   */
  static isExpired(): boolean {
    const data = this.load();
    if (!data) return true;
    return new Date(data.expiresAt) < new Date();
  }

  /**
   * 获取存储信息
   * @returns 存储统计信息
   */
  static getStorageInfo(): LogStorageInfo {
    const data = this.load();
    if (!data) {
      return {
        uploadLogCount: 0,
        debugEntryCount: 0,
        sizeKB: 0,
        expiresAt: '-',
      };
    }

    const sizeKB = JSON.stringify(data).length / 1024;
    return {
      uploadLogCount: data.uploadLogs.length,
      debugEntryCount: data.debugEntries.length,
      sizeKB: Number(sizeKB.toFixed(2)),
      expiresAt: data.expiresAt,
    };
  }

  /**
   * 获取配置常量（用于测试）
   */
  static getConfig() {
    return LOG_STORAGE_CONFIG;
  }
}