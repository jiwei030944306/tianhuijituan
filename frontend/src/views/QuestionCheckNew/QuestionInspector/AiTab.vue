<script setup lang="ts">
/**
 * AI 优化工作台组件
 *
 * 功能：
 * - 调用 AI 接口对题目进行智能分析
 * - 生成年级、难度、知识点、解析等建议
 * - 展示 AI 分析结果和推理过程
 * - 提供合并后 JSON 预览
 * - 支持确认入库操作（模拟）
 *
 * @component AiTab
 * @description QuestionInspector 的 AI 辅助优化标签页
 */

import { ref, watch } from 'vue';
import MathText from '@/components/common/MathText.vue';
import {
  optimizeQuestion,
  type AIOptimizeResult
} from '@/api/ai';
import {
  Loader2,
  Sparkles,
  AlertTriangle,
  BrainCircuit,
  FileJson,
  Check,
  Copy,
  Code2
} from 'lucide-vue-next';
import type { Question } from '@/types/question';

// ==================== Props 定义 ====================

const props = defineProps<{
  question: Question;
}>();

// ==================== Events 定义 ====================

const emit = defineEmits<{
  'update-question': [question: Question];
}>();

// ==================== 状态管理 ====================

const isOptimizing = ref<boolean>(false);           // AI 分析进行中状态
const aiResult = ref<AIOptimizeResult | null>(null); // AI 分析结果
const mergedResult = ref<Question | null>(null);    // 合并后的完整题目数据
const optimizeError = ref<string | null>(null);      // 优化错误信息
const optimizeTime = ref<number | null>(null);       // 优化耗时（毫秒）
const showDebug = ref<boolean>(false);               // 是否显示调试信息
const copySuccess = ref<string | null>(null);        // 复制成功提示

// ==================== 监听器 ====================

/**
 * 监听题目变化，重置状态或恢复已有 AI 数据
 */
watch(() => props.question, (newQ) => {
  // 重置状态
  isOptimizing.value = false;
  optimizeError.value = null;
  optimizeTime.value = null;

  // 如果题目已有 AI 数据，恢复显示
  if (newQ.isAiOptimized) {
    aiResult.value = {
      grade: newQ.aiGrade || '',
      difficulty: newQ.aiDifficulty || '',
      topics: newQ.aiTopics || [],
      category: newQ.aiCategory || '',
      analysis: newQ.aiAnalysis || '',
      reasoning: newQ.aiReasoning || ''
    };
    buildMergedResult(newQ, aiResult.value);
  } else {
    aiResult.value = null;
    mergedResult.value = null;
  }
}, { immediate: true });

// ==================== 方法 ====================

/**
 * 构建合并后的题目数据（模拟入库）
 * @param question - 原始题目数据
 * @param result - AI 分析结果
 */
const buildMergedResult = (question: Question, result: AIOptimizeResult) => {
  const now = new Date().toISOString();

  // 创建题目副本，避免修改原对象
  const cleanQuestion = { ...question };
  // @ts-ignore - 删除旧字段
  delete cleanQuestion.specialties;

  mergedResult.value = {
    ...cleanQuestion,

    // P1 系统字段补全（模拟）
    sourceFolder: question.sourceFolder || '',
    createdAt: question.createdAt || now,
    updatedAt: now,
    version: question.version || 1,

    // P2-3 AI 字段回填
    aiGrade: result.grade,
    // @ts-ignore
    aiDifficulty: result.difficulty,
    aiTopics: result.topics,
    // @ts-ignore
    aiCategory: result.category,
    aiAnalysis: result.analysis,
    aiReasoning: result.reasoning,
    aiModel: 'gemini-3-pro-preview',
    aiOptimizedAt: now,
    isAiOptimized: true,

    // P2-4 人工确认字段（默认采用 AI 建议值）
    // 尝试转换 grade 为 number，如果失败则保持 undefined
    grade: result.grade ? (isNaN(Number(result.grade)) ? undefined : Number(result.grade)) : undefined,
    // @ts-ignore
    difficulty: result.difficulty,
    topics: result.topics,
    // @ts-ignore
    category: result.category,
    comment: '',

    // 状态流转
    status: 'confirmed',
    confirmedAt: now
  };
};

/**
 * 调用 AI 接口进行题目优化分析
 */
const handleOptimize = async () => {
  isOptimizing.value = true;
  optimizeError.value = null;
  aiResult.value = null;
  mergedResult.value = null;

  const startTime = performance.now();

  try {
    // @ts-ignore - 类型兼容处理
    const result = await optimizeQuestion(props.question);
    aiResult.value = result;
    optimizeTime.value = Math.round(performance.now() - startTime);

    buildMergedResult(props.question, result);
  } catch (error: any) {
    optimizeError.value = error.message || '优化失败';
  } finally {
    isOptimizing.value = false;
  }
};

/**
 * 复制文本到剪贴板
 * @param text - 要复制的文本
 * @param type - 复制类型（用于显示提示）
 */
const copyToClipboard = async (text: string, type: 'prompt' | 'response' | 'merged') => {
  try {
    await navigator.clipboard.writeText(text);
    copySuccess.value = type;
    setTimeout(() => {
      copySuccess.value = null;
    }, 2000);
  } catch (err) {
    console.error('复制失败:', err);
  }
};

/**
 * 确认并保存（模拟入库操作）
 */
const handleConfirm = () => {
  if (mergedResult.value) {
    emit('update-question', mergedResult.value);
    alert('已模拟入库操作！(Console log updated question)');
    console.log('Confirmed Question:', mergedResult.value);
  }
};
</script>

<template>
  <div class="p-6 h-full flex flex-col">
    <!-- Header / Actions -->
    <div class="flex items-center justify-between mb-6 shrink-0">
      <div class="flex items-center gap-2">
        <div class="p-2 bg-indigo-50 rounded-lg text-indigo-600">
          <BrainCircuit :size="20" />
        </div>
        <div>
          <h3 class="font-bold text-slate-800">AI 智能优化</h3>
          <p class="text-xs text-slate-400">基于 Gemini-3 Pro 模型分析</p>
        </div>
      </div>

      <button
        @click="handleOptimize"
        :disabled="isOptimizing"
        class="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:shadow-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2 transition-all font-medium text-sm shadow-indigo-200"
      >
        <Loader2 v-if="isOptimizing" :size="16" class="animate-spin" />
        <Sparkles v-else :size="16" />
        {{ isOptimizing ? 'AI 分析中...' : (aiResult ? '重新分析' : '开始分析') }}
      </button>
    </div>

    <!-- Error State -->
    <div v-if="optimizeError" class="p-4 mb-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex items-start gap-2 shrink-0">
      <AlertTriangle :size="16" class="mt-0.5 shrink-0" />
      <div>
        <div class="font-bold">优化失败</div>
        <div>{{ optimizeError }}</div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!aiResult && !isOptimizing && !optimizeError" class="flex-1 flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-lg bg-slate-50/50">
      <Sparkles :size="48" class="mb-4 opacity-20" />
      <p class="text-sm font-medium">点击上方按钮开始 AI 分析</p>
      <p class="text-xs mt-2 opacity-60">将自动识别年级、难度、知识点并生成解析</p>
    </div>

    <!-- Loading State -->
    <div v-else-if="isOptimizing" class="flex-1 space-y-4 animate-pulse">
      <div class="h-24 bg-slate-100 rounded-lg"></div>
      <div class="h-32 bg-slate-100 rounded-lg"></div>
      <div class="h-40 bg-slate-100 rounded-lg"></div>
    </div>

    <!-- Result Content -->
    <div v-else-if="aiResult" class="flex-1 overflow-y-auto pr-2 space-y-6 animate-fade-in">

      <!-- Summary Cards -->
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
          <span class="text-xs text-slate-400 block mb-1">建议年级</span>
          <div class="text-lg font-bold text-indigo-600">{{ aiResult.grade || '未识别' }}</div>
        </div>
        <div class="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
          <span class="text-xs text-slate-400 block mb-1">建议难度</span>
          <div class="text-lg font-bold text-indigo-600">{{ aiResult.difficulty || '未识别' }}</div>
        </div>
        <div class="bg-white p-3 rounded-lg border border-slate-200 shadow-sm col-span-2">
          <span class="text-xs text-slate-400 block mb-1">知识点标签</span>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="t in aiResult.topics" :key="t" class="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-xs font-medium rounded border border-indigo-100">
              {{ t }}
            </span>
            <span v-if="!aiResult.topics?.length" class="text-slate-400 text-xs italic">无</span>
          </div>
        </div>
      </div>

      <!-- Analysis -->
      <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-sm relative overflow-hidden">
        <div class="absolute top-0 right-0 p-2 opacity-5">
          <BrainCircuit :size="64" />
        </div>
        <span class="text-xs font-bold text-slate-500 block mb-3 uppercase tracking-wider">AI 生成解析</span>
        <div class="text-sm text-slate-700 leading-relaxed prose prose-sm max-w-none">
          <MathText :text="aiResult.analysis || '未生成解析'" />
        </div>
      </div>

      <!-- Debug & Preview Toggle -->
      <div class="border-t border-slate-200 pt-4">
        <button
          @click="showDebug = !showDebug"
          class="flex items-center gap-2 text-xs text-slate-500 hover:text-slate-700 font-medium mb-3"
        >
          <Code2 :size="14" />
          {{ showDebug ? '隐藏调试信息' : '查看调试信息 & 入库预览' }}
        </button>

        <div v-if="showDebug" class="space-y-4 animate-fade-in">
           <!-- Merged Result Preview -->
           <div v-if="mergedResult" class="bg-slate-900 rounded-lg overflow-hidden shadow-sm">
              <div class="px-3 py-2 bg-slate-800 border-b border-slate-700 text-xs font-bold text-slate-300 flex justify-between items-center">
                <div class="flex items-center gap-2">
                  <FileJson :size="14" class="text-emerald-400" />
                  <span>P2 入库预览 (Merged JSON)</span>
                </div>
                <button
                  @click="copyToClipboard(JSON.stringify(mergedResult, null, 2), 'merged')"
                  class="text-slate-400 hover:text-white transition-colors"
                  title="复制"
                >
                  <Check v-if="copySuccess === 'merged'" :size="14" class="text-green-400" />
                  <Copy v-else :size="14" />
                </button>
              </div>
              <pre class="p-3 text-[10px] leading-relaxed text-emerald-50 font-mono overflow-x-auto max-h-[300px]">{{ JSON.stringify(mergedResult, null, 2) }}</pre>
            </div>

            <!-- Raw AI Debug -->
            <div v-if="aiResult.debug" class="bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
               <div class="px-3 py-2 border-b border-slate-200 text-xs font-bold text-slate-500">
                 Reasoning Chain
               </div>
               <div class="p-3 text-[10px] font-mono text-slate-600 whitespace-pre-wrap max-h-40 overflow-y-auto bg-white">
                 {{ aiResult.reasoning }}
               </div>
            </div>
        </div>
      </div>

      <!-- Action Footer -->
      <div class="sticky bottom-0 bg-white/90 backdrop-blur pt-4 pb-2 border-t border-slate-100 mt-auto">
        <button
          @click="handleConfirm"
          class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold rounded-lg shadow-sm shadow-emerald-200 transition-all flex items-center justify-center gap-2"
        >
          <Check :size="16" />
          确认入库 (模拟)
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>