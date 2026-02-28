<!-- 
  1. 页面简介 (Page Introduction)
  试题卡组件 (QuestionCard.vue)
  本组件是系统的核心展示组件，负责渲染单个试题的完整信息。
  支持多种状态显示、难度标记、选项高亮、图片预览等功能，是试题列表和详情页的核心展示单元。
-->

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：computed (响应式计算)
 * - 项目类型：Question, Option, StemImage (来自 @/types/question)
 * - 项目组件：MathText (LaTeX 公式渲染)
 * - 图标库：lucide-vue-next (Lucide 图标集)
 */
import { computed } from 'vue';
import type { Question, Option, StemImage } from '@/types/question';
import MathText from '@/components/common/MathText.vue';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  Image as ImageIcon,
  Check,
  Hash,
  Star,
  X
} from 'lucide-vue-next';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- Props 定义 ---
interface QuestionCardProps {
  question: Question;
  onClick?: () => void;
  isSelected?: boolean;
  isActive?: boolean;
  showCheckbox?: boolean;
  onToggleCheck?: (id: string) => void;
  errorMsg?: string;  // 错误消息（用于调试状态）
}

const props = withDefaults(defineProps<QuestionCardProps>(), {
  isSelected: false,
  isActive: false,
  showCheckbox: false
});

// --- 3. 核心代码强调：状态配置映射 ---
// 定义不同题目状态的视觉样式（颜色、背景、边框、图标）
const STATUS_CONFIG: Record<string, { color: string, bg: string, border: string, icon: any, label: string }> = {
  'error': { color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200', icon: AlertTriangle, label: '异常' },
  'waste': { color: 'text-slate-600', bg: 'bg-slate-100', border: 'border-slate-200', icon: AlertTriangle, label: '废题' },
  'confirmed': { color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200', icon: CheckCircle, label: '已确认' },
  'active': { color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200', icon: Clock, label: '待标化' }
};

// --- 3. 核心代码强调：难度映射配置 ---
const DIFFICULTY_MAP: Record<string, { label: string, color: string, bg: string }> = {
  '易': { label: '易', color: 'text-emerald-700', bg: 'bg-emerald-50' },
  '较易': { label: '较易', color: 'text-teal-700', bg: 'bg-teal-50' },
  '中档': { label: '中档', color: 'text-blue-700', bg: 'bg-blue-50' },
  '较难': { label: '较难', color: 'text-amber-700', bg: 'bg-amber-50' },
  '难': { label: '难', color: 'text-rose-700', bg: 'bg-rose-50' }
};

// --- 动态计算属性区 ---

// 获取当前状态样式
const statusStyle = computed(() => {
  return STATUS_CONFIG[props.question.status] || STATUS_CONFIG['active'];
});

// 获取当前难度样式
const difficultyStyle = computed(() => {
  return DIFFICULTY_MAP[props.question.difficulty || '中档'] || DIFFICULTY_MAP['中档'];
});

// 判断是否为选择题（单选/多选）
const isChoiceQuestion = computed(() => {
  return props.question.type === 'single_choice' || props.question.type === 'multiple_choice';
});

// 判断是否为填空题
const isFillInQuestion = computed(() => {
  return props.question.type === 'fill_blank' || props.question.type === 'short_answer';
});

// 判断是否为解答题
const isSubjectiveQuestion = computed(() => {
  return props.question.type === 'subjective';
});

// 判断是否显示答案高亮（已归档或待标化状态）
const shouldHighlightAnswer = computed(() => {
  return (props.question.status === 'confirmed' || props.question.status === 'active') && isChoiceQuestion.value;
});
</script>

<template>
  <!-- ==========================================
       2. 主要功能代码分区注释 - 页面渲染区
       ========================================== -->

  <!-- [Question Card Container] 试题卡片容器 -->
  <div
    class="group relative flex flex-col h-full bg-white rounded-xl transition-all duration-200 cursor-pointer overflow-hidden border hover:shadow-lg"
    :class="[
      // 选中状态：紫色环
      isSelected ? 'ring-2 ring-indigo-600 border-indigo-600 z-10 shadow-md' :
      // 激活状态：蓝色环
      isActive ? 'border-indigo-400 shadow-md ring-1 ring-indigo-50' :
      // 普通状态：灰色边框
      'border-slate-200 hover:border-indigo-300'
    ]"
    @click="onClick"
  >
    <!-- [Header] 顶部：状态徽章和题号 -->
    <div class="px-4 pt-4 pb-2 flex justify-between items-start">
      <div class="flex items-center gap-2">
        <!-- 状态徽章 -->
        <div :class="`flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] font-bold ${statusStyle.bg} ${statusStyle.color}`">
          <component :is="statusStyle.icon" :size="12" :stroke-width="2.5" />
          <span>{{ statusStyle.label }}</span>
        </div>
        <!-- 难度徽章 -->
        <div :class="`px-2 py-1 rounded-md text-[11px] font-bold ${difficultyStyle.bg} ${difficultyStyle.color}`">
          {{ difficultyStyle.label }}
        </div>
      </div>
      <!-- 题号 -->
      <span class="font-mono text-[10px] text-slate-300 group-hover:text-slate-400 transition-colors pt-1">
        {{ props.question.questionNumber ? `#${String(props.question.questionNumber).padStart(2, '0')}` : props.question.id.substring(0, 4) }}
      </span>
    </div>

    <!-- [Body] 中部：题干、选项、图片 -->
    <div class="px-4 py-2 flex-1 min-h-[4rem] flex flex-col gap-3">
      <!-- 题干 -->
      <div :class="`text-sm text-slate-800 leading-7 font-serif ${props.question.status === 'error' ? 'opacity-80' : ''}`">
        <MathText :text="props.question.stem" />
      </div>

      <!-- 图片展示 -->
      <div v-if="props.question.stemImages && props.question.stemImages.length > 0" class="flex flex-col gap-2 mt-2">
        <div
          v-for="(img, idx) in props.question.stemImages"
          :key="idx"
          class="relative rounded-lg border border-slate-100 bg-slate-50 p-2 flex items-center justify-center"
        >
          <img
            :src="img.src"
            alt="Stem"
            class="max-w-full max-h-32 object-contain"
            @error="(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              target.parentElement?.classList.add('hidden');
            }"
          />
        </div>
      </div>

      <!-- 选项列表（仅选择题） -->
      <div v-if="isChoiceQuestion && props.question.options && props.question.options.length > 0" class="flex flex-col gap-1.5 mt-1">
        <div
          v-for="opt in props.question.options"
          :key="opt.key || opt.label"
          class="flex items-start gap-2.5 text-xs p-1.5 rounded-lg transition-colors"
          :class="shouldHighlightAnswer && (opt.isCorrect || props.question.answer?.includes(opt.key || opt.label)) ? 'bg-emerald-50/60' : 'hover:bg-slate-50'"
        >
          <!-- 选项标识 -->
          <span
            :class="[
              'w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5',
              shouldHighlightAnswer && (opt.isCorrect || props.question.answer?.includes(opt.key || opt.label))
                ? 'bg-emerald-500 text-white shadow-sm'
                : 'bg-slate-100 text-slate-500 border border border-slate-200'
            ]"
          >
            {{ opt.key || opt.label }}
          </span>
          <!-- 选项内容 -->
          <div
            :class="[
              'flex-1 leading-relaxed',
              shouldHighlightAnswer && (opt.isCorrect || props.question.answer?.includes(opt.key || opt.label))
                ? 'text-emerald-800 font-medium'
                : 'text-slate-600'
            ]"
          >
            <MathText v-if="opt.content" :text="opt.content" />
            <span v-else-if="opt.image" class="text-slate-400 text-[10px]">[图片选项]</span>
          </div>
        </div>
      </div>

      <!-- 填空题/解答题提示 -->
      <div v-if="!isChoiceQuestion" class="text-[10px] text-slate-300 italic mt-2">
        <span v-if="isFillInQuestion">填空题 (Fill-in)</span>
        <span v-else-if="isSubjectiveQuestion">解答题 (Subjective)</span>
      </div>
    </div>

    <!-- [Footer] 底部：标签信息 -->
    <div class="px-4 py-3 mt-auto flex flex-wrap gap-2 items-center border-t border-slate-50">
      <!-- 年级标签 -->
      <span v-if="props.question.grade" class="text-[10px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
        {{ props.question.grade }}年级
      </span>
      <!-- 知识点标签 -->
      <span v-if="props.question.topics && props.question.topics.length > 0" class="text-[10px] font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100 flex items-center gap-0.5">
        <Hash :size="10" class="opacity-50" />
        {{ props.question.topics[0] }}
      </span>
      <!-- 题类标签 -->
      <span
        v-if="props.question.category"
        class="text-[10px] font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded border border-amber-100 flex items-center gap-0.5"
      >
        <Star :size="10" class="fill-amber-600 text-amber-600" />
        {{ props.question.category }}
      </span>
    </div>

    <!-- [Error Overlay] 错误提示层（仅异常状态显示） -->
    <div
      v-if="props.question.status === 'error' && (props.errorMsg || props.question.statusMessage)"
      class="bg-red-50 px-4 py-2.5 border-t border-red-100 flex items-center gap-2 text-[10px] text-red-600 font-bold"
    >
      <AlertTriangle :size="12" class="shrink-0 fill-red-100" />
      <span class="truncate">{{ props.errorMsg || props.question.statusMessage }}</span>
    </div>

    <!-- [Checkbox] 复选框（右上角，可选） -->
    <div
      v-if="showCheckbox"
      class="absolute top-4 right-4 z-20"
      @click="(e) => { e.stopPropagation(); onToggleCheck && onToggleCheck(props.question.id); }"
    >
      <div
        :class="[
          'w-5 h-5 rounded-md border transition-all flex items-center justify-center cursor-pointer shadow-sm',
          isSelected
            ? 'bg-indigo-600 border-indigo-600 text-white scale-110'
            : 'bg-white border-slate-300 text-transparent hover:border-indigo-400 hover:scale-105'
        ]"
      >
        <Check v-if="isSelected" :size="14" :stroke-width="3" />
        <X v-else :size="14" :stroke-width="2" />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 组件样式使用 Tailwind CSS，无需额外样式 */
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>