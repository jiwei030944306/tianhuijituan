<!--
  系统日志模块组件
  展示系统日志，支持按级别筛选
-->

<template>
  <div class="flex-1 p-6 overflow-auto">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-bold text-slate-700 text-lg">系统日志</h3>
      <select
        :value="level"
        @change="emit('update:level', ($event.target as HTMLSelectElement).value)"
        class="px-3 py-1.5 text-sm bg-white text-slate-600 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500"
      >
        <option value="all">全部级别</option>
        <option value="INFO">INFO</option>
        <option value="WARN">WARN</option>
        <option value="ERROR">ERROR</option>
      </select>
    </div>

    <div class="space-y-2">
      <div
        v-for="(log, index) in logs"
        :key="index"
        class="flex items-start gap-3 p-3 bg-white rounded-lg border border-slate-200"
      >
        <span
          class="text-xs px-2 py-0.5 rounded font-mono"
          :class="getLevelClass(log.level)"
        >
          {{ log.level }}
        </span>
        <div class="flex-1">
          <div class="text-sm text-slate-700">{{ log.message }}</div>
          <div class="text-xs text-slate-400 mt-1">{{ log.timestamp }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ==========================================
// 类型定义
// ==========================================

interface LogItem {
  level: 'INFO' | 'WARN' | 'ERROR';
  message: string;
  timestamp: string;
}

// ==========================================
// Props & Emits
// ==========================================

defineProps<{
  logs: LogItem[];
  level: string;
}>();

const emit = defineEmits<{
  (e: 'update:level', value: string): void;
}>();

// ==========================================
// 方法
// ==========================================

const getLevelClass = (level: string) => {
  switch (level) {
    case 'INFO': return 'bg-blue-100 text-blue-600';
    case 'WARN': return 'bg-amber-100 text-amber-600';
    case 'ERROR': return 'bg-red-100 text-red-600';
    default: return 'bg-slate-100 text-slate-600';
  }
};
</script>