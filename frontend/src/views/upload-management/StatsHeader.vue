<script setup lang="ts">
/**
 * 统计仪表盘头部组件
 * 显示累计导入批次、试题数、图片数等统计信息
 */
import { Upload } from '@element-plus/icons-vue';

interface Props {
  totalBatches: number;
  totalQuestions: number;
  totalImages: number;
}

interface Emits {
  (e: 'report-logs'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();
</script>

<template>
  <!-- 统计卡片 - 统一卡片风格 -->
  <div class="px-4 py-3 bg-slate-50 border-b border-slate-200 shrink-0">
    <div class="bg-white rounded-lg shadow-sm border border-slate-200 px-6 py-4 flex items-center justify-between">

      <!-- 左侧：标题 -->
      <div>
        <h1 class="text-xl font-bold text-slate-800">导入管理中心</h1>
        <p class="text-xs text-slate-500 mt-1">管理本地上传批次与监控解析日志</p>
      </div>

      <!-- 中间：统计数据 -->
      <div class="flex items-center gap-8">
        <!-- 累计导入批次 -->
        <div class="flex flex-col">
          <div class="text-xs text-slate-500 mb-1">累计导入批次</div>
          <div class="text-2xl font-bold text-slate-800">{{ totalBatches }}</div>
        </div>

        <!-- 累计试题数 -->
        <div class="flex flex-col">
          <div class="text-xs text-slate-500 mb-1">累计试题数</div>
          <div class="text-2xl font-bold text-blue-600">{{ totalQuestions }}</div>
        </div>

        <!-- 累计图片数 -->
        <div class="flex flex-col">
          <div class="text-xs text-slate-500 mb-1">累计图片数</div>
          <div class="text-2xl font-bold text-purple-600">{{ totalImages }}</div>
        </div>

        <!-- 引擎状态 -->
        <div class="flex flex-col">
          <div class="text-xs text-slate-500 mb-1">引擎状态</div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-green-500"></span>
            <span class="text-sm font-medium text-green-600">运行正常</span>
          </div>
        </div>
      </div>

      <!-- 右侧：操作按钮 -->
      <div class="flex gap-2">
        <el-button
          type="warning"
          :icon="Upload"
          @click="emit('report-logs')"
          plain
          size="small"
        >
          上报日志
        </el-button>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* 组件样式使用 Tailwind CSS */
</style>
