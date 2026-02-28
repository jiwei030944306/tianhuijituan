<script setup lang="ts">
import { AlertTriangle, PieChart } from 'lucide-vue-next';

// ==================== Props 定义 ====================

interface FileStats {
  total: number;         // 总题量
  single: number;        // 单选题数量
  multi: number;         // 多选题数量
  fill: number;          // 填空题数量
  calculation: number;  // 计算题数量
  application: number;   // 应用题数量
  subjective: number;    // 解答题数量
  errorCount: number;    // 错误数量
}

interface Props {
  fileStats: FileStats | null;  // 统计数据
  selectedFile: string | null;   // 是否已选择批次
}

const props = defineProps<Props>();
</script>

<template>
  <!-- 统计卡片 - 卡片风格（参考上传管理中心） -->
  <div class="px-4 py-3 bg-slate-50 border-b border-slate-200 shrink-0">
    <div class="bg-white rounded-lg shadow-sm border border-slate-200 px-6 py-4 flex items-center gap-8">

      <!-- 总题量 -->
      <div class="flex flex-col">
        <div class="text-xs text-slate-500 mb-1">导入题数</div>
        <div class="text-2xl font-bold text-slate-800">
          {{ fileStats && selectedFile ? fileStats.total : '--' }}
        </div>
      </div>

      <!-- 单选题 -->
      <div class="flex flex-col">
        <div class="text-xs text-slate-500 mb-1">单选题数</div>
        <div class="text-2xl font-bold text-blue-600">
          {{ fileStats && selectedFile ? fileStats.single : '--' }}
        </div>
      </div>

      <!-- 多选题 -->
      <div class="flex flex-col">
        <div class="text-xs text-slate-500 mb-1">多选题数</div>
        <div class="text-2xl font-bold text-orange-600">
          {{ fileStats && selectedFile ? fileStats.multi : '--' }}
        </div>
      </div>

      <!-- 填空题 -->
      <div class="flex flex-col">
        <div class="text-xs text-slate-500 mb-1">填空题数</div>
        <div class="text-2xl font-bold text-emerald-600">
          {{ fileStats && selectedFile ? fileStats.fill : '--' }}
        </div>
      </div>

      <!-- 计算题 -->
      <div class="flex flex-col">
        <div class="text-xs text-slate-500 mb-1">计算题数</div>
        <div class="text-2xl font-bold text-purple-600">
          {{ fileStats && selectedFile ? fileStats.calculation : '--' }}
        </div>
      </div>

      <!-- 应用题 -->
      <div class="flex flex-col">
        <div class="text-xs text-slate-500 mb-1">应用题数</div>
        <div class="text-2xl font-bold text-pink-600">
          {{ fileStats && selectedFile ? fileStats.application : '--' }}
        </div>
      </div>

      <!-- 解答题 -->
      <div class="flex flex-col">
        <div class="text-xs text-slate-500 mb-1">解答题数</div>
        <div class="text-2xl font-bold text-slate-600">
          {{ fileStats && selectedFile ? fileStats.subjective : '--' }}
        </div>
      </div>

      <!-- 数据状态 -->
      <div class="flex flex-col">
        <div class="text-xs text-slate-500 mb-1">引擎状态</div>
        <div class="flex items-center gap-2">
          <span
            v-if="fileStats && fileStats.errorCount > 0"
            class="flex items-center gap-1 text-sm font-medium text-red-600"
          >
            <span class="w-2 h-2 rounded-full bg-red-500"></span>
            发现异常
          </span>
          <span
            v-else-if="fileStats && selectedFile"
            class="flex items-center gap-1 text-sm font-medium text-green-600"
          >
            <span class="w-2 h-2 rounded-full bg-green-500"></span>
            运行正常
          </span>
          <span
            v-else
            class="flex items-center gap-1 text-sm font-medium text-slate-400"
          >
            <span class="w-2 h-2 rounded-full bg-slate-300"></span>
            未选择批次
          </span>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* 统计卡片样式 */
</style>
