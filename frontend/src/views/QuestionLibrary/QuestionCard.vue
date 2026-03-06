<script setup lang="ts">
import { ref, computed } from 'vue';
import { ChevronDown, ChevronUp, Edit3, CheckCircle2, Trash2, Copy } from 'lucide-vue-next';
import type { Question } from '@/types/question';
import { getDifficultyLabel, gradeLabels, type Difficulty } from '@/types/question';
import MathText from '@/components/common/MathText.vue';

interface Props {
  question: Question;
}

const props = defineProps<Props>();

// 定义事件
const emit = defineEmits<{
  (e: 'delete', id: string): void;
}>();

const isExpanded = ref(false);

// 切换展开/收起
const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
};

// 删除处理
const handleDelete = () => {
  if (confirm('确定要删除这道题目吗？')) {
    emit('delete', props.question.id);
  }
};

// 难度样式映射
const difficultyStyle = computed(() => {
  const diff = props.question.difficulty as Difficulty;
  const styles: Record<string, string> = {
    'easy': 'bg-green-50 text-green-600',
    'medium_easy': 'bg-emerald-50 text-emerald-600',
    'medium': 'bg-amber-50 text-amber-600',
    'medium_hard': 'bg-orange-50 text-orange-600',
    'hard': 'bg-red-50 text-red-600'
  };
  return styles[diff] || 'bg-slate-100 text-slate-600';
});

// 难度中文
const difficultyLabel = computed(() => {
  return getDifficultyLabel(props.question.difficulty);
});

// 年级中文
const gradeLabel = computed(() => {
  const grade = props.question.grade;
  return grade ? (gradeLabels[grade] || `${grade}年级`) : '-';
});

// 解析内容（优先 AI 解析）
const analysisContent = computed(() => {
  return props.question.aiAnalysis || props.question.analysis || '暂无解析';
});

// 是否有选项
const hasOptions = computed(() => {
  return props.question.options && props.question.options.length > 0;
});

// 正确答案
const correctAnswer = computed(() => {
  return props.question.answer || '-';
});

// 格式化时间
const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
  } catch {
    return '-';
  }
};

// 题类样式
const categoryStyle = computed(() => {
  const cat = props.question.category;
  const styles: Record<string, string> = {
    '常考题': 'bg-indigo-50 text-indigo-600',
    '易错题': 'bg-rose-50 text-rose-600',
    '好题': 'bg-emerald-50 text-emerald-600',
    '压轴题': 'bg-violet-50 text-violet-600',
    '优选题': 'bg-sky-50 text-sky-600'
  };
  return styles[cat || ''] || 'bg-slate-100 text-slate-600';
});

// 判断选项是否是正确答案
const isCorrectOption = (option: { label?: string; key?: string; content: string }) => {
  const label = option.label || option.key || '';
  return props.question.answer?.includes(label);
};

// 是否为相似题
const isDuplicate = computed(() => props.question.isDuplicate === true);
</script>

<template>
  <div
    :class="[
      'bg-white rounded-xl border transition-all duration-300',
      isExpanded ? 'shadow-lg border-indigo-200' : 'hover:shadow-md',
      question.status === 'error' ? 'border-red-300 bg-red-50/30' :
      question.status === 'waste' ? 'border-slate-300 bg-slate-50/50' :
      isDuplicate ? 'border-amber-300 bg-amber-50/30' :
      'border-slate-200'
    ]"
  >
    <!-- 收起状态：简洁预览 -->
    <div
      v-if="!isExpanded"
      class="p-4 cursor-pointer"
      @click="toggleExpand"
    >
      <div class="flex items-start justify-between gap-4">
        <div class="flex-1 min-w-0">
          <!-- 顶部：题号 + 状态标签 -->
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xs font-mono text-slate-400">#{{ question.questionNumber || '?' }}</span>
            <span
              v-if="question.status === 'error'"
              class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-red-100 text-red-700"
            >
              错误
            </span>
            <span
              v-if="question.status === 'waste'"
              class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-200 text-slate-600"
            >
              废题
            </span>
            <span
              v-if="question.isAiOptimized"
              class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-purple-100 text-purple-700"
            >
              AI优化
            </span>
            <span
              v-if="isDuplicate"
              class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-amber-100 text-amber-700 flex items-center gap-0.5"
            >
              <Copy :size="10" />
              相似题
            </span>
          </div>

          <!-- 题目内容预览 -->
          <div class="text-sm text-slate-800 line-clamp-2 mb-3">
            {{ question.stem?.substring(0, 200) || '无内容' }}
            <span v-if="question.stem && question.stem.length > 200">...</span>
          </div>

          <!-- 标签区 -->
          <div class="flex items-center gap-1.5 flex-wrap">
            <span
              v-if="question.type"
              class="px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 text-xs font-medium"
            >
              {{ question.type }}
            </span>
            <span
              v-if="question.difficulty"
              :class="['px-2 py-0.5 rounded-full text-xs font-medium', difficultyStyle]"
            >
              {{ difficultyLabel }}
            </span>
            <span
              v-if="question.category"
              :class="['px-2 py-0.5 rounded-full text-xs font-medium', categoryStyle]"
            >
              {{ question.category }}
            </span>
            <span
              v-for="topic in question.topics?.slice(0, 3)"
              :key="topic"
              class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs"
            >
              {{ topic }}
            </span>
            <span
              v-if="question.topics && question.topics.length > 3"
              class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 text-xs"
            >
              +{{ question.topics.length - 3 }}
            </span>
          </div>

          <!-- 来源信息 -->
          <div v-if="question.source" class="mt-2 text-xs text-slate-400">
            来源: {{ question.source }}
          </div>
        </div>

        <!-- 展开提示图标 -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <ChevronDown :size="20" class="text-slate-400" />
        </div>
      </div>
    </div>

    <!-- 展开状态：紧凑展示 -->
    <div v-else class="p-3">
      <!-- 顶部工具栏 -->
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-1.5">
          <span class="text-xs font-mono text-slate-500">#{{ question.questionNumber || '?' }}</span>
          <span v-if="question.status === 'error'" class="px-1 py-0.5 rounded text-[10px] bg-red-100 text-red-700">错误</span>
          <span v-if="question.status === 'waste'" class="px-1 py-0.5 rounded text-[10px] bg-slate-200 text-slate-600">废题</span>
          <span v-if="question.isAiOptimized" class="px-1 py-0.5 rounded text-[10px] bg-purple-100 text-purple-700">AI优化</span>
          <span v-if="isDuplicate" class="px-1 py-0.5 rounded text-[10px] bg-amber-100 text-amber-700 flex items-center gap-0.5">
            <Copy :size="10" />
            相似题
          </span>
        </div>
        <div class="flex items-center gap-1">
          <button v-if="isDuplicate" @click.stop="handleDelete" class="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="删除">
            <Trash2 :size="14" />
          </button>
          <button @click.stop class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors" title="编辑">
            <Edit3 :size="14" />
          </button>
          <button @click="toggleExpand" class="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded transition-colors" title="收起">
            <ChevronUp :size="16" />
          </button>
        </div>
      </div>

      <!-- 题目内容 -->
      <div class="text-sm text-slate-800 mb-2 leading-relaxed">
        <MathText :text="question.stem || '无内容'" />
      </div>

      <!-- 选项（横向排列，更紧凑） -->
      <div v-if="hasOptions" class="flex flex-wrap gap-2 mb-2">
        <div
          v-for="(option, index) in question.options"
          :key="index"
          :class="[
            'flex items-center gap-1.5 px-2 py-1 rounded border text-xs',
            isCorrectOption(option) ? 'bg-green-50 border-green-300 text-green-700' : 'bg-slate-50 border-slate-200 text-slate-600'
          ]"
        >
          <span :class="['w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-medium', isCorrectOption(option) ? 'bg-green-500 text-white' : 'bg-slate-200 text-slate-500']">
            {{ option.label || option.key || String.fromCharCode(65 + index) }}
          </span>
          <MathText :text="option.content" class="max-w-[200px]" />
          <CheckCircle2 v-if="isCorrectOption(option)" :size="12" class="text-green-500" />
        </div>
      </div>

      <!-- 答案 + 解析（一行） -->
      <div class="flex gap-3 mb-2">
        <div class="flex items-center gap-1.5 px-2 py-1 bg-indigo-50 rounded">
          <span class="text-xs text-indigo-500">答案</span>
          <span class="text-sm font-semibold text-indigo-700">{{ correctAnswer }}</span>
        </div>
        <div class="flex-1 px-2 py-1 bg-amber-50 rounded overflow-hidden">
          <span class="text-xs text-amber-500 mr-1">解析<span v-if="question.aiAnalysis" class="text-purple-400">(AI)</span>:</span>
          <MathText :text="analysisContent" font-size="text-xs" color="text-amber-800" />
        </div>
      </div>

      <!-- 属性标签（一行） -->
      <div class="flex items-center gap-1.5 flex-wrap text-xs">
        <span v-if="question.type" class="px-1.5 py-0.5 rounded bg-blue-50 text-blue-600">{{ question.type }}</span>
        <span v-if="question.difficulty" :class="['px-1.5 py-0.5 rounded', difficultyStyle]">{{ difficultyLabel }}</span>
        <span v-if="question.category" :class="['px-1.5 py-0.5 rounded', categoryStyle]">{{ question.category }}</span>
        <span v-if="question.grade" class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">{{ gradeLabel }}</span>
        <span v-for="topic in question.topics" :key="topic" class="px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-600">{{ topic }}</span>
      </div>

      <!-- 来源（底部小字） -->
      <div v-if="question.source" class="mt-1.5 text-[10px] text-slate-400">
        {{ question.source }}
      </div>
    </div>
  </div>
</template>