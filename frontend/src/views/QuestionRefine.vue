<!--
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 试题标化中心 (QuestionRefine.vue)
  本页面是系统的 P2 核心功能模块，负责对已入库的试题进行知识点打标、AI解析编写与人工审核。
  它整合了批次列表、题目筛选、数据统计及深度详情编辑功能，确保试题的标准化质量。
-->

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：ref, computed, onMounted, watch (状态驱动视图)
 * - 路由跳转：useRouter (环境校验)
 * - 状态管理：useContextStore (业务上下文), useUserStore (用户信息)
 * - 业务组件：BatchList (批次列表), StatsCards (统计卡片), QuestionTable (数据表格)
 */
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useContextStore } from '@/stores/context';
import { ElInput, ElSelect, ElOption, ElButton } from 'element-plus';
import { CATEGORY_OPTIONS } from '@/types/question';
import type { Question, QuestionStatus, Difficulty } from '@/types/question';
import BatchList from '@/components/common/BatchList.vue';
import StatsCards from '@/components/common/StatsCards.vue';
import QuestionCard from '@/components/common/QuestionCard.vue';
import QuestionEditor from './QuestionRefine/QuestionEditor.vue';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 本地类型定义 ---
// 批次接口
interface Batch {
  batch_id: string;
  display_name: string;
  timestamp: string;
  status: string;
  teacher_name: string;
  original_filename: string;
  file_count: number;
  image_count: number;
}

// 筛选条件接口
interface Filters {
  keyword: string;
  type: string;
  difficulty: string;
  category: string;
}

// 统计数据接口
interface FileStats {
  total: number;
  single: number;
  multi: number;
  fill: number;
  calculation: number;
  application: number;
  subjective: number;
  errorCount: number;
}

// --- 配置常量 ---
const PAGE_SIZE = 20;

// 题型选项（包含所有题型）
const TYPE_OPTIONS = [
  { value: 'single_choice', label: '单选', color: 'text-blue-700' },
  { value: 'multiple_choice', label: '多选', color: 'text-orange-700' },
  { value: 'fill_blank', label: '填空', color: 'text-emerald-700' },
  { value: 'fill_in', label: '填空', color: 'text-emerald-700' },
  { value: 'calculation', label: '计算', color: 'text-purple-700' },
  { value: 'application', label: '应用', color: 'text-pink-700' },
  { value: 'subjective', label: '解答', color: 'text-slate-700' }
];

// 难度选项
const DIFFICULTY_OPTIONS: Array<{ value: Difficulty; label: string }> = [
  { value: '易', label: '易' },
  { value: '较易', label: '较易' },
  { value: '中档', label: '中档' },
  { value: '较难', label: '较难' },
  { value: '难', label: '难' }
];

// 标准知识点（根据科目动态调整）
const STANDARD_KNOWLEDGE_POINTS = [
  '有理数', '整式加减', '一元一次方程', '几何图形初步',
  '相交线与平行线', '实数', '平面直角坐标系', '函数基础',
  '一次函数', '二次函数', '几何证明', '三角函数',
  '概率统计', '向量', '数列', '导数'
];

// AI 解析模板
const AI_ANALYSIS_TEMPLATE = (stem: string, knowledge: string) => {
  return `【AI 智能解析】\n本题主要考察 **${knowledge || '该知识点'}**。\n\n**解题步骤：**\n1. 根据题意 ${stem.substring(0, 20)}... 可知...\n2. 运用相关定理推导...\n\n**结论：**\n$$ \\therefore $$ 最终答案得出...`;
};

// --- 环境校验逻辑 ---
const router = useRouter();
const contextStore = useContextStore();

if (!contextStore.grade || !contextStore.subject) {
  router.push('/');
}

const folderCode = contextStore.folderCode || '';

// --- 响应式状态管理 ---
const allFiles = ref<Batch[]>([]);
const selectedFile = ref<string | null>(null);
const selectedQuestion = ref<Question | null>(null);
const displayQuestions = ref<Question[]>([]);
const filters = ref<Filters>({
  keyword: '',
  type: 'ALL',
  difficulty: 'ALL',
  category: 'ALL'
});
const isLoading = ref(false);
const errorMsg = ref<string | null>(null);
const uploadsCollapsed = ref(false);

// 编辑器状态
const editingQ = ref<Question | null>(null);
const isEditorOpen = ref(false);
const isSaving = ref(false);

// --- 动态计算属性区 ---

// 批次列表计算
const visibleFiles = computed(() => allFiles.value);

// 3. 核心代码强调：实时数据统计 (Real-time Stats)
// 根据当前批次内的题目数据，自动生成各题型的分布统计
const fileStats = computed<FileStats | null>(() => {
  if (!displayQuestions.value.length) return null;
  return {
    total: displayQuestions.value.length,
    single: displayQuestions.value.filter(q => q.type === 'single_choice').length,
    multi: displayQuestions.value.filter(q => q.type === 'multiple_choice').length,
    fill: displayQuestions.value.filter(q => q.type === 'fill_blank' || q.type === 'fill_in').length,
    calculation: displayQuestions.value.filter(q => q.type === 'calculation').length,
    application: displayQuestions.value.filter(q => q.type === 'application').length,
    subjective: displayQuestions.value.filter(q => q.type === 'subjective').length,
    errorCount: 0
  };
});

// 3. 核心代码强调：多维筛选与智能排序 (Filter & Sort)
// 支持关键词、题型、难度过滤，并优先按题号排序，其次按题型优先级排序
const filteredTableData = computed(() => {
  const result = displayQuestions.value.filter(q => {
    const lowerKey = filters.value.keyword.toLowerCase();
    const matchKeyword = !filters.value.keyword ||
                         q.id.toLowerCase().includes(lowerKey) ||
                         q.stem.toLowerCase().includes(lowerKey);

    const matchType = filters.value.type === 'ALL' || q.type === filters.value.type;
    const matchDiff = filters.value.difficulty === 'ALL' || q.difficulty === filters.value.difficulty;
    const matchCategory = filters.value.category === 'ALL' || q.category === filters.value.category;

    return matchKeyword && matchType && matchDiff && matchCategory;
  });

  const typePriority: Record<string, number> = {
    'single_choice': 1,
    'multiple_choice': 2,
    'fill_in': 3,
    'subjective': 4
  };

  return result.sort((a, b) => {
    if (a.questionNumber && b.questionNumber) {
      return a.questionNumber - b.questionNumber;
    }
    const pA = typePriority[a.type || ''] || 99;
    const pB = typePriority[b.type || ''] || 99;
    return pA - pB;
  });
});

// 3. 核心代码强调：题目状态分类
// 将题目按状态分为待标化和已完成两组（基于筛选后的数据）
// 待标化：active / error（兼容未知状态按待处理处理）
const todoQuestions = computed(() => {
  return filteredTableData.value.filter((q) => {
    if (!q.status) return true;
    return q.status === 'active' || q.status === 'error';
  });
});

// 已完成：confirmed / waste
const doneQuestions = computed(() => {
  return filteredTableData.value.filter((q) => q.status === 'confirmed' || q.status === 'waste');
});

// 建议知识点标签（结合已有知识点和标准知识点）
const suggestedTags = computed(() => {
  const counts: Record<string, number> = {};
  displayQuestions.value.forEach(q => {
    if (q.topics && q.topics[0]) {
      counts[q.topics[0]] = (counts[q.topics[0]] || 0) + 1;
    }
  });
  const topTags = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(e => e[0]);
  return [...new Set([...topTags, ...STANDARD_KNOWLEDGE_POINTS])].slice(0, 10);
});

// --- 业务方法区 ---

// 获取上传批次历史
const fetchBatchList = async () => {
  isLoading.value = true;
  errorMsg.value = null;
  try {
    if (!folderCode) {
      errorMsg.value = '环境信息不完整，请重新选择学科学段';
      return;
    }
    const response = await fetch(`/api/questions/upload-history?folder_code=${folderCode}`);
    if (!response.ok) throw new Error('获取批次列表失败');
    const data = await response.json();
    allFiles.value = data.records || [];
    if (allFiles.value.length > 0 && !selectedFile.value) {
      selectedFile.value = allFiles.value[0].batch_id;
    }
  } catch (error: any) {
    errorMsg.value = error.message || '获取批次列表失败';
  } finally {
    isLoading.value = false;
  }
};

// 3. 核心代码强调：批次详情加载 (Batch Detail Loader)
// 加载选中批次下的所有题目详情，并自动重置筛选器
const fetchBatchQuestions = async (batchId: string) => {
  selectedFile.value = batchId;
  isLoading.value = true;
  errorMsg.value = null;
  displayQuestions.value = [];
  try {
    if (!folderCode) {
      errorMsg.value = '环境信息不完整，请重新选择学科学段';
      return;
    }
    const response = await fetch(`/api/questions/batch/${batchId}?folder_code=${folderCode}`);
    if (!response.ok) throw new Error('获取题目失败');
    const data = await response.json();
    displayQuestions.value = data.questions || [];
    resetFilters();
  } catch (error: any) {
    errorMsg.value = error.message || '获取题目失败';
  } finally {
    isLoading.value = false;
  }
};

const handleSelectQuestion = (q: Question) => {
  selectedQuestion.value = q;
  // 打开编辑器
  editingQ.value = q;
  isEditorOpen.value = true;
};

// 3. 核心代码强调：编辑器保存逻辑
// 保存编辑后的题目，并自动跳转到下一题
const handleEditorSave = async (status: QuestionStatus, data: Partial<Question>) => {
  if (!editingQ.value) return;
  isSaving.value = true;
  try {
    const normalizedStatus: QuestionStatus =
      status === 'confirmed' || status === 'waste' || status === 'active' || status === 'error'
        ? status
        : 'active';

    // 构建更新后的题目
    const updatedQ: Question = {
      ...editingQ.value,
      ...data,
      status: normalizedStatus,
      confirmedAt: normalizedStatus === 'confirmed' ? (data.confirmedAt || new Date().toISOString()) : editingQ.value.confirmedAt
    };

    // 更新本地列表
    const index = displayQuestions.value.findIndex(q => q.id === editingQ.value!.id);
    if (index !== -1) {
      displayQuestions.value[index] = updatedQ;
    }

    // 如果是确认或废弃，自动跳转到下一题
    if (normalizedStatus === 'confirmed' || normalizedStatus === 'waste') {
      const currentIndex = displayQuestions.value.findIndex(q => q.id === editingQ.value!.id);
      let nextQ: Question | null = null;

      // 向前查找下一个待处理题目
      for (let i = currentIndex + 1; i < displayQuestions.value.length; i++) {
        const q = displayQuestions.value[i];
        if (!q.status || q.status === 'active' || q.status === 'error') {
          nextQ = q;
          break;
        }
      }

      if (nextQ) {
        editingQ.value = nextQ;
        selectedQuestion.value = nextQ;
      } else {
        // 没有下一题了，关闭编辑器
        closeEditor();
      }
    } else {
      closeEditor();
    }
  } catch (error) {
    console.error('保存失败:', error);
    errorMsg.value = '保存失败，请重试';
  } finally {
    isSaving.value = false;
  }
};

// 3. 核心代码强调：AI 自动生成解析
// 根据题干和知识点生成智能解析
const handleGenerateAI = () => {
  if (!editingQ.value) return;
  const snippet = editingQ.value.stem.substring(0, 20).replace(/[^\u4e00-\u9fa5]/g, "");
  const knowledge = editingQ.value.topics?.[0] || '';
  const generated = AI_ANALYSIS_TEMPLATE(snippet, knowledge);

  const target = editingQ.value;
  target.aiAnalysis = generated;
  target.aiReasoning = '基于题干结构与知识点进行步骤化推理（示例）';
  target.aiTopics = target.topics?.slice(0, 3) || [];
  target.aiDifficulty = target.difficulty || '中档';
  target.aiGrade = target.grade ? String(target.grade) : '';
  target.aiCategory = target.category;
  target.aiModel = target.aiModel || 'mock-ai-generator';
  target.aiOptimizedAt = new Date().toISOString();
  target.isAiOptimized = true;

  // 触发编辑器内部回调兼容
  console.log('AI 生成解析:', generated);
};

// 关闭编辑器
const closeEditor = () => {
  editingQ.value = null;
  isEditorOpen.value = false;
};

const resetFilters = () => {
  filters.value = {
    keyword: '',
    type: 'ALL',
    difficulty: 'ALL',
    category: 'ALL'
  };
};

// --- 状态监听区 ---
watch(selectedFile, (newFile) => {
  if (newFile) fetchBatchQuestions(newFile);
});

// --- 初始化挂载 ---
onMounted(() => {
  fetchBatchList();
});
</script>

<template>
  <div class="absolute top-16 left-0 right-0 bottom-0 flex overflow-hidden bg-white">

    <!-- ==========================================
         2. 主要功能代码分区注释 - 页面渲染区
         ========================================== -->

    <!-- [Batch Sidebar] 左侧：批次导航列表 -->
    <!-- 3. 核心代码强调：控制批次切换的核心入口，支持列表折叠 -->
    <div class="w-[10%] min-w-[120px] h-full">
      <BatchList
        :files="allFiles"
        :selected-file="selectedFile"
        :visible-files="visibleFiles"
        :uploads-collapsed="uploadsCollapsed"
        @file-select="fetchBatchQuestions"
        @toggle-collapse="uploadsCollapsed = !uploadsCollapsed"
      />
    </div>

    <!-- [Main Content] 中间：统计卡片与数据表格 -->
    <div class="flex-1 flex flex-col min-w-0 bg-white">

      <!-- 3. 核心代码强调：当前批次数据分布的可视化摘要 -->
      <StatsCards
        :file-stats="fileStats"
        :selected-file="selectedFile"
      />

<!-- 主内容区：标化工作台 -->
      <div class="flex-1 overflow-y-auto p-6 bg-slate-50/50">
        <!-- 筛选工具栏 -->
        <div v-if="selectedFile && displayQuestions.length > 0" class="mb-6 bg-white rounded-xl p-4 shadow-sm border border-slate-100">
          <div class="flex flex-wrap gap-4 items-center">
            <!-- 关键词搜索 -->
            <div class="flex-1 min-w-[200px]">
              <ElInput
                v-model="filters.keyword"
                placeholder="搜索题干或题目ID..."
                clearable
                prefix-icon="Search"
              />
            </div>

            <!-- 题型筛选 -->
            <div class="w-[140px]">
              <ElSelect
                v-model="filters.type"
                placeholder="题型"
                clearable
                class="w-full"
              >
                <ElOption label="全部" value="ALL" />
                <ElOption
                  v-for="opt in TYPE_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </ElSelect>
            </div>

            <!-- 难度筛选 -->
            <div class="w-[120px]">
              <ElSelect
                v-model="filters.difficulty"
                placeholder="难度"
                clearable
                class="w-full"
              >
                <ElOption label="全部" value="ALL" />
                <ElOption
                  v-for="opt in DIFFICULTY_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </ElSelect>
            </div>

            <!-- 题类筛选 -->
            <div class="w-[140px]">
              <ElSelect
                v-model="filters.category"
                placeholder="题类"
                clearable
                class="w-full"
              >
                <ElOption label="全部" value="ALL" />
                <ElOption
                  v-for="category in CATEGORY_OPTIONS"
                  :key="category"
                  :label="category"
                  :value="category"
                />
              </ElSelect>
            </div>

            <!-- 重置按钮 -->
            <ElButton
              v-if="filters.keyword || filters.type !== 'ALL' || filters.difficulty !== 'ALL' || filters.category !== 'ALL'"
              @click="resetFilters"
              type="default"
              size="default"
            >
              重置筛选
            </ElButton>

            <!-- 筛选结果统计 -->
            <div class="ml-auto text-sm text-slate-500">
              共 <span class="font-semibold text-slate-700">{{ filteredTableData.length }}</span> 道题目
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="flex items-center justify-center h-64 text-slate-400">
          <div class="text-center">
            <div class="w-12 h-12 mx-auto mb-4 rounded-xl bg-indigo-100 flex items-center justify-center animate-pulse">
              <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <p class="text-sm">加载批次数据中...</p>
          </div>
        </div>

        <!-- 未选择批次 -->
        <div v-else-if="!selectedFile" class="flex items-center justify-center h-64 text-slate-400 border-2 border-dashed border-slate-200 rounded-xl bg-slate-100 m-4">
          <div class="text-center">
            <svg class="w-12 h-12 mx-auto mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p class="text-sm">请在左侧选择一个任务批次</p>
          </div>
        </div>

        <!-- 批次无题目 -->
        <div v-else-if="displayQuestions.length === 0" class="flex items-center justify-center h-64 text-slate-400 border-2 border-dashed border-slate-200 rounded-xl bg-slate-100 m-4">
          <div class="text-center">
            <svg class="w-12 h-12 mx-auto mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-sm">该批次无待处理试题</p>
          </div>
        </div>

        <!-- 题目列表 -->
        <div v-else class="space-y-8">
          <!-- 待标化队列 -->
          <div v-if="todoQuestions.length > 0">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
              <h3 class="text-sm font-bold text-slate-700">待标化队列 ({{ todoQuestions.length }})</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
              <QuestionCard
                v-for="q in todoQuestions"
                :key="q.id"
                :question="q"
                :is-active="selectedQuestion?.id === q.id"
                @click="handleSelectQuestion(q)"
              />
            </div>
          </div>

          <!-- 已完成队列 -->
          <div v-if="doneQuestions.length > 0" class="opacity-70 hover:opacity-100 transition-opacity">
            <div class="flex items-center gap-2 mb-4">
              <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 class="text-sm font-bold text-slate-500">已完成 ({{ doneQuestions.length }})</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
              <QuestionCard
                v-for="q in doneQuestions"
                :key="q.id"
                :question="q"
                @click="handleSelectQuestion(q)"
              />
            </div>
          </div>
        </div>
</div>
      </div>

    <!-- ==========================================
         [Question Editor] 题目编辑器模态框
         ========================================== -->
    <QuestionEditor
      v-if="editingQ"
      :question="editingQ"
      :is-open="isEditorOpen"
      :suggested-tags="suggestedTags"
      @close="closeEditor"
      @save="handleEditorSave"
      @generate-ai="handleGenerateAI"
    />
  </div>
</template>


<style scoped>
/* 主容器样式 - 已精简,组件样式在各自文件中 */
</style>
