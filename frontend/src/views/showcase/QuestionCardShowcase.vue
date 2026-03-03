<!--
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 试题卡片展示 (QuestionCardShowcase.vue)
  本页面基于文茂天卉中学 2023-2024 学年第一学期阶段二学情反馈试题数据，展示 QuestionCard 组件在不同状态、难度和题型下的真实表现。
-->
<template>
  <div class="question-card-showcase">
    <div class="showcase-header">
      <h1>QuestionCard 组件展示 (真实数据版)</h1>
      <p class="description">基于文茂天卉中学 2023-2024 学年第一学期阶段二学情反馈试题数据展示</p>
    </div>

    <!-- [Stats Summary] 统计摘要 -->
    <div class="stats-summary mb-8 flex gap-4 justify-center">
      <div class="stat-card">
        <span class="label">总题数:</span>
        <span class="value">{{ allQuestions.length }}</span>
      </div>
      <div class="stat-card">
        <span class="label">有图片:</span>
        <span class="value">{{ questionsWithImages.length }}</span>
      </div>
    </div>

    <!-- [Real Questions Section] 真实试题展示区 -->
    <section class="showcase-section">
      <div class="flex justify-between items-center mb-6">
        <h2>真实试题展示 (26道题)</h2>
        <div class="status-legend flex gap-4 text-xs">
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-slate-100 border border-slate-200"></span> 草稿 (默认)</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-blue-50 border border-blue-200"></span> 待标化 (第5,10题)</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-emerald-50 border border-emerald-200"></span> 已归档 (第15,20题)</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-red-50 border border-red-200"></span> 异常 (第25题)</span>
        </div>
      </div>
      
      <div class="card-grid">
        <QuestionCard 
          v-for="q in displayQuestions" 
          :key="q.id" 
          :question="q" 
          selectable
          @click="handleCardClick(q)"
        />
      </div>
    </section>

    <!-- [Question Types Breakdown] 题型分布展示区 -->
    <section class="showcase-section">
      <h2>题型分布展示</h2>
      <div class="type-section" v-for="(qs, type) in groupedQuestions" :key="type">
        <h3 class="type-title">{{ getTypeName(type) }}</h3>
        <div class="card-grid">
          <QuestionCard 
            v-for="q in qs.slice(0, 4)" 
            :key="q.id" 
            :question="q" 
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * 4. 引用挂载说明
 * - 响应式：computed, ref, onMounted（Vue 3 响应式 API）
 * - 组件引用：QuestionCard.vue（通用试题卡片组件）
 * - 类型定义：Question（试题类型接口）
 * - 工具函数：convertJsonToQuestions（JSON 数据转换工具）
 */
import { computed, ref, onMounted } from 'vue'
import QuestionCard from '@/components/common/QuestionCard.vue'
import type { Question } from '@/types/question'
import { convertJsonToQuestions } from '@/utils/questionDataConverter'

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 组件状态管理模块 ---

const loading = ref(false)
const error = ref<string | null>(null)
const rawQuestions = ref<any[]>([])
const currentBatchId = ref<string>('')

// --- 数据获取模块 ---

// 3. 核心代码强调：从后端 API 获取试题数据
// 使用批次 ID 获取真实试题数据，支持错误处理和加载状态管理
async function fetchQuestions() {
  loading.value = true
  error.value = null

  try {
    // 使用批次 ID 获取真实试题数据
    const batchId = '20260204-214305-atctxn'
    const folderCode = 'm7s9m2' // 测试用 folder_code
    currentBatchId.value = batchId
    const response = await fetch(`/api/questions/batch/${batchId}?folder_code=${folderCode}`)

    if (!response.ok) {
      throw new Error(`获取数据失败: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    rawQuestions.value = data.questions || []
  } catch (e) {
    error.value = e instanceof Error ? e.message : '未知错误'
    console.error('获取试题数据失败:', e)
  } finally {
    loading.value = false
  }
}

// 3. 核心代码强调：组件挂载时自动获取数据
// 确保页面加载时立即获取试题数据
onMounted(() => {
  fetchQuestions()
})

// --- 计算属性模块 ---

// 3. 核心代码强调：转换并处理原始数据
// 将 API 返回的原始数据转换为 Question 类型，并设置演示用的不同状态
const allQuestions = computed(() => {
  const questions = convertJsonToQuestions(rawQuestions.value, currentBatchId.value)

  // Manually set different statuses for demonstration as requested
  return questions.map((q, index) => {
    const num = index + 1
    if (num === 5 || num === 10) return { ...q, status: 'active' as const }
    if (num === 15 || num === 20) return { ...q, status: 'archived' as const }
    if (num === 25) return { ...q, status: 'error' as const, comment: '图片加载失败或格式不正确' }
    return q
  })
})

// 3. 核心代码强调：展示题目列表
// 直接使用转换后的所有题目
const displayQuestions = computed(() => allQuestions.value)

// 3. 核心代码强调：筛选包含图片的题目
// 用于统计和展示有配图的试题
const questionsWithImages = computed(() =>
  allQuestions.value.filter(q => q.stemImages && q.stemImages.length > 0)
)

// 3. 核心代码强调：按题型分组题目
// 将题目按照题型分类，便于按类型展示
const groupedQuestions = computed(() => {
  const groups: Record<string, Question[]> = {}
  allQuestions.value.forEach(q => {
    if (!groups[q.type]) groups[q.type] = []
    groups[q.type].push(q)
  })
  return groups
})

// --- 工具函数模块 ---

// 3. 核心代码强调：题型名称映射
// 将英文题型代码转换为中文显示名称
function getTypeName(type: string): string {
  const map: Record<string, string> = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    fill_blank: '填空题',
    short_answer: '简答题',
    calculation: '计算题',
    application: '应用题',
    true_false: '判断题',
    subjective: '解答题'
  }
  return map[type] || type
}

// --- 事件处理模块 ---

// 3. 核心代码强调：卡片点击事件处理
// 记录用户点击的题目信息，可用于后续的详情展示或其他交互
function handleCardClick(question: Question) {
  console.log('Clicked question:', question.id, question.questionNumber)
}
</script>

<style scoped>
/* 5. 样式定义 */
/* 主容器样式 */
.question-card-showcase {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
  background-color: #f8fafc;
  min-h: 100vh;
}

/* 头部区域样式 */
.showcase-header {
  margin-bottom: 3rem;
  text-align: center;
}

.showcase-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.showcase-header .description {
  font-size: 1.125rem;
  color: #64748b;
}

/* 统计摘要区域样式 */
.stats-summary {
  display: flex;
  justify-content: center;
  gap: 2rem;
}

/* 统计卡片样式 */
.stat-card {
  background: white;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid #e2e8f0;
}

.stat-card .label {
  color: #64748b;
  font-size: 0.875rem;
}

.stat-card .value {
  color: #4f46e5;
  font-weight: 700;
  font-size: 1.25rem;
}

/* 展示区域样式 */
.showcase-section {
  margin-bottom: 4rem;
}

.showcase-section h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
}

/* 题型分组区域样式 */
.type-section {
  margin-top: 2rem;
}

.type-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 1rem;
  padding-left: 0.5rem;
  border-left: 4px solid #6366f1;
}

/* 卡片网格布局样式 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1.5rem;
}

/* 响应式布局：移动端单列显示 */
@media (max-width: 640px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
