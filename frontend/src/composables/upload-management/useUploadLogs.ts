/**
 * 上传日志管理 Composable
 * 职责: 日志收集、持久化、上报
 */
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { LogStorage } from '@/utils/logStorage';
import { LogReporter } from '@/utils/logReporter';
import type { UploadLog, LogUserInfo } from '@/types/log';

type DebuggerRefLike = {
  value?: {
    entries?: unknown[];
    addEntry?: (level: string, source: string, msg: string) => void;
  };
};

export function useUploadLogs() {
  // 状态
  const uploadLogs = ref<UploadLog[]>([]);

  // 计算属性 - 简洁日志摘要(最近3条)
  const logSummary = computed(() => uploadLogs.value.slice(-3).reverse());

  // 添加日志
  const addLog = (msg: string, level: UploadLog['level'] = 'info', debuggerRef?: DebuggerRefLike) => {
    const time = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    const timestamp = Date.now();
    uploadLogs.value.push({ time, level, msg, timestamp });

    // 如果有debugger引用,同步日志
    if (debuggerRef?.value) {
      debuggerRef.value.addEntry(level, '系统', msg);
    }

    // 保存到 localStorage
    saveLogs(debuggerRef);
  };

  // 从 localStorage 恢复日志
  const restoreLogs = () => {
    const data = LogStorage.load();
    if (data) {
      uploadLogs.value = data.uploadLogs;
      console.log(`已恢复 ${uploadLogs.value.length} 条日志`);
    }
  };

  // 保存日志到 localStorage
  const saveLogs = (debuggerRef?: DebuggerRefLike) => {
    if (debuggerRef?.value) {
      // 同时保存 uploadLogs 和 debugEntries
      const entries = (debuggerRef.value as any).entries || [];
      LogStorage.save(uploadLogs.value, entries);
    } else {
      // 只保存 uploadLogs
      LogStorage.save(uploadLogs.value, []);
    }
  };

  // 上报日志到服务器
  const reportLogs = async (debuggerRef: DebuggerRefLike, userInfo: LogUserInfo) => {
    if (!debuggerRef?.value) {
      ElMessage.warning('调试器未就绪');
      return;
    }

    const entries = (debuggerRef.value as any).entries || [];
    if (entries.length === 0) {
      ElMessage.info('没有日志可上报');
      return;
    }

    ElMessage.info('正在上报日志...');

    const result = await LogReporter.report(entries, userInfo, true);

    if (result.success) {
      ElMessage.success(result.message);
    } else {
      ElMessage.error(result.message);
    }
  };

  // 清空日志
  const clearLogs = () => {
    uploadLogs.value = [];
  };

  return {
    // 状态
    uploadLogs,
    logSummary,

    // 方法
    addLog,
    restoreLogs,
    saveLogs,
    reportLogs,
    clearLogs,
  };
}
