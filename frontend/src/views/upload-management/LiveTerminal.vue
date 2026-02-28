<script setup lang="ts">
/**
 * 实时终端组件
 * 显示上传处理的实时日志
 */
import { Monitor } from '@element-plus/icons-vue';

interface UploadLog {
  time: string;
  level: 'info' | 'success' | 'warning' | 'error';
  msg: string;
  timestamp?: number;
}

interface Props {
  uploadLogs: UploadLog[];
  uploading: boolean;
}

const props = defineProps<Props>();
</script>

<template>
  <!-- LIVE TERMINAL -->
  <div class="absolute inset-0 bg-[#1e1e1e] p-4 font-mono text-xs overflow-y-auto">
    <div v-if="uploadLogs.length === 0" class="h-full flex flex-col items-center justify-center text-slate-600 opacity-50">
      <el-icon class="text-4xl mb-3"><Monitor /></el-icon>
      <p>Terminal Ready. Waiting for jobs...</p>
    </div>

    <div v-else class="space-y-1">
      <div class="text-slate-500 mb-2 pb-2 border-b border-slate-700">
        {{ new Date().toString() }}
      </div>
      <div
        v-for="(log, i) in uploadLogs"
        :key="i"
        class="flex gap-2"
      >
        <span class="text-slate-500 shrink-0">[{{ log.time }}]</span>
        <span :class="{
          'text-green-400': log.level === 'success',
          'text-red-400 font-bold': log.level === 'error',
          'text-yellow-400': log.level === 'warning',
          'text-slate-300': log.level === 'info'
        }">
          <span v-if="log.level === 'info'" class="text-blue-500 mr-1">ℹ</span>
          <span v-else-if="log.level === 'success'" class="text-green-500 mr-1">✔</span>
          <span v-else-if="log.level === 'warning'" class="text-yellow-500 mr-1">⚠</span>
          <span v-else-if="log.level === 'error'" class="text-red-500 mr-1">✖</span>
          {{ log.msg }}
        </span>
      </div>
      <div v-if="uploading" class="animate-pulse text-indigo-400 mt-2">_</div>
    </div>
  </div>
</template>

<style scoped>
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #1e1e1e;
}

::-webkit-scrollbar-thumb {
  background: #424242;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #4f4f4f;
}
</style>
