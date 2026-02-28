<script setup lang="ts">
import { Search, MoreHorizontal, Image as ImageIcon, AlertTriangle, Sparkles } from 'lucide-vue-next';
import QuestionFilters from './QuestionFilters.vue';
import QuestionPagination from './QuestionPagination.vue';
import type { Question, QuestionFilters as Filters } from '@/types/question'; // 使用共享类型

// ==================== Props 定义 ====================

interface SelectOption {
  value: string;
  label: string;
  color?: string;
}

interface Props {
  questions: Question[];              // 题目列表(已筛选已分页)
  selectedQuestionId: string | null;  // 选中的题目ID
  filters: any;                       // 筛选条件 (本地 Filters 接口可能与全局略有不同，暂用 any 或保持兼容)
  typeOptions: SelectOption[];        // 题型选项
  difficultyOptions: SelectOption[];  // 难度选项
  currentPage: number;                // 当前页码
  totalPages: number;                 // 总页数
  totalItems: number;                 // 总条数
  pageSize: number;                   // 每页条数
  hasSelectedFile: boolean;           // 是否已选择批次
}

const props = defineProps<Props>();

// ==================== Events 定义 ====================

const emit = defineEmits<{
  'question-select': [question: Question];  // 选择题目
  'update:filters': [filters: any];          // 更新筛选条件
  'clear-filters': [];                        // 清空筛选
  'page-change': [page: number];              // 页码变更
}>();

// ==================== 方法 ====================

// 英文题型到中文的映射（与父组件保持一致）
const TYPE_NAME_MAP: Record<string, string> = {
  'single_choice': '选择题',
  'multiple_choice': '多选题',
  'fill_blank': '填空题',
  'subjective': '解答题',
  'calculation': '计算题',
  'application': '应用题',
  'drawing': '作图题',
  'experiment': '实验题',
  'short_answer': '简答题',
  'true_false': '判断题'
};

// 题型颜色映射
const TYPE_COLORS: Record<string, string> = {
  '选择题': 'text-blue-700',
  '多选题': 'text-orange-700',
  '填空题': 'text-emerald-700',
  '解答题': 'text-purple-700',
  '判断题': 'text-slate-700',
  '计算题': 'text-indigo-700',
  '应用题': 'text-pink-700',
  '作图题': 'text-cyan-700',
  '实验题': 'text-amber-700',
  '简答题': 'text-lime-700',
  'single_choice': 'text-blue-700',
  'multiple_choice': 'text-orange-700',
  'fill_blank': 'text-emerald-700',
  'fill_in': 'text-emerald-700',
  'subjective': 'text-purple-700',
  'calculation': 'text-indigo-700',
  'application': 'text-pink-700',
  'drawing': 'text-cyan-700',
  'experiment': 'text-amber-700',
  'short_answer': 'text-lime-700',
  'true_false': 'text-slate-700'
};

// 获取题型配置
const getTypeConfig = (typeStr: string) => {
  // 先从 typeOptions 查找（优先使用父组件的配置）
  const found = props.typeOptions.find(t => t.value === typeStr);
  if (found) {
    return found;
  }
  // 如果找不到，使用映射逻辑
  const label = TYPE_NAME_MAP[typeStr] || typeStr || '未知';
  const color = TYPE_COLORS[typeStr] || 'text-slate-500';
  return { label, color };
};

// 选择题目
const selectQuestion = (q: Question) => {
  emit('question-select', q);
};

// 重置筛选
const handleClearFilters = () => {
  emit('clear-filters');
};
</script>

<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-slate-50">
    <!-- 筛选器卡片 -->
    <QuestionFilters
      :filters="filters"
      :type-options="typeOptions"
      :difficulty-options="difficultyOptions"
      @update:filters="emit('update:filters', $event)"
      @clear-filters="handleClearFilters"
    />

    <!-- 表格卡片 -->
    <div class="flex-1 overflow-auto px-4 pb-4">
      <div class="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden h-full flex flex-col">
        <!-- 未选择批次 -->
        <div v-if="!hasSelectedFile" class="flex-1 flex flex-col items-center justify-center text-slate-400">
          <Search :size="32" class="opacity-30 mb-2"/>
          <p class="text-xs">请选择左侧批次以查看数据</p>
        </div>

        <!-- 无匹配记录 -->
        <div v-else-if="questions.length === 0" class="flex-1 flex flex-col items-center justify-center text-slate-400">
          <Search :size="32" class="mb-2 opacity-30"/>
          <p class="text-xs">未找到匹配记录</p>
          <button @click="handleClearFilters" class="mt-2 text-xs text-indigo-600 hover:underline">清空筛选</button>
        </div>

        <!-- 数据表格 -->
        <div v-else class="flex-1 overflow-auto">
          <table class="w-full text-left border-collapse table-fixed">
            <thead class="bg-slate-50 sticky top-0 z-10 shadow-sm text-xs font-bold text-slate-600 uppercase">
              <tr>
                <th class="px-3 py-2 w-14 border-r border-b border-slate-200 text-center">No.</th>
                <th class="px-3 py-2 w-20 border-r border-b border-slate-200 text-center">题型</th>
                <th class="px-3 py-2 w-16 border-r border-b border-slate-200 text-center">AI</th>
                <th class="px-3 py-2 w-[22%] border-r border-b border-slate-200">题干 <span class="text-[10px] font-normal text-slate-400 normal-case">(Stem)</span></th>
                <th class="px-3 py-2 w-[38%] border-r border-b border-slate-200">选项 <span class="text-[10px] font-normal text-slate-400 normal-case">(Options)</span></th>
                <th class="px-3 py-2 w-36 border-r border-b border-slate-200 text-center">答案 <span class="text-[10px] font-normal text-slate-400 normal-case">(Ans)</span></th>
                <th class="px-2 py-2 w-10 border-b border-slate-200"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-xs">
              <tr
                v-for="(q, idx) in questions"
                :key="q.id"
                @click="selectQuestion(q)"
                :class="[
                  'group h-10 cursor-pointer transition-colors',
                  // 错误状态：红色背景
                  q.status === 'error' ? 'bg-red-50 hover:bg-red-100 text-red-900' :
                  // 选中状态：蓝色背景
                  selectedQuestionId === q.id ? 'bg-blue-50 text-blue-900' :
                  // 默认状态
                  'hover:bg-blue-50/50 text-slate-600'
                ]"
              >
                <!-- 题号 -->
                <td class="px-2 py-2 text-center border-r border-slate-100 font-mono text-[10px] truncate">
                  <div class="flex items-center justify-center gap-1">
                    <AlertTriangle v-if="q.status === 'error'" :size="12" class="text-red-500" />
                    <span :class="q.status === 'error' ? 'text-red-500' : 'text-slate-400'">
                      {{ q.questionNumber || idx + 1 }}
                    </span>
                  </div>
                </td>

                <!-- 题型 -->
                <td :class="['px-2 py-2 text-center border-r border-slate-100 font-bold', getTypeConfig(q.type).color]">
                  {{ getTypeConfig(q.type).label }}
                </td>

                <!-- AI优化状态 -->
                <td class="px-2 py-2 text-center border-r border-slate-100">
                  <div
                    v-if="q.isAiOptimized"
                    class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-700"
                    title="已AI优化"
                  >
                    <Sparkles :size="10" />
                    <span class="text-[10px] font-bold">是</span>
                  </div>
                  <span v-else class="text-[10px] text-slate-300">否</span>
                </td>

                <!-- 题干 -->
                <td class="px-3 py-2 border-r border-slate-100">
                  <div class="flex items-center gap-2 h-full overflow-hidden">
                    <span
                      v-if="q.stemImages && q.stemImages.length > 0"
                      class="text-[10px] bg-slate-100 px-1 rounded border border-slate-200 shrink-0 flex items-center gap-0.5"
                    >
                      <ImageIcon :size="10"/> 图
                    </span>
                    <div class="truncate font-medium w-full" :title="q.stem">{{ q.stem }}</div>
                  </div>
                </td>

                <!-- 选项 -->
                <td class="px-3 py-2 border-r border-slate-100">
                  <div v-if="q.options && q.options.length > 0" class="flex items-center gap-3 h-full overflow-hidden">
                    <div
                      v-for="opt in q.options"
                      :key="opt.key || opt.label"
                      class="flex items-center gap-1 shrink-0 max-w-[200px]"
                    >
                      <span
                        :class="[
                          'font-mono font-bold text-[10px] px-1 rounded border',
                          opt.key === q.answer || (q.answer && q.answer.includes(opt.key || opt.label || ''))
                            ? 'bg-green-100 border-green-300 text-green-700'
                            : 'bg-white border-slate-200 text-slate-400'
                        ]"
                      >
                        {{ opt.key || opt.label }}
                      </span>
                      <span
                        :class="[
                          'truncate',
                          opt.key === q.answer ? 'text-green-700' : 'text-slate-500'
                        ]"
                        :title="opt.content"
                      >
                        {{ opt.content }}
                      </span>
                    </div>
                  </div>
                  <span v-else class="text-slate-300 italic">-</span>
                </td>

                <!-- 答案 -->
                <td class="px-3 py-2 text-center border-r border-slate-100 bg-slate-50/30">
                  <div class="w-full truncate font-mono font-bold text-slate-800" :title="q.answer">
                    {{ q.answer || '?' }}
                  </div>
                </td>

                <!-- 更多操作 -->
                <td class="px-2 py-2 text-center">
                  <MoreHorizontal :size="14" class="text-slate-300 mx-auto group-hover:text-indigo-500"/>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 分页器 -->
    <QuestionPagination
      v-if="hasSelectedFile && questions.length > 0"
      :current-page="currentPage"
      :total-pages="totalPages"
      :total-items="totalItems"
      :page-size="pageSize"
      @page-change="emit('page-change', $event)"
    />
  </div>
</template>

<style scoped>
/* 表格样式 */
</style>
