<script setup lang="ts">
import { Search, Sparkles } from 'lucide-vue-next';

// ==================== Props 定义 ====================

interface Filters {
  keyword: string;
  type: string;
  difficulty: string;
  status?: string;
  isAiOptimized?: boolean;
}

interface SelectOption {
  value: string;
  label: string;
}

interface Props {
  filters: any;                       // 暂用 any 兼容
  typeOptions: SelectOption[];          // 题型选项
  difficultyOptions: SelectOption[];    // 难度选项
}

const props = defineProps<Props>();

// ==================== Events 定义 ====================

const emit = defineEmits<{
  'update:filters': [filters: any];  // 更新筛选条件
  'clear-filters': [];                    // 清空筛选
}>();

// ==================== 方法 ====================

// 更新筛选器通用方法
const updateFilter = (key: string, value: any) => {
  emit('update:filters', { ...props.filters, [key]: value });
};

// 快捷筛选：异常题目
const filterErrorQuestions = () => {
  emit('update:filters', { ...props.filters, status: 'error' });
};

// 快捷筛选：待优化
const filterPendingOptimization = () => {
  emit('update:filters', { ...props.filters, isAiOptimized: false });
};
</script>

<template>
  <!-- 筛选器工具栏 - 卡片风格 -->
  <div class="px-4 py-3 bg-slate-50 shrink-0">
    <div class="flex items-center justify-between gap-4">
      <!-- 左侧：搜索框 -->
      <div class="relative flex-1 max-w-sm">
        <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"/>
        <input
          type="text"
          :value="filters.keyword"
          @input="updateFilter('keyword', ($event.target as HTMLInputElement).value)"
          placeholder="搜索题干或ID..."
          class="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-md focus:ring-1 focus:ring-blue-500 outline-none transition-all shadow-sm"
        />
      </div>

      <!-- 右侧：下拉筛选 -->
      <div class="flex items-center gap-2">
        <!-- 快捷筛选：异常题目 -->
        <button
          @click="filterErrorQuestions"
          :class="[
            'px-3 py-1.5 text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5',
            filters.status === 'error'
              ? 'bg-indigo-100 text-indigo-700 ring-1 ring-indigo-300'
              : 'text-indigo-600 bg-indigo-50 hover:bg-indigo-100'
          ]"
        >
          <span class="w-2 h-2 rounded-full bg-red-500"></span>
          异常题目
        </button>

        <!-- 快捷筛选：待优化 -->
        <button
          @click="filterPendingOptimization"
          :class="[
            'px-3 py-1.5 text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5',
            filters.isAiOptimized === false
              ? 'bg-purple-100 text-purple-700 ring-1 ring-purple-300'
              : 'text-purple-600 bg-purple-50 hover:bg-purple-100'
          ]"
        >
          <Sparkles :size="12" />
          待优化
        </button>

        <!-- 难度筛选 -->
        <select
          :value="filters.difficulty"
          @change="updateFilter('difficulty', ($event.target as HTMLSelectElement).value)"
          class="pl-2 pr-6 py-1.5 text-xs border border-slate-300 rounded-md bg-white outline-none cursor-pointer shadow-sm hover:border-slate-400 transition-colors"
        >
          <option value="ALL">全部难度</option>
          <option v-for="opt in difficultyOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>

        <!-- 题型筛选 -->
        <select
          :value="filters.type"
          @change="updateFilter('type', ($event.target as HTMLSelectElement).value)"
          class="pl-2 pr-6 py-1.5 text-xs border border-slate-300 rounded-md bg-white outline-none cursor-pointer shadow-sm hover:border-slate-400 transition-colors"
        >
          <option value="ALL">全部题型</option>
          <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>

        <!-- 重置按钮 - 始终显示，方便用户快速清空筛选 -->
        <button
          @click="emit('clear-filters')"
          class="text-xs text-slate-500 hover:text-indigo-600 px-2"
        >
          重置
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 筛选器样式 */
</style>
