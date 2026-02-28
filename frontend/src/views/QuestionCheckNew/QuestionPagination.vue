<script setup lang="ts">
import { ChevronLeft, ChevronRight } from 'lucide-vue-next';

// ==================== Props 定义 ====================

interface Props {
  currentPage: number;    // 当前页码
  totalPages: number;     // 总页数
  totalItems: number;     // 总条数
  pageSize: number;       // 每页条数
}

const props = defineProps<Props>();

// ==================== Events 定义 ====================

const emit = defineEmits<{
  'page-change': [page: number];  // 页码变更
}>();

// ==================== 计算属性 ====================

// 当前显示的起始条数
const startItem = () => {
  return (props.currentPage - 1) * props.pageSize + 1;
};

// 当前显示的结束条数
const endItem = () => {
  return Math.min(props.currentPage * props.pageSize, props.totalItems);
};

// ==================== 方法 ====================

// 上一页
const previousPage = () => {
  if (props.currentPage > 1) {
    emit('page-change', props.currentPage - 1);
  }
};

// 下一页
const nextPage = () => {
  if (props.currentPage < props.totalPages) {
    emit('page-change', props.currentPage + 1);
  }
};
</script>

<template>
  <!-- 分页器 -->
  <div class="h-10 border-t border-slate-200 bg-slate-50 flex items-center justify-between px-4 shrink-0 select-none">
    <!-- 显示信息 -->
    <span class="text-xs text-slate-500">
      显示 {{ startItem() }} - {{ endItem() }} 条,共 {{ totalItems }} 条
    </span>

    <!-- 分页控件 -->
    <div class="flex items-center gap-2">
      <!-- 上一页按钮 -->
      <button
        @click="previousPage"
        :disabled="currentPage === 1"
        class="p-1 rounded-md hover:bg-slate-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-slate-600"
      >
        <ChevronLeft :size="16"/>
      </button>

      <!-- 页码显示 -->
      <span class="text-xs font-mono font-medium text-slate-700 bg-white border border-slate-200 px-2 py-0.5 rounded-md shadow-sm min-w-[3rem] text-center">
        {{ currentPage }} / {{ totalPages }}
      </span>

      <!-- 下一页按钮 -->
      <button
        @click="nextPage"
        :disabled="currentPage === totalPages"
        class="p-1 rounded-md hover:bg-slate-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-slate-600"
      >
        <ChevronRight :size="16"/>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* 分页器样式 */
</style>
