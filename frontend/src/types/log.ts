/**
 * 日志类型定义
 * 定义日志持久化相关的数据结构和类型
 */

/**
 * 日志级别
 */
export type LogLevel = 'info' | 'success' | 'warning' | 'error';

/**
 * 基础日志条目（用于 UploadManagement.vue）
 */
export interface UploadLog {
  time: string;           // 时间戳 "14:30:25"
  level: LogLevel;        // 日志级别
  msg: string;            // 日志消息
  timestamp?: number;     // 时间戳（毫秒）
}

/**
 * 调试日志条目（用于 UploadDebugger.vue）
 */
export interface DebugEntry {
  id: string;             // 唯一ID: "debug_1738664625123_abc123"
  timestamp: string;      // 精确时间戳: "14:30:25.123"
  level: LogLevel;        // 日志级别
  stage: string;          // 阶段: "冲突检测"、"文件上传"等
  message: string;        // 消息
  details?: unknown;      // 详细数据（可展开查看）
  duration?: number;      // 耗时（毫秒）
}

/**
 * 日志存储数据结构
 */
export interface LogStorageData {
  version: string;        // 存储版本号
  uploadLogs: UploadLog[]; // 基础日志列表
  debugEntries: DebugEntry[]; // 调试日志列表
  lastUpdated: string;    // 最后更新时间（ISO格式）
  expiresAt: string;      // 过期时间（ISO格式）
}

/**
 * 用户信息（用于日志上报）
 */
export interface LogUserInfo {
  userId?: string;
  userName?: string;
  folderCode?: string;
}

/**
 * 环境信息（用于日志上报）
 */
export interface LogEnvironment {
  userAgent: string;
  url: string;
  timestamp: string;
}

/**
 * 服务器日志上报数据
 */
export interface LogReportData {
  logs: DebugEntry[];     // 日志列表
  userInfo: LogUserInfo;  // 用户信息
  environment: LogEnvironment;  // 环境信息
}

/**
 * 日志上报结果
 */
export interface LogReportResult {
  success: boolean;
  message: string;
}

/**
 * 日志存储信息
 */
export interface LogStorageInfo {
  uploadLogCount: number;
  debugEntryCount: number;
  sizeKB: number;
  expiresAt: string;
}
