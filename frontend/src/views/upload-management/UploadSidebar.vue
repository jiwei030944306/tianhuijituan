<script setup lang="ts">
/**
 * 上传侧边栏组件
 * 包含:环境信息、上传区域、处理日志、待处理队列
 */
import {
  UploadFilled,
  Document,
  Delete,
  Loading,
  Bell,
  View,
  Folder
} from '@element-plus/icons-vue';

interface UploadLog {
  time: string;
  level: 'info' | 'success' | 'warning' | 'error';
  msg: string;
  timestamp?: number;
}

interface Props {
  files: File[];
  uploading: boolean;
  progress: number;
  uploadLogs: UploadLog[];
  logSummary: UploadLog[];
  currentGrade: string;
  currentSubject: string;
  currentTeacher: string;
  folderCode: string;
}

interface Emits {
  (e: 'file-select', event: Event): void;
  (e: 'upload-start'): void;
  (e: 'clear-files'): void;
  (e: 'remove-file', index: number): void;
  (e: 'open-debugger'): void;
  (e: 'file-input-click'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// 获取日志图标
const getLogIcon = (level: string) => {
  switch (level) {
    case 'success': return '✅';
    case 'warning': return '⚠️';
    case 'error': return '❌';
    default: return 'ℹ️';
  }
};

// 获取日志颜色类
const getLogColor = (level: string) => {
  switch (level) {
    case 'success': return 'text-green-600';
    case 'warning': return 'text-yellow-600';
    case 'error': return 'text-red-600';
    default: return 'text-blue-600';
  }
};
</script>

<template>
  <!-- LEFT SIDEBAR: OPERATION ZONE -->
  <div class="w-[15%] bg-white border-r border-slate-200 flex flex-col z-10 shadow-sm">
    <!-- Header with Environment Info -->
    <div class="p-4 border-b border-slate-100">
      <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
        <el-icon class="text-green-600"><UploadFilled /></el-icon>
        资源导入
      </h2>
      <div class="flex items-center gap-2 text-xs text-slate-500 mt-2">
        <el-icon><Folder /></el-icon>
        <span>{{ currentGrade }}</span>
        <span>|</span>
        <span>{{ currentSubject }}</span>
        <span>|</span>
        <span>{{ currentTeacher }}</span>
      </div>
      <div class="flex items-center gap-2 text-xs text-slate-400 mt-1">
        <el-icon><Document /></el-icon>
        <span>代码:{{ folderCode }}</span>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 p-4 flex flex-col overflow-y-auto">
      <!-- Upload Area (Small Height) -->
      <div v-if="!uploading" class="mb-3">
        <div
          class="h-24 border-2 border-dashed border-green-300 bg-green-50/30 rounded-lg flex flex-col items-center justify-center transition-all cursor-pointer hover:bg-green-50 hover:border-green-500"
          @click="emit('file-input-click')"
        >
          <el-icon class="text-green-600 text-xl mb-1"><UploadFilled /></el-icon>
          <span class="text-xs font-bold text-green-700">点击上传 ZIP/JSON</span>
          <span class="text-[10px] text-green-500">支持 .zip .json 格式</span>
        </div>
      </div>

      <!-- Uploading State -->
      <div v-else class="h-24 bg-green-50 rounded-lg flex flex-col items-center justify-center border border-green-200 mb-3 px-4 text-center">
        <el-icon class="text-green-600 text-xl animate-spin mb-1"><Loading /></el-icon>
        <p class="font-bold text-green-900 text-xs">正在导入数据...</p>
        <el-progress :percentage="progress" class="w-full mt-2" :stroke-width="6" status="success" />
      </div>

      <!-- Processing Logs (Brief) -->
      <div class="mb-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <el-icon><Bell /></el-icon>
            处理日志
          </span>
          <button
            v-if="uploadLogs.length > 0"
            @click="emit('open-debugger')"
            class="text-[10px] text-green-600 hover:text-green-700 flex items-center gap-0.5"
          >
            <el-icon><View /></el-icon>
            查看详情
          </button>
        </div>
        <div class="bg-slate-100 rounded-lg p-2 space-y-1">
          <div v-if="uploadLogs.length === 0" class="text-[10px] text-slate-400 text-center py-2">
            暂无处理日志
          </div>
          <div
            v-for="(log, i) in logSummary"
            :key="i"
            class="text-[10px] flex items-start gap-1.5"
          >
            <span>{{ getLogIcon(log.level) }}</span>
            <span :class="getLogColor(log.level)" class="truncate">{{ log.msg }}</span>
          </div>
        </div>
      </div>

      <!-- Queue List -->
      <div class="flex-1 min-h-0 flex flex-col">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">
            待处理队列 ({{ files.length }})
          </span>
          <button
            v-if="files.length > 0 && !uploading"
            @click="emit('clear-files')"
            class="text-[10px] text-slate-400 hover:text-red-500 transition-colors"
          >
            清空
          </button>
        </div>

        <div class="flex-1 overflow-y-auto border border-slate-100 rounded-lg bg-slate-50 p-2 space-y-2">
          <div v-if="files.length === 0" class="h-full flex flex-col items-center justify-center text-slate-300">
            <el-icon class="text-2xl mb-1 opacity-50"><Document /></el-icon>
            <span class="text-[10px]">暂无文件</span>
          </div>

          <div
            v-for="(file, index) in files"
            :key="index"
            class="flex items-center gap-2 p-2 bg-white border border-slate-200 rounded-md shadow-sm"
          >
            <div class="w-6 h-6 rounded bg-green-50 text-green-600 flex items-center justify-center shrink-0">
              <el-icon><Document /></el-icon>
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-xs font-bold text-slate-700 truncate" :title="file.name">
                {{ file.name }}
              </div>
            </div>
            <button
              v-if="!uploading"
              @click="emit('remove-file', index)"
              class="text-slate-300 hover:text-red-500 transition-colors"
            >
              <el-icon><Delete /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Action -->
    <div class="p-4 border-t border-slate-100 bg-slate-50">
      <el-button
        type="primary"
        size="large"
        class="w-full"
        :disabled="files.length === 0 || uploading"
        @click="emit('upload-start')"
      >
        {{ uploading ? '处理中...' : '开始导入处理' }}
      </el-button>
    </div>
  </div>
</template>

<style scoped>
/* 组件样式使用 Tailwind CSS */
</style>
