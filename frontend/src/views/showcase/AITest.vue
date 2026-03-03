<!--
  AI清洗测试工作台
  功能：
  1. 左侧：批次列表 (复用 BatchList)
  2. 中间：题目列表 (支持筛选：有效、待处理、多模态)
  3. 右侧：AI 检视器 (原题 vs AI优化结果)
-->

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useContextStore } from '@/stores/context';
import BatchList from '@/components/common/BatchList.vue';
import MathText from '@/components/common/MathText.vue';
import {
  optimizeQuestion,
  type AIOptimizeResult
} from '@/api/ai';
import {
  Loader2,
  Sparkles,
  AlertTriangle,
  Image as ImageIcon,
  CheckCircle2,
  XCircle,
  BrainCircuit,
  ArrowRight,
  Filter,
  Search,
  Code2,
  FileJson,
  Copy,
  Check
} from 'lucide-vue-next';
import { apiClient } from '@/api/base';

// ==================== 类型定义 ====================

interface Question {
  id: string;
  questionNumber: number;
  type: string;
  difficulty: string;
  stem: string;
  options: any[];
  answer: string;
  analysis: string;
  stemImages: any[];
  topics: string[];
  status?: string;
  isAiOptimized?: boolean;
  aiTempResult?: AIOptimizeResult; // 临时保存AI结果
  aiTempTime?: number;             // 临时保存耗时
  [key: string]: any;
}

interface Batch {
  batch_id: string;
  display_name: string;
  file_count: number;
}

interface FilterState {
  status: 'all' | 'valid' | 'error';
  optimization: 'all' | 'pending' | 'optimized';
  multimodal: 'all' | 'has_images' | 'text_only';
  search: string;
}

// ==================== 状态管理 ====================

const router = useRouter();
const contextStore = useContextStore();

// 复制状态
const copySuccess = ref<string | null>(null);

// 布局状态
const uploadsCollapsed = ref(false);

// 数据状态
const batches = ref<Batch[]>([]);
const selectedBatchId = ref<string | null>(null);
const questions = ref<Question[]>([]);
const selectedQuestionId = ref<string | null>(null);
const isLoadingBatches = ref(false);
const isLoadingQuestions = ref(false);

// AI 状态
const isOptimizing = ref(false);
const aiResult = ref<AIOptimizeResult | null>(null);
const mergedResult = ref<Question | null>(null); // 新增：合并后的完整试题
const optimizeError = ref<string | null>(null);
const optimizeTime = ref<number | null>(null);

// 筛选状态
const filters = ref<FilterState>({
  status: 'valid',     // 默认只看有效的
  optimization: 'all',
  multimodal: 'all',
  search: ''
});

// 调试模式状态
const showDebug = ref(false);

// ==================== 计算属性 ====================

// 当前选中的题目
const selectedQuestion = computed(() => {
  return questions.value.find(q => q.id === selectedQuestionId.value) || null;
});

// 筛选后的题目列表
const filteredQuestions = computed(() => {
  return questions.value.filter(q => {
    // 1. 状态筛选
    if (filters.value.status === 'valid' && q.status === 'error') return false;
    if (filters.value.status === 'error' && q.status !== 'error') return false;

    // 2. 优化状态筛选
    if (filters.value.optimization === 'pending' && q.isAiOptimized) return false;
    if (filters.value.optimization === 'optimized' && !q.isAiOptimized) return false;

    // 3. 多模态筛选
    const hasImages = (q.stemImages && q.stemImages.length > 0) ||
                      (q.options && q.options.some(o => o.image));
    if (filters.value.multimodal === 'has_images' && !hasImages) return false;
    if (filters.value.multimodal === 'text_only' && hasImages) return false;

    // 4. 搜索筛选
    if (filters.value.search) {
      const keyword = filters.value.search.toLowerCase();
      return q.stem.toLowerCase().includes(keyword) ||
             q.id.toLowerCase().includes(keyword);
    }

    return true;
  });
});

// 统计信息
const stats = computed(() => {
  return {
    total: questions.value.length,
    shown: filteredQuestions.value.length,
    valid: questions.value.filter(q => q.status !== 'error').length,
    error: questions.value.filter(q => q.status === 'error').length,
    optimized: questions.value.filter(q => q.isAiOptimized).length,
    hasImages: questions.value.filter(q => (q.stemImages?.length || 0) > 0).length
  };
});

// ==================== 方法 ====================

// 加载批次列表
  const fetchBatches = async () => {
  const folderCode = contextStore.folderCode;
  if (!folderCode) {
    // 如果没有环境上下文，跳转回首页或提示
    alert('请先选择学科学段');
    router.push('/');
    return;
  }

  isLoadingBatches.value = true;
  try {
    const response = await apiClient.get(`/api/questions/upload-history?folder_code=${folderCode}`);
    const data = response?.data;
    batches.value = data?.records || [];
    // 默认选中第一个
    if (batches.value.length > 0 && !selectedBatchId.value) {
      handleBatchSelect(batches.value[0].batch_id);
    }
  } catch (error: unknown) {
    console.error('获取批次失败:', error instanceof Error ? error.message : String(error));
  } finally {
};

// 加载批次题目
  const fetchQuestions = async (batchId: string) => {
  isLoadingQuestions.value = true;
  questions.value = [];
  selectedQuestionId.value = null;
  aiResult.value = null;
  optimizeError.value = null;
  optimizeTime.value = null;

    try {
      const folderCode = 'm7s9m2'; // 测试用 folder_code
      const response = await apiClient.get(`/api/questions/batch/${batchId}?folder_code=${folderCode}`);
      const data = response?.data;
      questions.value = data?.questions || [];
    } catch (error: unknown) {
      console.error('获取题目失败:', error instanceof Error ? error.message : String(error));
    } finally {
};

// 选择批次
const handleBatchSelect = (batchId: string) => {
  selectedBatchId.value = batchId;
  fetchQuestions(batchId);
};

// 选择题目
const handleQuestionSelect = (question: Question) => {
  selectedQuestionId.value = question.id;

  // 恢复之前保存的 AI 结果（如果有）
  if (question.aiTempResult) {
    aiResult.value = question.aiTempResult;
    optimizeTime.value = question.aiTempTime || null;

    // 重新构建合并结果（如果已有AI结果）
    buildMergedResult(question, question.aiTempResult);
  } else {
    aiResult.value = null;
    optimizeTime.value = null;
    mergedResult.value = null;
  }

  optimizeError.value = null;
};

// 构建合并后的结果（模拟入库）
const buildMergedResult = (question: Question, result: AIOptimizeResult) => {
  const now = new Date().toISOString();

  // 创建副本，删除废弃字段
  const cleanQuestion = { ...question };
  delete cleanQuestion.specialties; // 删除旧字段
  delete cleanQuestion.aiTempResult; // 删除临时字段
  delete cleanQuestion.aiTempTime; // 删除临时字段

  mergedResult.value = {
    ...cleanQuestion,

    // P1 系统字段补全
    sourceFolder: question.sourceFolder || '',
    createdAt: question.createdAt || now,
    updatedAt: now,
    version: question.version || 1,

    // P2-3 AI 字段回填
    aiGrade: result.grade,
    aiDifficulty: result.difficulty,
    aiTopics: result.topics,
    aiCategory: result.category,
    aiAnalysis: result.analysis,
    aiReasoning: result.reasoning,
    aiModel: 'gemini-3-pro-preview',
    aiOptimizedAt: now,
    isAiOptimized: true,

    // P2-4 人工确认字段（默认采用 AI 建议值）
    grade: result.grade ? (isNaN(Number(result.grade)) ? result.grade : Number(result.grade)) : undefined,
    difficulty: result.difficulty,
    topics: result.topics,
    category: result.category,
    comment: '',

    // 状态流转
    status: 'confirmed',
    confirmedAt: now
  };
};

// 执行 AI 优化
const handleOptimize = async () => {
  if (!selectedQuestion.value) return;

  isOptimizing.value = true;
  optimizeError.value = null;
  aiResult.value = null;
  mergedResult.value = null;

  const startTime = performance.now();

  try {
    const result = await optimizeQuestion(selectedQuestion.value);
    aiResult.value = result;
    optimizeTime.value = Math.round(performance.now() - startTime);

    // 构建合并结果
    if (selectedQuestion.value) {
      buildMergedResult(selectedQuestion.value, result);

      // 保存到当前题目对象中
      selectedQuestion.value.aiTempResult = result;
      selectedQuestion.value.aiTempTime = optimizeTime.value;
    }
  } catch (error: any) {
    optimizeError.value = error.message || '优化失败';
  } finally {
    isOptimizing.value = false;
  }
};

// 辅助：获取题目图片
const getQuestionImages = (q: Question) => {
  const images = [];
  if (q.stemImages) {
    images.push(...q.stemImages.map(img => ({ ...img, type: 'stem' })));
  }
  return images;
};

// 图片路径处理 (参考 api/ai.ts)
const getImageUrl = (path: string) => {
  if (!path) return '';
  if (path.startsWith('http') || path.startsWith('data:')) return path;
  // 开发环境默认指向后端端口
  return `http://localhost:8000/${path.startsWith('/') ? path.slice(1) : path}`;
};

// 复制到剪贴板
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

// 生命周期
onMounted(() => {
  fetchBatches();
});

</script>

<template>
  <div class="absolute inset-0 flex bg-slate-100 overflow-hidden">

    <!-- 左侧：批次列表 -->
    <div class="w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 transition-all duration-300" :class="{ 'w-16': uploadsCollapsed }">
      <BatchList
        :files="batches"
        :selected-file="selectedBatchId"
        :visible-files="batches"
        :uploads-collapsed="uploadsCollapsed"
        @file-select="handleBatchSelect"
        @toggle-collapse="uploadsCollapsed = !uploadsCollapsed"
      />
    </div>

    <!-- 中间：题目列表 -->
    <div class="w-96 flex flex-col bg-white border-r border-slate-200 shrink-0">
      <!-- 头部筛选区 -->
      <div class="p-4 border-b border-slate-200 bg-slate-50">
        <h2 class="text-sm font-bold text-slate-700 mb-3 flex items-center justify-between">
          <span>题目列表</span>
          <span class="text-xs font-normal text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full">{{ stats.shown }}/{{ stats.total }}</span>
        </h2>

        <!-- 搜索 -->
        <div class="relative mb-3">
          <Search :size="14" class="absolute left-2.5 top-2.5 text-slate-400" />
          <input
            v-model="filters.search"
            type="text"
            placeholder="搜索题干关键词..."
            class="w-full pl-8 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
          />
        </div>

        <!-- 筛选按钮组 -->
        <div class="space-y-2">
          <div class="flex gap-1">
            <button
              @click="filters.status = 'valid'"
              :class="['flex-1 py-1 text-[10px] rounded border transition-colors', filters.status === 'valid' ? 'bg-indigo-50 border-indigo-200 text-indigo-700 font-bold' : 'bg-white border-slate-200 text-slate-600']"
            >
              有效
            </button>
            <button
              @click="filters.status = 'error'"
              :class="['flex-1 py-1 text-[10px] rounded border transition-colors', filters.status === 'error' ? 'bg-red-50 border-red-200 text-red-700 font-bold' : 'bg-white border-slate-200 text-slate-600']"
            >
              异常 ({{ stats.error }})
            </button>
          </div>

          <div class="flex gap-1">
             <button
              @click="filters.multimodal = filters.multimodal === 'has_images' ? 'all' : 'has_images'"
              :class="['flex-1 py-1 text-[10px] rounded border transition-colors flex items-center justify-center gap-1', filters.multimodal === 'has_images' ? 'bg-amber-50 border-amber-200 text-amber-700 font-bold' : 'bg-white border-slate-200 text-slate-600']"
            >
              <ImageIcon :size="12" /> 含图片
            </button>
            <button
              @click="filters.optimization = filters.optimization === 'pending' ? 'all' : 'pending'"
              :class="['flex-1 py-1 text-[10px] rounded border transition-colors', filters.optimization === 'pending' ? 'bg-purple-50 border-purple-200 text-purple-700 font-bold' : 'bg-white border-slate-200 text-slate-600']"
            >
              待优化
            </button>
          </div>
        </div>
      </div>

      <!-- 列表内容 -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="isLoadingQuestions" class="h-full flex items-center justify-center text-slate-400">
          <Loader2 :size="24" class="animate-spin" />
        </div>
        <div v-else-if="filteredQuestions.length === 0" class="h-full flex items-center justify-center text-slate-400 text-xs">
          没有找到匹配的题目
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="q in filteredQuestions"
            :key="q.id"
            @click="handleQuestionSelect(q)"
            :class="[
              'p-3 cursor-pointer hover:bg-slate-50 transition-colors border-l-4',
              selectedQuestionId === q.id ? 'bg-indigo-50/50 border-l-indigo-500' : 'border-l-transparent'
            ]"
          >
            <div class="flex items-start justify-between mb-1">
              <span :class="[
                'text-[10px] px-1.5 py-0.5 rounded font-mono font-bold',
                q.status === 'error' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'
              ]">
                #{{ q.questionNumber }}
              </span>
              <div class="flex gap-1">
                <span v-if="q.stemImages?.length" class="text-[10px] text-amber-600 bg-amber-50 px-1 rounded flex items-center">
                  <ImageIcon :size="10" class="mr-0.5" />图
                </span>
                <span v-if="q.isAiOptimized" class="text-[10px] text-purple-600 bg-purple-50 px-1 rounded flex items-center">
                  <Sparkles :size="10" class="mr-0.5" />AI
                </span>
              </div>
            </div>

            <div class="text-xs text-slate-700 line-clamp-2 mb-1">
              {{ q.stem }}
            </div>

            <div class="flex items-center justify-between text-[10px] text-slate-400">
              <span>{{ q.type }}</span>
              <span>{{ q.difficulty }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：AI 检视工作台 -->
    <div class="flex-1 bg-slate-50 flex flex-col min-w-0">
      <div v-if="!selectedQuestion" class="h-full flex flex-col items-center justify-center text-slate-400">
        <BrainCircuit :size="48" class="mb-4 opacity-20" />
        <p>请从左侧选择一道题目开始测试</p>
      </div>

      <div v-else class="h-full flex flex-col">
        <!-- 顶部工具栏 -->
        <div class="h-14 border-b border-slate-200 bg-white px-6 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-3">
            <span class="text-lg font-bold text-slate-800">题目 #{{ selectedQuestion.questionNumber }}</span>
            <span class="px-2 py-0.5 bg-slate-100 text-slate-500 text-xs rounded">{{ selectedQuestion.type }}</span>
          </div>

          <div class="flex items-center gap-2">
            <!-- 调试开关 -->
            <button
              @click="showDebug = !showDebug"
              :class="[
                'p-2 rounded-lg transition-colors flex items-center gap-1.5 text-xs font-medium',
                showDebug ? 'bg-slate-200 text-slate-800' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
              ]"
              title="查看原始 JSON 数据"
            >
              <Code2 :size="16" />
              <span>调试信息</span>
            </button>

            <button
              @click="handleOptimize"
              :disabled="isOptimizing"
              class="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:shadow-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2 transition-all font-medium text-sm"
            >
              <Loader2 v-if="isOptimizing" :size="16" class="animate-spin" />
              <Sparkles v-else :size="16" />
              {{ isOptimizing ? 'AI 分析中...' : '开始 AI 优化' }}
            </button>
          </div>
        </div>

        <!-- 内容对比区 -->
        <div class="flex-1 flex overflow-hidden">

          <!-- 左半边：原始数据 -->
          <div class="flex-1 overflow-y-auto p-6 border-r border-slate-200 bg-white">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-slate-400"></span> 原始题目 (Original)
            </div>

            <!-- 题干 -->
            <div class="prose prose-sm max-w-none mb-6">
              <MathText :text="selectedQuestion.stem" />
            </div>

            <!-- 图片 -->
            <div v-if="getQuestionImages(selectedQuestion).length > 0" class="mb-6 grid grid-cols-2 gap-4">
              <div v-for="(img, idx) in getQuestionImages(selectedQuestion)" :key="idx" class="relative group border rounded-lg overflow-hidden bg-slate-50">
                <img :src="getImageUrl(img.src)" class="w-full h-32 object-contain" />
                <div class="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-[10px] px-2 py-1">
                  题干图片 {{ idx + 1 }}
                </div>
              </div>
            </div>

            <!-- 选项 -->
            <div class="space-y-2 mb-6">
              <div
                v-for="opt in selectedQuestion.options"
                :key="opt.key"
                class="flex items-start gap-3 p-3 rounded border border-slate-100 bg-slate-50"
              >
                <span class="font-bold text-slate-500">{{ opt.key }}.</span>
                <MathText :text="opt.content" class="text-sm text-slate-700" />
              </div>
            </div>

            <!-- 答案与解析 -->
            <div class="grid grid-cols-1 gap-4">
              <div class="p-3 bg-green-50 rounded border border-green-100">
                <span class="text-xs font-bold text-green-700 block mb-1">参考答案</span>
                <MathText :text="selectedQuestion.answer" class="text-sm font-medium" />
              </div>
              <div v-if="selectedQuestion.analysis" class="p-3 bg-slate-50 rounded border border-slate-100">
                <span class="text-xs font-bold text-slate-500 block mb-1">原始解析</span>
                <MathText :text="selectedQuestion.analysis" class="text-sm text-slate-600" />
              </div>
            </div>
          </div>

          <!-- 右半边：AI 结果 / 调试信息 -->
          <div class="flex-1 overflow-y-auto p-6 bg-slate-50/50">

            <!-- 调试视图 -->
            <div v-if="showDebug" class="h-full flex flex-col animate-fade-in">
              <div class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                <FileJson :size="14" /> 原始数据交互 (JSON Debug)
              </div>

              <div v-if="!aiResult?.debug && !mergedResult" class="flex-1 flex items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-lg">
                <p class="text-sm">暂无调试数据，请先执行 AI 优化</p>
              </div>

              <div v-else class="space-y-4 flex-1 overflow-y-auto">
                <!-- Request -->
                <div v-if="aiResult?.debug" class="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm">
                  <div class="px-3 py-2 bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-600 flex justify-between items-center">
                    <div class="flex items-center gap-2">
                      <span>Request Payload (Prompt)</span>
                      <span class="text-slate-400 font-normal">POST /v1/chat/completions</span>
                    </div>
                    <button
                      @click="copyToClipboard(JSON.stringify(aiResult.debug.prompt, null, 2), 'prompt')"
                      class="text-slate-400 hover:text-indigo-600 transition-colors"
                      title="复制请求内容"
                    >
                      <Check v-if="copySuccess === 'prompt'" :size="14" class="text-green-600" />
                      <Copy v-else :size="14" />
                    </button>
                  </div>
                  <pre class="p-3 text-[10px] leading-relaxed text-slate-600 bg-slate-50/50 overflow-x-auto font-mono max-h-60">{{ JSON.stringify(aiResult.debug.prompt, null, 2) }}</pre>
                </div>

                <!-- Response -->
                <div v-if="aiResult?.debug" class="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm">
                  <div class="px-3 py-2 bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-600 flex justify-between items-center">
                    <div class="flex items-center gap-2">
                      <span>Response Data (Raw)</span>
                      <span class="text-green-600 font-normal">200 OK</span>
                    </div>
                    <button
                      @click="copyToClipboard(JSON.stringify(aiResult.debug.rawResponse, null, 2), 'response')"
                      class="text-slate-400 hover:text-indigo-600 transition-colors"
                      title="复制响应内容"
                    >
                      <Check v-if="copySuccess === 'response'" :size="14" class="text-green-600" />
                      <Copy v-else :size="14" />
                    </button>
                  </div>
                  <pre class="p-3 text-[10px] leading-relaxed text-slate-600 bg-slate-50/50 overflow-x-auto font-mono max-h-96">{{ JSON.stringify(aiResult.debug.rawResponse, null, 2) }}</pre>
                </div>

                <!-- Merged Result Preview -->
                <div v-if="mergedResult" class="bg-white rounded-lg border-2 border-indigo-100 overflow-hidden shadow-sm">
                  <div class="px-3 py-2 bg-indigo-50 border-b border-indigo-100 text-xs font-bold text-indigo-800 flex justify-between items-center">
                    <div class="flex items-center gap-2">
                      <FileJson :size="14" class="text-indigo-600" />
                      <span>P2 Ingestion Preview (Merged JSON)</span>
                      <span class="bg-indigo-200 text-indigo-700 px-1.5 rounded text-[10px]">Ready for DB</span>
                    </div>
                    <button
                      @click="copyToClipboard(JSON.stringify(mergedResult, null, 2), 'merged')"
                      class="text-indigo-400 hover:text-indigo-700 transition-colors"
                      title="复制完整JSON"
                    >
                      <Check v-if="copySuccess === 'merged'" :size="14" class="text-green-600" />
                      <Copy v-else :size="14" />
                    </button>
                  </div>
                  <pre class="p-3 text-[10px] leading-relaxed text-slate-700 bg-indigo-50/20 overflow-x-auto font-mono max-h-[500px]">{{ JSON.stringify(mergedResult, null, 2) }}</pre>
                </div>
              </div>
            </div>

            <!-- 常规 AI 结果视图 -->
            <div v-else>
              <div class="text-xs font-bold text-indigo-500 uppercase tracking-wider mb-4 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" v-if="isOptimizing"></span>
                  <span class="w-2 h-2 rounded-full bg-indigo-500" v-else></span>
                  AI 优化建议 (Suggestion)
                </div>
                <span v-if="optimizeTime" class="text-slate-400 font-normal normal-case">耗时 {{ optimizeTime }}ms</span>
              </div>

              <!-- 空状态 / 错误 / 结果 -->
              <div v-if="optimizeError" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex items-start gap-2">
                <AlertTriangle :size="16" class="mt-0.5 shrink-0" />
                <div>
                  <div class="font-bold">优化失败</div>
                  <div>{{ optimizeError }}</div>
                </div>
              </div>

              <div v-else-if="!aiResult && !isOptimizing" class="h-64 flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-lg">
                <Sparkles :size="32" class="mb-2 opacity-20" />
                <p class="text-sm">点击上方按钮开始分析</p>
              </div>

              <div v-else-if="isOptimizing" class="space-y-4">
                <div class="h-24 bg-white rounded-lg animate-pulse"></div>
                <div class="h-32 bg-white rounded-lg animate-pulse"></div>
                <div class="h-40 bg-white rounded-lg animate-pulse"></div>
              </div>

              <div v-else-if="aiResult" class="space-y-6 animate-fade-in">
                <!-- 核心标签 -->
                <div class="grid grid-cols-2 gap-4">
                  <div class="bg-white p-4 rounded-lg shadow-sm border border-slate-100">
                    <span class="text-xs text-slate-400 block mb-1">建议年级</span>
                    <div class="text-lg font-bold text-indigo-600">{{ aiResult.grade || '未识别' }}</div>
                  </div>
                  <div class="bg-white p-4 rounded-lg shadow-sm border border-slate-100">
                    <span class="text-xs text-slate-400 block mb-1">建议难度</span>
                    <div class="text-lg font-bold text-indigo-600">{{ aiResult.difficulty || '未识别' }}</div>
                  </div>
                </div>

                <!-- 知识点 -->
                <div class="bg-white p-4 rounded-lg shadow-sm border border-slate-100">
                  <span class="text-xs text-slate-400 block mb-3">知识点标签</span>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="t in aiResult.topics"
                      :key="t"
                      class="px-2.5 py-1 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-md border border-indigo-100"
                    >
                      {{ t }}
                    </span>
                    <span v-if="!aiResult.topics?.length" class="text-slate-400 text-xs italic">未识别到知识点</span>
                  </div>
                </div>

                <!-- AI 解析 -->
                <div class="bg-white p-4 rounded-lg shadow-sm border border-slate-100 relative overflow-hidden">
                  <div class="absolute top-0 right-0 p-2 opacity-10">
                    <BrainCircuit :size="64" />
                  </div>
                  <span class="text-xs text-slate-400 block mb-2">AI 生成解析</span>
                  <div class="text-sm text-slate-700 leading-relaxed prose prose-sm max-w-none">
                    <MathText :text="aiResult.analysis || ''" />
                  </div>
                </div>

                <!-- 推理过程 (折叠) -->
                <div class="bg-slate-100 p-4 rounded-lg border border-slate-200">
                  <span class="text-xs font-bold text-slate-500 block mb-2">🤔 思考链 (Reasoning)</span>
                  <div class="text-xs text-slate-500 font-mono whitespace-pre-wrap leading-relaxed max-h-40 overflow-y-auto">
                    {{ aiResult.reasoning || '无推理过程记录' }}
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
