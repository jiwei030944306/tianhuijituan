<!-- 
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 试题自检与同步中心 (QuestionCheckNew.vue)
  本页面是系统的 P1 核心功能模块，负责对已上传的试题批次进行全方位检视。
  它整合了批次列表、题目筛选、数据统计及深度详情巡检功能，确保入库题目的质量。
-->

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：ref, computed, onMounted, watch (状态驱动视图)
 * - 路由跳转：useRouter (环境校验)
 * - 状态管理：useContextStore (业务上下文), useUserStore (用户信息)
 * - 业务组件：QuestionInspector (详情巡检), QuestionTable (数据表格), BatchList (批次列表), StatsCards (统计卡片)
 */
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useContextStore } from '@/stores/context';
import { useUserStore } from '@/stores/user';
import QuestionInspector from './QuestionCheckNew/QuestionInspector/index.vue';
import QuestionTable from './QuestionCheckNew/QuestionTable.vue';
import BatchList from '@/components/common/BatchList.vue';
import StatsCards from '@/components/common/StatsCards.vue';
import { Sparkles } from 'lucide-vue-next';
import { QuestionFilled } from '@element-plus/icons-vue';
import HelpGuide from '@/components/common/HelpGuide.vue';
import {
  DIFFICULTY_OPTIONS as RAW_DIFFICULTY_OPTIONS,
  QUESTION_TYPES,
  QUESTION_TYPE_TO_ENGLISH,
  QUESTION_TYPE_TO_CHINESE,
  ENGLISH_QUESTION_TYPES,
  getEnglishTypeName,
  getChineseTypeName,
  getTypesBySubjectEnglish,
  type Question,
  type Difficulty
} from '@/types/question';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 3. 核心代码强调：核心业务类型定义 ---
// 严格定义题型、难度及题目结构，确保全链路类型安全

// 题目类型（涵盖所有数据库题型值）
// 使用 Question 接口中的 type 定义

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

// --- 配置常量 ---
const PAGE_SIZE = 20;

// 题型颜色映射（支持所有学段、所有学科）
const TYPE_COLORS: Record<string, string> = {
  // ===== 通用题型（所有学科共有）=====
  '选择题': 'text-blue-700',
  '单选题': 'text-blue-700',
  'single_choice': 'text-blue-700',
  '多选题': 'text-orange-700',
  'multiple_choice': 'text-orange-700',
  '填空题': 'text-emerald-700',
  'fill_blank': 'text-emerald-700',
  'fill_in': 'text-emerald-700',
  '解答题': 'text-purple-700',
  'subjective': 'text-purple-700',
  '判断题': 'text-slate-700',
  'true_false': 'text-slate-700',

  // ===== 数学特有 =====
  '计算题': 'text-indigo-700',
  'calculation': 'text-indigo-700',

  // ===== 语文特有 =====
  '汉字书写': 'text-amber-600',
  '翻译': 'text-cyan-600',
  '基础知识': 'text-teal-600',
  '默写': 'text-lime-600',
  '语言运用': 'text-sky-600',
  '综合读写': 'text-violet-600',
  '名著阅读': 'text-fuchsia-600',
  '现代文阅读': 'text-rose-600',
  '古诗词赏析': 'text-red-600',
  '文言文阅读': 'text-stone-600',
  '作文': 'text-yellow-600',
  '综合性学习': 'text-neutral-600',

  // ===== 英语特有 =====
  '听力题': 'text-amber-500',
  '完形填空': 'text-cyan-500',
  '阅读理解': 'text-teal-500',
  '信息匹配': 'text-lime-500',
  '选词填空': 'text-sky-500',
  '短文填空': 'text-violet-500',
  '语法填空': 'text-fuchsia-500',
  '其他阅读题型': 'text-rose-500',
  '对话填空': 'text-red-500',
  '单词拼写': 'text-stone-500',
  '词性转换': 'text-yellow-500',
  '句型转换': 'text-neutral-500',
  '句子改错': 'text-orange-500',
  '完成句子': 'text-emerald-500',
  '翻译题': 'text-blue-500',
  '短文改错': 'text-purple-500',
  '书面表达': 'text-indigo-500',
  '词汇应用': 'text-pink-500',

  // ===== 物理特有 =====
  '选择说明题': 'text-amber-800',
  '作图题': 'text-cyan-800',
  'drawing': 'text-cyan-800',
  '简答题': 'text-teal-800',
  'short_answer': 'text-teal-800',
  '实验探究题': 'text-lime-800',
  '综合能力题': 'text-sky-800',
  '科普阅读题': 'text-violet-800',

  // ===== 化学特有 =====
  '选择填充题': 'text-amber-900',
  '实验题': 'text-cyan-900',
  'experiment': 'text-cyan-900',
  '推断题': 'text-teal-900',
  '工艺流程题': 'text-lime-900',
  '科学探究题': 'text-sky-900',
  '综合应用题': 'text-violet-900',

  // ===== 生物特有 =====
  '材料分析题': 'text-rose-700',

  // ===== 历史特有 =====
  '辨析题': 'text-amber-700',
  '材料题': 'text-cyan-700',
  '论述题': 'text-teal-700',

  // ===== 地理特有 =====
  '连线题': 'text-lime-700',

  // ===== 政治/道德与法治特有 =====
  '评析题': 'text-fuchsia-700',
  '阐述见解题': 'text-rose-700',
  '判断说理题': 'text-stone-700',
  '情境探究题': 'text-yellow-700',
  '分析说明题': 'text-neutral-700',
  '综合探究题': 'text-orange-700',
  '辨析评析题': 'text-emerald-700',
  '图表题': 'text-blue-600',
  '探究类试题': 'text-purple-600',

  // 默认
  'default': 'text-slate-500'
};

// 使用 question.ts 中定义的难度选项（英文值+中文显示）
const DIFFICULTY_OPTIONS = RAW_DIFFICULTY_OPTIONS;

// --- 辅助工具函数 ---
const getTypeConfig = (typeStr?: string) => {
  // 使用 question.ts 中的映射函数
  const label = getChineseTypeName(typeStr) || typeStr || '未知';
  return {
    value: typeStr || 'unknown',
    label: label,
    color: TYPE_COLORS[typeStr || ''] || TYPE_COLORS['default']
  };
};

const getDifficultyLabel = (diff?: string) => {
  return diff || '未知';
};

// --- 环境校验逻辑 ---
const router = useRouter();
const contextStore = useContextStore();
const userStore = useUserStore();

if (!contextStore.grade || !contextStore.subject) {
  router.push('/');
}

const currentSubject = contextStore.subject || 'math'; // default to math code if null
// 根据当前学段和学科获取题型列表
const currentLevel = contextStore.grade === 'senior' ? '高中' : '初中';
// 转换 subject code to chinese name for looking up types
const subjectNameMap: Record<string, string> = {
  'math': '数学', 'chinese': '语文', 'english': '英语', 'physics': '物理',
  'chemistry': '化学', 'biology': '生物', 'history': '历史',
  'geography': '地理', 'politics': '道德与法治', 'technology': '通用技术'
};
const currentSubjectName = subjectNameMap[currentSubject] || '数学';

// 动态生成当前学科的题型选项（使用英文值作为 value，中文作为 label）
const TYPE_OPTIONS = computed(() => {
  // 获取当前学科的英文题型列表
  const englishTypes = getTypesBySubjectEnglish(currentSubjectName, currentLevel);
  return englishTypes.map(enType => ({
    value: enType,  // 英文值用于数据匹配
    label: getChineseTypeName(enType) || enType,  // 中文用于显示
    color: TYPE_COLORS[enType] || TYPE_COLORS['default']
  }));
});

// --- 响应式状态管理 ---
const allFiles = ref<Batch[]>([]);
const selectedFile = ref<string | null>(null);
const visibleCount = ref(20);
const selectedQuestion = ref<Question | null>(null);
const displayQuestions = ref<Question[]>([]);
const showHelpGuide = ref(false);
const filters = ref<Filters>({
  keyword: '',
  type: 'ALL',
  difficulty: 'ALL'
});
const currentPage = ref(1);
const isLoading = ref(false);
const errorMsg = ref<string | null>(null);
const uploadsCollapsed = ref(false);

// --- 动态计算属性区 ---

// 批次列表计算
const visibleFiles = computed(() => allFiles.value);

// 3. 核心代码强调：实时数据统计 (Real-time Stats)
// 根据当前批次内的题目数据，自动生成各题型的分布统计
const fileStats = computed<FileStats | null>(() => {
  if (!displayQuestions.value.length) return null;
  // 简化的统计逻辑，主要统计几大类
  return {
    total: displayQuestions.value.length,
    single: displayQuestions.value.filter(q => q.type?.includes('选择') || q.type === 'single_choice').length,
    multi: displayQuestions.value.filter(q => q.type?.includes('多选') || q.type === 'multiple_choice').length,
    fill: displayQuestions.value.filter(q => q.type?.includes('填空') || q.type === 'fill_blank').length,
    calculation: displayQuestions.value.filter(q => q.type?.includes('计算')).length,
    application: displayQuestions.value.filter(q => q.type?.includes('应用')).length,
    subjective: displayQuestions.value.filter(q => q.type?.includes('解答') || q.type === 'subjective').length,
    errorCount: displayQuestions.value.filter(q => q.status === 'error').length
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

    // 新增筛选逻辑
    const matchStatus = !filters.value.status || q.status === filters.value.status;

    // AI 筛选逻辑修复：处理 undefined 情况
    // 待优化: isAiOptimized !== true
    // 已优化: isAiOptimized === true
    let matchAi = true;
    if (filters.value.isAiOptimized === true) {
      matchAi = q.isAiOptimized === true;
    } else if (filters.value.isAiOptimized === false) {
      matchAi = !q.isAiOptimized; // undefined or false -> match
    }

    return matchKeyword && matchType && matchDiff && matchStatus && matchAi;
  });

  const typePriority: Record<string, number> = {
    '选择题': 1, 'single_choice': 1,
    '多选题': 2, 'multiple_choice': 2,
    '填空题': 3, 'fill_in': 3,
    '解答题': 4, 'subjective': 4
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

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredTableData.value.length / PAGE_SIZE));
});

// 分页切片
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE;
  return filteredTableData.value.slice(start, start + PAGE_SIZE);
});

// --- 业务方法区 ---

// 更新题目数据（从Inspector同步）
const handleUpdateQuestion = (updatedQ: Question) => {
  // 更新列表中的数据
  const idx = displayQuestions.value.findIndex(q => q.id === updatedQ.id);
  if (idx !== -1) {
    displayQuestions.value[idx] = updatedQ;
  }
  // 更新选中题目
  if (selectedQuestion.value?.id === updatedQ.id) {
    selectedQuestion.value = updatedQ;
  }
};

// 获取上传批次历史
const fetchBatchList = async () => {
  isLoading.value = true;
  errorMsg.value = null;
  try {
    const folderCode = contextStore.folderCode;
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
    const response = await fetch(`/api/questions/batch/${batchId}`);
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
};

const handleLoadMore = () => {
  visibleCount.value += 20;
};

const resetFilters = () => {
  filters.value = {
    keyword: '',
    type: 'ALL',
    difficulty: 'ALL'
  };
};

// --- 状态监听区 ---
watch(selectedFile, (newFile) => {
  if (newFile) fetchBatchQuestions(newFile);
});

watch(filters, () => {
  currentPage.value = 1;
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

      <!-- 3. 核心代码强调：题目主列表，支持分页、即时筛选与详情唤起 -->
      <QuestionTable
        :questions="paginatedData"
        :selected-question-id="selectedQuestion?.id || null"
        :filters="filters"
        :type-options="TYPE_OPTIONS"
        :difficulty-options="DIFFICULTY_OPTIONS"
        :current-page="currentPage"
        :total-pages="totalPages"
        :total-items="filteredTableData.length"
        :page-size="PAGE_SIZE"
        :has-selected-file="!!selectedFile"
        @question-select="handleSelectQuestion"
        @update:filters="filters = $event"
        @clear-filters="resetFilters"
        @page-change="currentPage = $event"
      />
    </div>

    <!-- [Inspector Drawer] 右侧：详情深度检视器 -->
    <!-- 3. 核心代码强调：题目内容的完整检视（含解析、图片与原始数据） -->
    <QuestionInspector
      :question="selectedQuestion"
      :visible="!!selectedQuestion"
      @close="selectedQuestion = null"
      @update-question="handleUpdateQuestion"
    />

  </div>
</template>


<style scoped>
/* 主容器样式 - 已精简,组件样式在各自文件中 */
</style>