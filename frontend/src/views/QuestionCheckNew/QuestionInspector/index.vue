<script setup lang="ts">
import { ref, watch } from 'vue';
import { FileCode, X, Eye, Code2, Copy, Sparkles } from 'lucide-vue-next';
import PreviewTab from './PreviewTab.vue';
import JsonTab from './JsonTab.vue';
import AiTab from './AiTab.vue';
import type { Question } from '@/types/question'; // 使用共享类型

// ==================== Props 定义 ====================

interface Props {
  question: Question | null;  // 选中的题目
  visible: boolean;           // 是否可见
}

const props = defineProps<Props>();

// ==================== Events 定义 ====================

const emit = defineEmits<{
  close: [];  // 关闭检视器
  'update-question': [question: Question]; // 更新题目
}>();

// ==================== 状态管理 ====================

// 当前激活的标签页
const inspectorTab = ref<'preview' | 'json' | 'ai'>('preview');

// JSON内容
const codeContent = ref('');

// JSON错误
const jsonError = ref<string | null>(null);

// ==================== 监听题目变化 ====================

watch(() => props.question, (newQuestion) => {
  if (newQuestion) {
    // 重置为预览标签页
    inspectorTab.value = 'preview';
    // 更新JSON内容
    codeContent.value = JSON.stringify(newQuestion, null, 2);
    // 清空错误
    jsonError.value = null;
  }
}, { immediate: true });

// ==================== 方法 ====================

// 关闭检视器
const handleClose = () => {
  emit('close');
};

// 保存JSON修改(模拟)
const handleSaveCode = () => {
  try {
    const parsed = JSON.parse(codeContent.value);
    jsonError.value = null;
    emit('update-question', parsed); // 将修改后的数据回传
    // console.log('JSON valid and saved');
  } catch (e: any) {
    jsonError.value = e.message;
  }
};
</script>

<template>
  <!-- 检视器容器 -->
  <div
    v-if="visible && question"
    class="absolute top-0 right-0 bottom-0 w-[600px] bg-white border-l border-slate-200 shadow-[0_0_40px_rgba(0,0,0,0.1)] z-50 flex flex-col transition-all duration-300 animate-slide-in-right"
  >
    <!-- 检视器头部 -->
    <div
      class="h-14 border-b flex items-center justify-between px-4 shrink-0 bg-slate-50 border-slate-200"
    >
      <div class="flex items-center gap-3">
        <div class="p-1.5 bg-white border border-slate-200 rounded text-slate-500">
           <FileCode :size="16" />
        </div>
        <div class="flex flex-col">
           <span class="font-bold text-sm text-slate-700">单行数据检视</span>
           <span class="text-[10px] text-slate-400 font-mono">{{ question.id }}</span>
        </div>
      </div>
      <button @click="handleClose" class="text-slate-400 hover:text-slate-600 p-1 hover:bg-slate-100 rounded-lg transition-colors">
        <X :size="20"/>
      </button>
    </div>

    <!-- 标签页导航 -->
    <div class="flex border-b border-slate-200 bg-white shrink-0 px-2">
      <button
        @click="inspectorTab = 'preview'"
        :class="[
          'flex items-center justify-center gap-2 px-4 py-3 text-xs font-bold transition-colors relative',
          inspectorTab === 'preview' ? 'text-indigo-600' : 'text-slate-500 hover:text-slate-700'
        ]"
      >
        <Eye :size="14"/> 渲染预览
        <div v-if="inspectorTab === 'preview'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 rounded-t-full"></div>
      </button>
      <button
        @click="inspectorTab = 'json'"
        :class="[
          'flex items-center justify-center gap-2 px-4 py-3 text-xs font-bold transition-colors relative',
          inspectorTab === 'json' ? 'text-indigo-600' : 'text-slate-500 hover:text-slate-700'
        ]"
      >
        <Code2 :size="14"/> JSON 源码
        <div v-if="inspectorTab === 'json'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 rounded-t-full"></div>
      </button>
      <button
        @click="inspectorTab = 'ai'"
        :class="[
          'flex items-center justify-center gap-2 px-4 py-3 text-xs font-bold transition-colors relative',
          inspectorTab === 'ai' ? 'text-purple-600' : 'text-slate-500 hover:text-slate-700'
        ]"
      >
        <Sparkles :size="14"/> AI 优化工作台
        <div v-if="inspectorTab === 'ai'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-600 rounded-t-full"></div>
      </button>
    </div>

    <!-- 内容区域 -->
    <div class="flex-1 overflow-y-auto p-0 relative bg-slate-50/50">
      <!-- 预览标签页 -->
      <PreviewTab
        v-if="inspectorTab === 'preview'"
        :question="question"
      />

      <!-- JSON 标签页 -->
      <JsonTab
        v-if="inspectorTab === 'json'"
        v-model:code="codeContent"
        :json-error="jsonError"
        @save="handleSaveCode"
      />

      <!-- AI 标签页 -->
      <AiTab
        v-if="inspectorTab === 'ai'"
        :question="question"
        @update-question="emit('update-question', $event)"
      />
    </div>

    <!-- 底部操作按钮 -->
    <div class="p-4 border-t border-slate-200 bg-white shrink-0 flex gap-3" v-if="inspectorTab === 'json'">
      <button class="flex-1 py-2.5 bg-white border border-slate-300 rounded-lg text-xs font-bold text-slate-700 hover:border-indigo-300 hover:text-indigo-600 transition-colors flex items-center justify-center gap-2">
        <Copy :size="14"/> 复制 JSON
      </button>
      <button
        @click="handleSaveCode"
        class="flex-1 py-2.5 bg-indigo-600 rounded-lg text-xs font-bold text-white hover:bg-indigo-700 transition-colors shadow-sm shadow-indigo-200"
      >
        保存修改 (Save)
      </button>
    </div>
  </div>
</template>

<style scoped>
/* 动画效果 */
@keyframes slide-in-right {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animate-slide-in-right {
  animation: slide-in-right 0.3s ease-out;
}
</style>
