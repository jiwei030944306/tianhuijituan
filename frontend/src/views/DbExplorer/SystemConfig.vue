<!--
  系统配置模块组件
  展示系统配置项列表
-->

<template>
  <div class="flex-1 p-6 overflow-auto">
    <h3 class="font-bold text-slate-700 text-lg mb-4">系统配置项</h3>
    <div class="space-y-3">
      <div
        v-for="config in configs"
        :key="config.key"
        class="flex items-center justify-between p-4 bg-white rounded-xl border border-slate-200"
      >
        <div>
          <div class="font-medium text-slate-700">{{ config.key }}</div>
          <div class="text-sm text-slate-500">{{ config.description }}</div>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm font-mono bg-slate-100 px-3 py-1 rounded border border-slate-200">
            {{ config.value }}
          </span>
          <button class="text-slate-400 hover:text-indigo-600 transition-colors">
            <Settings :size="16" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Settings } from 'lucide-vue-next';

// ==========================================
// 类型定义
// ==========================================

interface ConfigItem {
  key: string;
  value: string;
  description: string;
}

// ==========================================
// Props
// ==========================================

defineProps<{
  configs: ConfigItem[];
}>();
</script>