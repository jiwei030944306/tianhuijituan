/**
 * 监控告警状态管理
 * 
 * 负责系统监控数据的告警判断、通知推送和告警历史管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  HealthResponse,
  PerformanceResponse,
  ErrorLogItem
} from '@/types/monitor';

/**
 * 告警级别
 */
export type AlertLevel = 'info' | 'warning' | 'critical';

/**
 * 告警类型
 */
export type AlertType = 
  | 'health'           // 服务健康状态
  | 'error_rate'       // 错误率超标
  | 'response_time'    // 响应时间过长
  | 'slow_requests'    // 慢请求过多
  | 'database'         // 数据库异常
  | 'disk'             // 磁盘空间不足
  | 'memory'           // 内存使用过高;

/**
 * 告警条目
 */
export interface AlertItem {
  id: string;
  type: AlertType;
  level: AlertLevel;
  title: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
  data?: Record<string, any>;
}

/**
 * 告警阈值配置
 */
export interface AlertThresholds {
  // 错误率阈值（%）
  errorRateWarning: number;
  errorRateCritical: number;
  
  // 响应时间阈值（ms）
  responseTimeWarning: number;
  responseTimeCritical: number;
  
  // 慢请求数量阈值
  slowRequestsWarning: number;
  slowRequestsCritical: number;
  
  // 磁盘使用率阈值（%）
  diskUsageWarning: number;
  diskUsageCritical: number;
  
  // 内存使用率阈值（%）
  memoryUsageWarning: number;
  memoryUsageCritical: number;
}

/**
 * 默认告警阈值
 */
const DEFAULT_THRESHOLDS: AlertThresholds = {
  errorRateWarning: 1,      // 错误率 > 1% 警告
  errorRateCritical: 5,     // 错误率 > 5% 严重
  responseTimeWarning: 500, // 响应时间 > 500ms 警告
  responseTimeCritical: 1000, // 响应时间 > 1000ms 严重
  slowRequestsWarning: 5,   // 慢请求 > 5 个 警告
  slowRequestsCritical: 10, // 慢请求 > 10 个 严重
  diskUsageWarning: 80,     // 磁盘 > 80% 警告
  diskUsageCritical: 90,    // 磁盘 > 90% 严重
  memoryUsageWarning: 80,   // 内存 > 80% 警告
  memoryUsageCritical: 90,  // 内存 > 90% 严重
};

/**
 * 告警声音配置
 */
const ALERT_SOUNDS: Record<AlertLevel, string> = {
  info: 'data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU',
  warning: 'data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU',
  critical: 'data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU',
};

export const useMonitorStore = defineStore('monitor', () => {
  // ==================== 状态 ====================
  
  /** 当前健康状态 */
  const health = ref<HealthResponse | null>(null);
  
  /** 当前性能数据 */
  const performance = ref<PerformanceResponse | null>(null);
  
  /** 当前告警列表 */
  const alerts = ref<AlertItem[]>([]);
  
  /** 已确认的告警列表 */
  const acknowledgedAlerts = ref<AlertItem[]>([]);
  
  /** 告警阈值配置 */
  const thresholds = ref<AlertThresholds>({ ...DEFAULT_THRESHOLDS });
  
  /** 是否启用声音提示 */
  const soundEnabled = ref(true);
  
  /** 是否启用浏览器通知 */
  const notificationEnabled = ref(true);
  
  /** 是否启用自动刷新 */
  const autoRefreshEnabled = ref(true);
  
  /** 自动刷新间隔（秒） */
  const refreshInterval = ref(30);
  
  /** 最后检查时间 */
  const lastCheckTime = ref<string | null>(null);
  
  // ==================== 计算属性 ====================
  
  /** 未确认的告警数量 */
  const unacknowledgedCount = computed(() => {
    return alerts.value.filter(a => !a.acknowledged).length;
  });
  
  /** 严重告警数量 */
  const criticalCount = computed(() => {
    return alerts.value.filter(a => a.level === 'critical' && !a.acknowledged).length;
  });
  
  /** 警告告警数量 */
  const warningCount = computed(() => {
    return alerts.value.filter(a => a.level === 'warning' && !a.acknowledged).length;
  });
  
  /** 是否有严重告警 */
  const hasCriticalAlerts = computed(() => criticalCount.value > 0);
  
  /** 是否有警告 */
  const hasWarnings = computed(() => warningCount.value > 0);
  
  /** 系统整体状态 */
  const systemStatus = computed<'healthy' | 'degraded' | 'unhealthy'>(() => {
    if (criticalCount.value > 0) return 'unhealthy';
    if (warningCount.value > 0) return 'degraded';
    return 'healthy';
  });
  
  // ==================== 方法 ====================
  
  /**
   * 生成告警 ID
   */
  function generateAlertId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
  }
  
  /**
   * 创建告警
   */
  function createAlert(
    type: AlertType,
    level: AlertLevel,
    title: string,
    message: string,
    data?: Record<string, any>
  ): AlertItem {
    const alert: AlertItem = {
      id: generateAlertId(),
      type,
      level,
      title,
      message,
      timestamp: new Date().toISOString(),
      acknowledged: false,
      data,
    };
    
    // 添加到告警列表
    alerts.value.unshift(alert);
    
    // 触发通知
    triggerNotification(alert);
    
    // 播放声音
    playAlertSound(level);
    
    return alert;
  }
  
  /**
   * 确认告警
   */
  function acknowledgeAlert(alertId: string): void {
    const alertIndex = alerts.value.findIndex(a => a.id === alertId);
    if (alertIndex !== -1) {
      const alert = alerts.value[alertIndex];
      alert.acknowledged = true;
      acknowledgedAlerts.value.unshift(alert);
      alerts.value.splice(alertIndex, 1);
    }
  }
  
  /**
   * 确认所有告警
   */
  function acknowledgeAll(): void {
    acknowledgedAlerts.value.unshift(...alerts.value.map(a => ({ ...a, acknowledged: true })));
    alerts.value = [];
  }
  
  /**
   * 清除已确认的告警历史
   */
  function clearAcknowledged(): void {
    acknowledgedAlerts.value = [];
  }
  
  /**
   * 删除告警
   */
  function deleteAlert(alertId: string): void {
    alerts.value = alerts.value.filter(a => a.id !== alertId);
  }
  
  /**
   * 播放告警声音
   */
  function playAlertSound(level: AlertLevel): void {
    if (!soundEnabled.value) return;
    
    try {
      // 使用简单的蜂鸣声
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // 根据告警级别设置不同频率
      if (level === 'critical') {
        oscillator.frequency.value = 880; // A5
        gainNode.gain.value = 0.3;
        oscillator.type = 'square';
      } else if (level === 'warning') {
        oscillator.frequency.value = 440; // A4
        gainNode.gain.value = 0.2;
        oscillator.type = 'sine';
      } else {
        oscillator.frequency.value = 220; // A3
        gainNode.gain.value = 0.1;
        oscillator.type = 'sine';
      }
      
      oscillator.start();
      
      // 持续 300ms
      setTimeout(() => {
        oscillator.stop();
        audioContext.close();
      }, 300);
    } catch (error) {
      console.warn('播放告警声音失败:', error);
    }
  }
  
  /**
   * 请求浏览器通知权限
   */
  async function requestNotificationPermission(): Promise<boolean> {
    if (!('Notification' in window)) {
      console.warn('浏览器不支持通知');
      return false;
    }
    
    if (Notification.permission === 'granted') {
      return true;
    }
    
    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    
    return false;
  }
  
  /**
   * 触发浏览器通知
   */
  function triggerNotification(alert: AlertItem): void {
    if (!notificationEnabled.value) return;
    
    if (!('Notification' in window)) return;
    
    if (Notification.permission === 'granted') {
      try {
        const emoji = {
          critical: '🚨',
          warning: '⚠️',
          info: 'ℹ️',
        };
        
        new Notification(`${emoji[alert.level]} ${alert.title}`, {
          body: alert.message,
          icon: '/favicon.ico',
          tag: alert.id,
          requireInteraction: alert.level === 'critical',
        });
      } catch (error) {
        console.warn('发送浏览器通知失败:', error);
      }
    }
  }
  
  /**
   * 检查健康状态告警
   */
  function checkHealthAlerts(healthData: HealthResponse): void {
    // 检查服务整体状态
    if (healthData.status === 'unhealthy') {
      createAlert(
        'health',
        'critical',
        '服务异常',
        '系统服务检测到严重问题，请立即检查！',
        { status: healthData.status }
      );
    } else if (healthData.status === 'degraded') {
      createAlert(
        'health',
        'warning',
        '服务降级',
        '系统服务部分功能异常，请关注系统状态。',
        { status: healthData.status }
      );
    }
    
    // 检查磁盘状态
    const diskCheck = healthData.checks.disk;
    if (diskCheck) {
      if (diskCheck.used_percent >= thresholds.value.diskUsageCritical) {
        createAlert(
          'disk',
          'critical',
          '磁盘空间严重不足',
          `磁盘使用率已达 ${diskCheck.used_percent.toFixed(1)}%，仅剩 ${diskCheck.free_gb.toFixed(2)}GB 可用空间`,
          diskCheck
        );
      } else if (diskCheck.used_percent >= thresholds.value.diskUsageWarning) {
        createAlert(
          'disk',
          'warning',
          '磁盘空间不足',
          `磁盘使用率已达 ${diskCheck.used_percent.toFixed(1)}%，请注意清理空间`,
          diskCheck
        );
      }
    }
    
    // 检查内存状态
    const memoryCheck = healthData.checks.memory;
    if (memoryCheck && memoryCheck.used_percent) {
      if (memoryCheck.used_percent >= thresholds.value.memoryUsageCritical) {
        createAlert(
          'memory',
          'critical',
          '内存使用率严重超标',
          `内存使用率已达 ${memoryCheck.used_percent.toFixed(1)}%`,
          memoryCheck
        );
      } else if (memoryCheck.used_percent >= thresholds.value.memoryUsageWarning) {
        createAlert(
          'memory',
          'warning',
          '内存使用率超标',
          `内存使用率已达 ${memoryCheck.used_percent.toFixed(1)}%`,
          memoryCheck
        );
      }
    }
  }
  
  /**
   * 检查性能数据告警
   */
  function checkPerformanceAlerts(perfData: PerformanceResponse): void {
    const { summary } = perfData;
    
    // 检查错误率
    if (summary.error_rate_percent >= thresholds.value.errorRateCritical) {
      createAlert(
        'error_rate',
        'critical',
        '错误率严重超标',
        `当前错误率为 ${summary.error_rate_percent.toFixed(2)}%，远超正常水平`,
        { errorRate: summary.error_rate_percent }
      );
    } else if (summary.error_rate_percent >= thresholds.value.errorRateWarning) {
      createAlert(
        'error_rate',
        'warning',
        '错误率超标',
        `当前错误率为 ${summary.error_rate_percent.toFixed(2)}%，请关注`,
        { errorRate: summary.error_rate_percent }
      );
    }
    
    // 检查平均响应时间
    if (summary.avg_response_time_ms >= thresholds.value.responseTimeCritical) {
      createAlert(
        'response_time',
        'critical',
        '响应时间严重超时',
        `平均响应时间为 ${summary.avg_response_time_ms.toFixed(0)}ms，系统响应缓慢`,
        { avgResponseTime: summary.avg_response_time_ms }
      );
    } else if (summary.avg_response_time_ms >= thresholds.value.responseTimeWarning) {
      createAlert(
        'response_time',
        'warning',
        '响应时间超时',
        `平均响应时间为 ${summary.avg_response_time_ms.toFixed(0)}ms，性能下降`,
        { avgResponseTime: summary.avg_response_time_ms }
      );
    }
    
    // 检查慢请求数量
    if (summary.slow_requests_count >= thresholds.value.slowRequestsCritical) {
      createAlert(
        'slow_requests',
        'critical',
        '慢请求过多',
        `检测到 ${summary.slow_requests_count} 个慢请求（>1 秒），系统性能严重下降`,
        { slowRequests: summary.slow_requests_count }
      );
    } else if (summary.slow_requests_count >= thresholds.value.slowRequestsWarning) {
      createAlert(
        'slow_requests',
        'warning',
        '慢请求较多',
        `检测到 ${summary.slow_requests_count} 个慢请求（>1 秒），请优化性能`,
        { slowRequests: summary.slow_requests_count }
      );
    }
  }
  
  /**
   * 更新监控数据并检查告警
   */
  function updateMonitorData(data: {
    health: HealthResponse;
    performance: PerformanceResponse;
  }): void {
    health.value = data.health;
    performance.value = data.performance;
    lastCheckTime.value = new Date().toLocaleString('zh-CN');
    
    // 清除之前的未确认告警（避免重复）
    // 只保留需要持续的严重告警
    alerts.value = alerts.value.filter(a => 
      a.level === 'critical' && !a.acknowledged
    );
    
    // 检查新的告警
    checkHealthAlerts(data.health);
    checkPerformanceAlerts(data.performance);
  }
  
  /**
   * 重置所有状态
   */
  function reset(): void {
    health.value = null;
    performance.value = null;
    alerts.value = [];
    acknowledgedAlerts.value = [];
    lastCheckTime.value = null;
  }
  
  // ==================== 返回 ====================
  
  return {
    // 状态
    health,
    performance,
    alerts,
    acknowledgedAlerts,
    thresholds,
    soundEnabled,
    notificationEnabled,
    autoRefreshEnabled,
    refreshInterval,
    lastCheckTime,
    
    // 计算属性
    unacknowledgedCount,
    criticalCount,
    warningCount,
    hasCriticalAlerts,
    hasWarnings,
    systemStatus,
    
    // 方法
    createAlert,
    acknowledgeAlert,
    acknowledgeAll,
    clearAcknowledged,
    deleteAlert,
    requestNotificationPermission,
    updateMonitorData,
    checkHealthAlerts,
    checkPerformanceAlerts,
    reset,
  };
});
