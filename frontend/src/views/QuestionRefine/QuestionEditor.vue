<!--
  1. 页面简介 (Page Introduction)
  试题编辑器组件 (QuestionEditor.vue)
  本组件是标化中心的核心编辑界面，提供试题的深度编辑功能。
  包含左侧 A4 纸预览区和右侧属性编辑表单，支持知识点打标、难度调整、解析编写等功能。
-->

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：ref, computed, watch (响应式状态)
 * - 项目类型：Question, Option, StemImage (来自 @/types/question)
 * - 项目组件：MathText (LaTeX 公式渲染)
 * - 图标库：lucide-vue-next (Lucide 图标集)
 */
import { ref, computed, watch } from 'vue';
import type { Question, Option, StemImage } from '@/types/question';
import MathText from '@/components/common/MathText.vue';
import KnowledgePointSelector from '@/components/common/KnowledgePointSelector.vue';
import { getKnowledgeTree } from '@/config/knowledgePoints';
import {
  Tag,
  Save,
  Sparkles,
  GraduationCap,
  BarChart3,
  X,
  Layers,
  Hash,
  CheckCircle2,
  BookOpen,
  Info,
  FileText
} from 'lucide-vue-next';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- Props 定义 ---
interface QuestionEditorProps {
  question: Question;
  isOpen: boolean;
  suggestedTags?: string[];
}

interface QuestionEditorEmits {
  (e: 'close'): void;
  (e: 'save', status: string, data: Partial<Question>): void;
  (e: 'generate-ai'): void;
}

const props = withDefaults(defineProps<QuestionEditorProps>(), {
  suggestedTags: () => []
});

const emit = defineEmits<QuestionEditorEmits>();

// --- 配置常量 ---
const COMMON_TAGS = {
  juniorGrades: ['7', '8', '9'],
  seniorGrades: ['10', '11', '12'],
  difficulties: ['易', '较易', '中档', '较难', '难'],
  categories: ['常考题', '易错题', '好题', '压轴题', '优选题'],
  difficultiesLabel: {
    '易': '易',
    '较易': '较易',
    '中档': '中档',
    '较难': '较难',
    '难': '难'
  } as Record<string, string>
};

// --- 响应式状态管理 ---
const formState = ref({
  grade: '',
  difficulty: '',
  category: '',
  knowledgePoints: ['', '', ''] as string[],
  analysis: ''
});

const isSaving = ref(false);
const selectorOpen = ref(false);
const currentSelectorIndex = ref(0);

// 根据学段动态获取年级选项
const availableGrades = computed(() => {
  return props.question.educationLevel === '高中'
    ? COMMON_TAGS.seniorGrades
    : COMMON_TAGS.juniorGrades;
});

// 根据学科和学段获取知识点树
const knowledgeTree = computed(() => {
  return getKnowledgeTree(props.question.subject, props.question.educationLevel);
});

// --- 3. 核心代码强调：表单同步逻辑 ---
// 当编辑的题目变化时，同步更新表单状态
// 确保知识点始终为3个槽位
const ensureThreeKnowledgePoints = (topics?: string[]): string[] => {
  const result = ['', '', ''];
  if (topics) {
    for (let i = 0; i < Math.min(topics.length, 3); i++) {
      result[i] = topics[i] || '';
    }
  }
  return result;
};

watch(() => props.question, (newQ) => {
  if (newQ) {
    formState.value = {
      grade: newQ.grade ? String(newQ.grade) : '',
      difficulty: newQ.difficulty || '',
      category: newQ.category || '',
      knowledgePoints: ensureThreeKnowledgePoints(newQ.topics),
      analysis: newQ.analysis || ''
    };
  }
}, { immediate: true });

// --- 动态计算属性区 ---

// 判断是否为选择题
const isChoiceQuestion = computed(() => {
  return props.question.type === 'single_choice' || props.question.type === 'multiple_choice';
});

// --- 业务方法区 ---

// 打开知识点选择器
const handleOpenSelector = (index: number) => {
  currentSelectorIndex.value = index;
  selectorOpen.value = true;
};

// 确认知识点选择
const handleConfirmKnowledgePoint = (selected: string[]) => {
  if (selected.length > 0) {
    formState.value.knowledgePoints[currentSelectorIndex.value] = selected[0];
  } else {
    formState.value.knowledgePoints[currentSelectorIndex.value] = '';
  }
  selectorOpen.value = false;
};

// 关闭知识点选择器
const handleCloseSelector = () => {
  selectorOpen.value = false;
};

// 获取知识点按钮显示文本
const getKnowledgePointLabel = (index: number) => {
  const kp = formState.value.knowledgePoints[index];
  return kp || `知识点${index + 1}`;
};

// 保存（驳回）
const handleReject = async () => {
  if (isSaving.value) return;
  isSaving.value = true;
  try {
    const validKnowledgePoints = formState.value.knowledgePoints.filter(kp => kp);
    emit('save', 'active', {
      grade: formState.value.grade ? Number(formState.value.grade) : undefined,
      difficulty: formState.value.difficulty,
      category: formState.value.category || undefined,
      topics: validKnowledgePoints,
      analysis: formState.value.analysis
    });
  } finally {
    isSaving.value = false;
  }
};

// 保存并下一题
const handleSaveAndNext = async () => {
  if (isSaving.value) return;
  isSaving.value = true;
  try {
    const validKnowledgePoints = formState.value.knowledgePoints.filter(kp => kp);
    emit('save', 'confirmed', {
      grade: formState.value.grade ? Number(formState.value.grade) : undefined,
      difficulty: formState.value.difficulty,
      category: formState.value.category || undefined,
      topics: validKnowledgePoints,
      analysis: formState.value.analysis
    });
  } finally {
    isSaving.value = false;
  }
};

// AI 自动生成解析
const handleGenerateAI = () => {
  emit('generate-ai');
};

// 关闭编辑器
const handleClose = () => {
  emit('close');
};
</script>

<template>
  <!-- ==========================================
       2. 主要功能代码分区注释 - 页面渲染区
       ========================================== -->

  <!-- [Modal Overlay] 模态框遮罩层 -->
  <Transition name="modal">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 md:p-8"
      @click.self="handleClose"
    >
      <!-- [Modal Container] 模态框主容器 -->
      <div class="bg-white w-full max-w-[1400px] h-[90vh] rounded-2xl shadow-2xl flex overflow-hidden border border-slate-200 animate-scale-in">

<!-- ==========================================
             [LEFT PANEL] 左侧：A4 纸预览区
             ========================================== -->
        <div class="flex-1 bg-slate-200 flex flex-col items-center py-8 px-4 border-r border-slate-300 relative overflow-y-auto custom-scrollbar gap-6">

          <!-- [Fixed Card] 试题内容卡片 (固定在顶部) -->
          <div class="w-full max-w-[800px] bg-white shadow-lg p-8 rounded-sm shrink-0 z-10 relative">
            <!-- 装饰：A4纸顶部装订线 -->
            <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200"></div>

            <!-- 【试题内容】 -->
            <div>
              <div class="exam-paper-text">
                <span class="font-bold mr-2 select-none text-indigo-900">
                  {{ question.questionNumber ? `${question.questionNumber}.` : 'Q.' }}
                </span>
                <MathText :text="question.stem" />
              </div>

              <!-- 题干图片 -->
              <div
                v-if="question.stemImages && question.stemImages.length > 0"
                class="flex gap-4 mt-4 flex-wrap"
              >
                <div
                  v-for="(img, i) in question.stemImages"
                  :key="i"
                  class="max-w-[200px] border border-slate-200 p-1 bg-white inline-block rounded-sm shadow-sm"
                >
                  <img
                    :src="img.src"
                    alt="题干图片"
                    class="w-full h-auto object-contain"
                    @error="(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = 'https://placehold.co/200x150/e2e8f0/64748b?text=Image+' + (i + 1);
                    }"
                  />
                </div>
              </div>

              <!-- 选项列表 -->
              <div
                v-if="isChoiceQuestion && question.options && question.options.length > 0"
                class="grid grid-cols-2 gap-4 mt-6 exam-paper-text"
              >
                <div
                  v-for="opt in question.options"
                  :key="opt.key || opt.label"
                  class="flex gap-2 items-start group"
                >
                  <span class="font-bold shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-slate-50 text-slate-600 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors text-xs border border-slate-200">{{ opt.key || opt.label }}</span>
                  <div class="flex flex-col gap-2 w-full pt-0.5">
                    <MathText v-if="opt.content" :text="opt.content" />
                    <span v-else-if="opt.image" class="text-slate-400 text-[10px]">[图片选项]</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- [Answer Card] 答案和解析卡片 -->
          <div class="w-full max-w-[800px] bg-white shadow-lg p-8 rounded-sm shrink-0 z-10 relative">
            <!-- 装饰：A4纸顶部装订线 -->
            <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-200 via-emerald-100 to-emerald-200"></div>

            <!-- 【答案】 -->
            <div class="mb-6">
              <div class="flex items-center gap-2 mb-3">
                <CheckCircle2 :size="16" class="text-emerald-600" />
                <span class="font-bold text-emerald-800 text-sm">参考答案</span>
              </div>
              <div class="exam-paper-text pl-6">
                <MathText v-if="question.answer" :text="question.answer" />
                <span v-else class="text-slate-400 italic text-sm">暂无答案</span>
              </div>
            </div>

            <!-- 【解析】 -->
            <div>
              <div class="flex items-center gap-2 mb-3">
                <BookOpen :size="16" class="text-indigo-600" />
                <span class="font-bold text-indigo-800 text-sm">题目解析</span>
              </div>
              <div class="exam-paper-text pl-6">
                <MathText v-if="question.analysis" :text="question.analysis" />
                <span v-else class="text-slate-400 italic text-sm">暂无解析</span>
              </div>
            </div>
          </div>

        </div>

<!-- ==========================================
             [RIGHT PANEL] 右侧：属性编辑表单区
             ========================================== -->
        <div class="w-[420px] bg-white flex flex-col overflow-hidden">
          <!-- [Header] 顶部标题栏 -->
          <div class="p-5 border-b border-slate-200 bg-gradient-to-r from-indigo-50 to-white">
            <h3 class="font-bold text-slate-800 flex items-center gap-2">
              <Tag :size="18" class="text-indigo-600" />
              试题属性编辑
            </h3>
            <p class="text-xs text-slate-500 mt-1">完善试题的年级、难度、知识点和解析信息</p>
          </div>

          <!-- [Form Content] 表单内容区（可滚动） -->
          <div class="flex-1 overflow-y-auto custom-scrollbar p-5 space-y-6">

            <!-- 【年级选择】 -->
            <div>
              <label class="exam-label">
                <GraduationCap :size="14" class="text-indigo-500" />
                适用年级
              </label>
              <div class="grid grid-cols-3 gap-2">
                <button
                  v-for="grade in availableGrades"
                  :key="grade"
                  @click="formState.grade = grade"
                  :class="[
                    'py-2 px-3 rounded-lg text-xs font-medium transition-all',
                    formState.grade === grade
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  ]"
                >
                  {{ grade }}
                </button>
              </div>
            </div>

            <!-- 【难度选择】 -->
            <div>
              <label class="exam-label">
                <BarChart3 :size="14" class="text-indigo-500" />
                难度等级
              </label>
              <div class="grid grid-cols-4 gap-2">
                <button
                  v-for="diff in COMMON_TAGS.difficulties"
                  :key="diff"
                  @click="formState.difficulty = diff"
                  :class="[
                    'py-2 px-2 rounded-lg text-xs font-medium transition-all',
                    formState.difficulty === diff
                      ? `bg-indigo-600 text-white shadow-md shadow-indigo-200`
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  ]"
                >
                  {{ COMMON_TAGS.difficultiesLabel[diff] }}
                </button>
              </div>
            </div>

            <!-- 【题类选择】 -->
            <div>
              <label class="exam-label">
                <Tag :size="14" class="text-indigo-500" />
                题类标签
              </label>
              <div class="grid grid-cols-3 gap-2">
                <button
                  v-for="cat in COMMON_TAGS.categories"
                  :key="cat"
                  @click="formState.category = cat"
                  :class="[
                    'py-2 px-2 rounded-lg text-xs font-medium transition-all',
                    formState.category === cat
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  ]"
                >
                  {{ cat }}
                </button>
              </div>
            </div>

            <!-- 【知识点选择】 -->
            <div>
              <label class="exam-label">
                <Layers :size="14" class="text-indigo-500" />
                知识点标签
              </label>
              <div class="space-y-2">
                <div
                  v-for="(_, index) in formState.knowledgePoints"
                  :key="index"
                  class="flex items-center gap-2"
                >
                  <!-- 编号标识 -->
                  <span class="shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold flex items-center justify-center">
                    {{ index + 1 }}
                  </span>
                  <!-- 知识点按钮 -->
                  <button
                    @click="handleOpenSelector(index)"
                    class="flex-1 py-2.5 px-4 rounded-lg border-2 border-dashed border-slate-200 text-left text-sm hover:border-indigo-400 hover:bg-indigo-50/50 transition-all flex items-center justify-between group"
                  >
                    <span :class="formState.knowledgePoints[index] ? 'text-slate-700 font-medium' : 'text-slate-400'">
                      {{ formState.knowledgePoints[index] || '未选择' }}
                    </span>
                    <Hash :size="14" :class="formState.knowledgePoints[index] ? 'text-indigo-500' : 'text-slate-300 group-hover:text-indigo-400'" />
                  </button>
                </div>
              </div>
              <p class="text-[10px] text-slate-400 mt-2">点击选择对应的知识点，支持多层级分类</p>
            </div>

            <!-- 【解析编辑】 -->
            <div>
              <label class="exam-label">
                <FileText :size="14" class="text-indigo-500" />
                试题解析
              </label>
              <textarea
                v-model="formState.analysis"
                placeholder="请输入试题的详细解析..."
                class="w-full h-32 p-3 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none outline-none transition-all"
              ></textarea>
              <button
                @click="handleGenerateAI"
                class="mt-2 w-full py-2 px-4 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg text-xs font-medium hover:from-indigo-600 hover:to-purple-600 transition-all flex items-center justify-center gap-2 shadow-md shadow-indigo-200"
              >
                <Sparkles :size="14" />
                AI 自动生成解析
              </button>
            </div>

            <!-- 【信息提示】 -->
            <div class="bg-slate-50 rounded-lg p-3 border border-slate-200">
              <div class="flex items-start gap-2">
                <Info :size="14" class="text-indigo-500 shrink-0 mt-0.5" />
                <div class="text-xs text-slate-500 space-y-1">
                  <p>• 完善属性信息有助于后续的题目检索和统计分析</p>
                  <p>• 知识点标签建议选择最精确的层级</p>
                  <p>• 解析内容将展示给学生作为学习参考</p>
                </div>
              </div>
            </div>

          </div>

          <!-- [Footer Actions] 底部操作区 -->
          <div class="p-5 border-t border-slate-200 bg-slate-50/50 space-y-3">
            <button
              @click="handleSaveAndNext"
              :disabled="isSaving"
              class="w-full py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 shadow-lg shadow-indigo-200 font-bold text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CheckCircle2 :size="18" />
              {{ isSaving ? '保存中...' : '确认入库并下一题' }}
            </button>
            <button
              @click="handleReject"
              :disabled="isSaving"
              class="w-full py-2.5 border border-slate-200 text-slate-600 bg-white rounded-xl hover:bg-slate-50 font-medium text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              保留待处理
            </button>
          </div>

        </div>

      </div>
    </div>
  </Transition>

  <KnowledgePointSelector
    :is-open="selectorOpen"
    :selected="formState.knowledgePoints[currentSelectorIndex] ? [formState.knowledgePoints[currentSelectorIndex]] : []"
    :knowledge-tree="knowledgeTree"
    @close="handleCloseSelector"
    @confirm="handleConfirmKnowledgePoint"
  />
</template>

<style scoped>
/* A4 纸样式 */
.exam-paper-container {
  background: white;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.exam-label {
  @apply flex items-center gap-2 text-xs font-bold text-slate-500 mb-3 pb-1 border-b border-slate-100;
}

.exam-paper-text {
  @apply text-sm text-slate-800 leading-7 font-serif;
}

/* 自定义滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(148, 163, 184, 0.5);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(100, 116, 139, 0.8);
}
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scale-in {
  animation: scale-in 0.3s ease-out;
}
</style>