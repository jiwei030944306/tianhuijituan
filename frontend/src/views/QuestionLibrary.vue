<!--
  智研题库协作云 - 题库管理 (QuestionLibrary.vue)
  带层级结构的知识点筛选侧边栏
-->

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useContextStore } from '@/stores/context';
import { getKnowledgeTree } from '@/config/knowledgePoints';
import { questionApi } from '@/api/question';
import type { KnowledgeNode } from '@/components/common/KnowledgePointSelector.vue';
import type { Question } from '@/types/question';
import KnowledgeTreeSidebar from './QuestionLibrary/KnowledgeTreeSidebar.vue';

// --- 环境校验逻辑 ---
const router = useRouter();
const contextStore = useContextStore();

if (!contextStore.grade || !contextStore.subject) {
  router.push('/');
}

const currentSubject = contextStore.subject || '数学';
const currentGrade = contextStore.grade || '七年级';

// --- 知识点树 ---
const knowledgeTree = ref<KnowledgeNode[]>([]);
const expandedGroups = ref<Set<string>>(new Set());
const expandedSubGroups = ref<Set<string>>(new Set());

// --- 响应式状态管理 ---
const isLoading = ref(false);
const errorMsg = ref<string | null>(null);
const questions = ref<Question[]>([]);
const selectedTopics = ref<string[]>([]);
const searchKeyword = ref('');
const currentPage = ref(1);
const pageSize = ref(20);

// --- 知识点统计 ---
const knowledgeStats = computed(() => {
  const stats: Record<string, number> = {};
  
  questions.value.forEach(q => {
    if (q.topic) {
      stats[q.topic] = (stats[q.topic] || 0) + 1;
    }
  });
  
  return stats;
});

// --- 筛选后的题目列表 ---
const filteredQuestions = computed(() => {
  let result = questions.value;
  
  // 按知识点筛选
  if (selectedTopics.value.length > 0) {
    result = result.filter(q => 
      q.topic && selectedTopics.value.includes(q.topic)
    );
  }
  
  // 按关键词搜索
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(q => 
      (q.content && q.content.toLowerCase().includes(keyword)) ||
      (q.topic && q.topic.toLowerCase().includes(keyword))
    );
  }
  
  return result;
});

// --- 分页后的题目列表 ---
const paginatedQuestions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredQuestions.value.slice(start, end);
});

const totalPages = computed(() => 
  Math.ceil(filteredQuestions.value.length / pageSize.value)
);

// --- 获取题目列表 ---
const fetchQuestions = async () => {
  isLoading.value = true;
  errorMsg.value = null;
  
  try {
    // 将中文年级转换为数字（七年级 -> 7）
    const gradeNumber = parseInt(currentGrade.replace(/[^\d]/g, '')) || 7;
    
    const data = await questionApi.getList({
      subject: currentSubject,
      grade: gradeNumber
    });
    questions.value = data;
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '获取题目失败';
    console.error('获取题目失败:', err);
  } finally {
    isLoading.value = false;
  }
};

// --- 处理侧边栏事件 ---
const handleToggleTopic = (topicName: string) => {
  const index = selectedTopics.value.indexOf(topicName);
  if (index > -1) {
    selectedTopics.value.splice(index, 1);
  } else {
    selectedTopics.value.push(topicName);
  }
  currentPage.value = 1; // 重置页码
};

const handleToggleGroup = (groupId: string) => {
  if (expandedGroups.value.has(groupId)) {
    expandedGroups.value.delete(groupId);
  } else {
    expandedGroups.value.add(groupId);
  }
};

const handleToggleSubGroup = (groupId: string, subGroupId: string) => {
  const key = `${groupId}-${subGroupId}`;
  if (expandedSubGroups.value.has(key)) {
    expandedSubGroups.value.delete(key);
  } else {
    expandedSubGroups.value.add(key);
  }
};

const clearTopicFilter = () => {
  selectedTopics.value = [];
  currentPage.value = 1;
};

// --- 初始化挂载 ---
onMounted(() => {
  // 加载知识点树
  knowledgeTree.value = getKnowledgeTree(currentSubject);
  
  // 默认展开所有主分类和子分类
  knowledgeTree.value.forEach(group => {
    expandedGroups.value.add(group.id);
    group.children?.forEach(subGroup => {
      expandedSubGroups.value.add(`${group.id}-${subGroup.id}`);
    });
  });
  
  // 获取题目列表
  fetchQuestions();
});
</script>

<template>
  <div class="flex h-[calc(100vh-4rem)] bg-slate-50">
    
    <!-- 左侧知识点树侧边栏 -->
    <aside class="w-[300px] bg-white border-r border-slate-200 flex flex-col flex-shrink-0">
      <div class="p-4 border-b border-slate-200">
        <h2 class="text-sm font-semibold text-slate-800">知识点筛选</h2>
        <p class="text-xs text-slate-500 mt-1">{{ currentSubject }} · {{ currentGrade }}</p>
      </div>
      
      <div class="flex-1 overflow-y-auto p-3">
        <KnowledgeTreeSidebar
          :knowledge-tree="knowledgeTree"
          :knowledge-stats="knowledgeStats"
          :selected-topics="selectedTopics"
          :expanded-groups="expandedGroups"
          :expanded-sub-groups="expandedSubGroups"
          @toggle-topic="handleToggleTopic"
          @toggle-group="handleToggleGroup"
          @toggle-subgroup="handleToggleSubGroup"
        />
      </div>
      
      <!-- 已选知识点汇总 -->
      <div v-if="selectedTopics.length > 0" class="p-3 border-t border-slate-200 bg-slate-50">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-medium text-slate-600">已选知识点</span>
          <button
            @click="clearTopicFilter"
            class="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
          >
            清除全部
          </button>
        </div>
        <div class="flex flex-wrap gap-1.5">
          <span
            v-for="topic in selectedTopics"
            :key="topic"
            class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-indigo-100 text-indigo-700 text-xs"
          >
            {{ topic }}
            <button
              @click="handleToggleTopic(topic)"
              class="hover:text-indigo-900"
            >
              ×
            </button>
          </span>
        </div>
      </div>
    </aside>
    
    <!-- 右侧主内容区 -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <!-- 顶部统计与搜索栏 -->
      <header class="bg-white border-b border-slate-200 p-4">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h1 class="text-2xl font-bold text-slate-900">题库管理</h1>
            <p class="text-slate-600 text-sm mt-1">浏览已过审的精品题库</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">
              共 <strong class="text-slate-900">{{ filteredQuestions.length }}</strong> 道题目
            </span>
          </div>
        </div>
        
        <!-- 搜索框 -->
        <div class="flex items-center gap-3">
          <div class="relative flex-1 max-w-md">
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索题目内容或知识点..."
              class="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none text-sm"
            />
            <svg
              class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <!-- 筛选标签 -->
          <div class="flex items-center gap-2">
            <span
              v-if="selectedTopics.length > 0"
              class="px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-700 text-xs font-medium"
            >
              {{ selectedTopics.length }} 个知识点
            </span>
          </div>
        </div>
      </header>
      
      <!-- 题目列表区域 -->
      <div class="flex-1 overflow-y-auto p-4">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="flex items-center justify-center h-64">
          <div class="flex items-center gap-3 text-slate-500">
            <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span class="text-sm">加载中...</span>
          </div>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="errorMsg" class="flex items-center justify-center h-64">
          <div class="text-center">
            <p class="text-red-600 mb-2">{{ errorMsg }}</p>
            <button
              @click="fetchQuestions"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors"
            >
              重试
            </button>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="filteredQuestions.length === 0" class="flex items-center justify-center h-64">
          <div class="text-center">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 flex items-center justify-center">
              <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p class="text-slate-500">暂无符合条件的题目</p>
            <p v-if="selectedTopics.length > 0 || searchKeyword" class="text-slate-400 text-sm mt-1">
              请尝试调整筛选条件
            </p>
          </div>
        </div>
        
        <!-- 题目列表 -->
        <div v-else class="space-y-3">
          <div
            v-for="question in paginatedQuestions"
            :key="question.id"
            class="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1">
                <!-- 题目内容预览 -->
                <div class="text-sm text-slate-800 line-clamp-2 mb-2">
                  {{ question.content?.substring(0, 200) || '无内容' }}
                  <span v-if="question.content && question.content.length > 200">...</span>
                </div>
                
                <!-- 标签信息 -->
                <div class="flex items-center gap-2 flex-wrap">
                  <span
                    v-if="question.topic"
                    class="px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 text-xs font-medium"
                  >
                    {{ question.topic }}
                  </span>
                  <span
                    v-if="question.type"
                    class="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 text-xs font-medium"
                  >
                    {{ question.type }}
                  </span>
                  <span
                    v-if="question.difficulty"
                    class="px-2 py-0.5 rounded-full bg-amber-50 text-amber-600 text-xs font-medium"
                  >
                    {{ question.difficulty }}
                  </span>
                </div>
              </div>
              
              <!-- 操作按钮 -->
              <div class="flex items-center gap-2 flex-shrink-0">
                <button
                  class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                  title="查看详情"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- 分页器 -->
          <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 pt-4">
            <button
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="px-3 py-1.5 rounded-lg border border-slate-300 text-sm font-medium"
              :class="currentPage === 1 ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-white text-slate-700 hover:bg-slate-50'"
            >
              上一页
            </button>
            <span class="text-sm text-slate-600">
              {{ currentPage }} / {{ totalPages }}
            </span>
            <button
              @click="currentPage++"
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 rounded-lg border border-slate-300 text-sm font-medium"
              :class="currentPage === totalPages ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-white text-slate-700 hover:bg-slate-50'"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
</style>