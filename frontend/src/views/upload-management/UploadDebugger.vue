<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  Bug,
  Trash2,
  Download,
  ChevronDown,
  ChevronRight,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  Upload
} from 'lucide-vue-next';
import { LogStorage } from '@/utils/logStorage';
import { LogReporter } from '@/utils/logReporter';
import type { DebugEntry, LogUserInfo } from '@/types/log';
import { ElMessage } from 'element-plus';

// 调试信息条目接口
interface DebugEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'success' | 'warning' | 'error';
  stage: string;
  message: string;
  details?: any;
  duration?: number;
}

// 组件状态
const entries = ref<DebugEntry[]>([]);
const expandedEntries = ref<Set<string>>(new Set());
const filterLevel = ref<'all' | 'info' | 'success' | 'warning' | 'error'>('all');

// 生成唯一ID
const generateId = () => `debug_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

// 初始化
onMounted(() => {
  restoreEntries();
});

// 从 localStorage 恢复日志
const restoreEntries = () => {
  const data = LogStorage.load();
  if (data && data.debugEntries) {
    entries.value = data.debugEntries;
    console.log(`已恢复 ${entries.value.length} 条调试日志`);
  }
};

// 获取当前时间戳
const getTimestamp = () => {
  const now = new Date();
  return now.toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    fractionalSecondDigits: 3
  });
};

// 添加调试信息
const addEntry = (level: DebugEntry['level'], stage: string, message: string, details?: any, duration?: number) => {
  const entry: DebugEntry = {
    id: generateId(),
    timestamp: getTimestamp(),
    level,
    stage,
    message,
    details,
    duration
  };
  entries.value.unshift(entry); // 新条目添加到顶部

  // 限制条目数量，防止内存泄漏
  if (entries.value.length > 100) {
    entries.value = entries.value.slice(0, 100);
  }

  // 保存到 localStorage
  saveEntries();
};

// 保存日志到 localStorage
const saveEntries = () => {
  // 这里只保存 debugEntries，uploadLogs 由父组件负责保存
  LogStorage.save([], entries.value);
};

// 清空调试信息
const clearEntries = () => {
  entries.value = [];
  expandedEntries.value.clear();
  // 清空 localStorage
  LogStorage.clear();
};

// 导出调试信息
const exportEntries = () => {
  const data = {
    exportTime: new Date().toISOString(),
    entries: entries.value
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `upload-debug-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
};

// 上报日志到服务器
const reportEntries = async () => {
  if (entries.value.length === 0) {
    ElMessage.info('没有日志可上报');
    return;
  }

  ElMessage.info('正在上报日志...');

  const userInfo: LogUserInfo = {
    folderCode: '',
  };

  const result = await LogReporter.report(entries.value, userInfo, true);

  if (result.success) {
    ElMessage.success(result.message);
  } else {
    ElMessage.error(result.message);
  }
};

// 切换条目展开状态
const toggleEntry = (id: string) => {
  if (expandedEntries.value.has(id)) {
    expandedEntries.value.delete(id);
  } else {
    expandedEntries.value.add(id);
  }
};

// 过滤后的条目
const filteredEntries = computed(() => {
  if (filterLevel.value === 'all') return entries.value;
  return entries.value.filter(entry => entry.level === filterLevel.value);
});

// 统计信息
const stats = computed(() => {
  const total = entries.value.length;
  const info = entries.value.filter(e => e.level === 'info').length;
  const success = entries.value.filter(e => e.level === 'success').length;
  const warning = entries.value.filter(e => e.level === 'warning').length;
  const error = entries.value.filter(e => e.level === 'error').length;
  return { total, info, success, warning, error };
});

// 获取级别图标
const getLevelIcon = (level: DebugEntry['level']) => {
  switch (level) {
    case 'info': return Info;
    case 'success': return CheckCircle;
    case 'warning': return AlertTriangle;
    case 'error': return XCircle;
    default: return Info;
  }
};

// 获取级别颜色
const getLevelColor = (level: DebugEntry['level']) => {
  switch (level) {
    case 'info': return 'text-blue-600 bg-blue-50 border-blue-200';
    case 'success': return 'text-green-600 bg-green-50 border-green-200';
    case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'error': return 'text-red-600 bg-red-50 border-red-200';
    default: return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

// 获取阶段颜色
const getStageColor = (stage: string) => {
  const colors: Record<string, string> = {
    '初始化': 'text-purple-600',
    '文件选择': 'text-indigo-600',
    '冲突检测': 'text-orange-600',
    '上传准备': 'text-cyan-600',
    '文件上传': 'text-blue-600',
    '服务器处理': 'text-teal-600',
    '完成': 'text-green-600',
    '错误': 'text-red-600'
  };
  return colors[stage] || 'text-gray-600';
};

// 暴露方法给父组件
defineExpose({
  addEntry,
  clearEntries,
  logInfo: (stage: string, message: string, details?: any) => addEntry('info', stage, message, details),
  logSuccess: (stage: string, message: string, details?: any, duration?: number) => addEntry('success', stage, message, details, duration),
  logWarning: (stage: string, message: string, details?: any) => addEntry('warning', stage, message, details),
  logError: (stage: string, message: string, details?: any) => addEntry('error', stage, message, details),
  logFileSelect: (file: File) => {
    addEntry('info', '文件选择', `选中文件: ${file.name}`, {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: new Date(file.lastModified).toISOString()
    });
  },
  logConflictCheck: (params: any, response: any, duration: number) => {
    const hasConflict = response?.conflict;
    addEntry(
      hasConflict ? 'warning' : 'success',
      '冲突检测',
      hasConflict ? `发现冲突: ${response.message}` : '无冲突，可以上传',
      { request: params, response },
      duration
    );
  },
  logUploadRequest: (formData: FormData) => {
    const data: Record<string, any> = {};
    formData.forEach((value, key) => {
      data[key] = value instanceof File ? `[File: ${value.name}]` : value;
    });
    addEntry('info', '上传准备', '构建FormData请求', data);
  },
  logUploadResponse: (response: any, duration: number) => {
    addEntry(
      'success',
      '服务器处理',
      `上传成功: ${response.batch_id}`,
      response,
      duration
    );
  },
  logUploadError: (error: any, stage: string) => {
    addEntry('error', stage, error.message || '未知错误', {
      error: error.toString(),
      stack: error.stack
    });
  }
});
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm h-full flex flex-col">
    <!-- 头部 -->
    <div class="p-4 border-b border-gray-200 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <Bug class="w-5 h-5 text-indigo-600" />
        <h2 class="text-lg font-semibold text-gray-800">上传调试面板</h2>
        <span class="text-xs text-gray-400">({{ stats.total }}条记录)</span>
      </div>
      <div class="flex items-center gap-2">
        <!-- 过滤器 -->
        <select 
          v-model="filterLevel"
          class="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="all">全部 ({{ stats.total }})</option>
          <option value="info">信息 ({{ stats.info }})</option>
          <option value="success">成功 ({{ stats.success }})</option>
          <option value="warning">警告 ({{ stats.warning }})</option>
          <option value="error">错误 ({{ stats.error }})</option>
        </select>
        <!-- 导出按钮 -->
        <button 
          @click="exportEntries"
          class="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors"
          title="导出调试信息"
        >
          <Download class="w-4 h-4" />
        </button>
        <!-- 清空按钮 -->
        <button
          @click="clearEntries"
          class="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
          title="清空记录"
        >
          <Trash2 class="w-4 h-4" />
        </button>
        <!-- 上报按钮 -->
        <button
          @click="reportEntries"
          class="p-1.5 text-gray-500 hover:text-orange-600 hover:bg-orange-50 rounded transition-colors"
          title="上报日志"
        >
          <Upload class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 调试信息列表 -->
    <div class="flex-1 overflow-y-auto p-2 space-y-2">
      <div v-if="filteredEntries.length === 0" class="text-center text-gray-400 py-8">
        <Info class="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p class="text-sm">暂无调试信息</p>
        <p class="text-xs mt-1">上传文件后将显示详细调试信息</p>
      </div>

      <div 
        v-for="entry in filteredEntries" 
        :key="entry.id"
        class="border rounded-lg overflow-hidden"
        :class="getLevelColor(entry.level)"
      >
        <!-- 条目头部 -->
        <div 
          class="p-2 flex items-start gap-2 cursor-pointer hover:opacity-80 transition-opacity"
          @click="toggleEntry(entry.id)"
        >
          <component :is="getLevelIcon(entry.level)" class="w-4 h-4 mt-0.5 shrink-0" />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 text-xs">
              <span class="font-mono opacity-70">{{ entry.timestamp }}</span>
              <span class="font-medium" :class="getStageColor(entry.stage)">{{ entry.stage }}</span>
              <span v-if="entry.duration" class="text-xs opacity-60">
                <Clock class="w-3 h-3 inline mr-0.5" />
                {{ entry.duration }}ms
              </span>
            </div>
            <div class="text-sm font-medium mt-0.5 truncate">
              {{ entry.message }}
            </div>
          </div>
          <component 
            :is="expandedEntries.has(entry.id) ? ChevronDown : ChevronRight" 
            class="w-4 h-4 mt-0.5 shrink-0 opacity-50"
          />
        </div>

        <!-- 详情展开 -->
        <div v-if="expandedEntries.has(entry.id) && entry.details" class="border-t border-inherit px-2 py-2">
          <pre class="text-xs font-mono overflow-x-auto whitespace-pre-wrap break-all bg-black/5 rounded p-2">{{ JSON.stringify(entry.details, null, 2) }}</pre>
        </div>
      </div>
    </div>

    <!-- 底部统计 -->
    <div class="p-2 border-t border-gray-200 bg-gray-50 text-xs flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-blue-500"></span>
          信息 {{ stats.info }}
        </span>
        <span class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-green-500"></span>
          成功 {{ stats.success }}
        </span>
        <span class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-yellow-500"></span>
          警告 {{ stats.warning }}
        </span>
        <span class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-red-500"></span>
          错误 {{ stats.error }}
        </span>
      </div>
      <span class="text-gray-400">共 {{ stats.total }} 条</span>
    </div>
  </div>
</template>

<style scoped>
/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
