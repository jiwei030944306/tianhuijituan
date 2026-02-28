<!-- 
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 核心工作台 (Home.vue)
  本页面作为系统的中心枢纽，整合了 P0-P5 六大核心功能模块入口。
  它负责展示当前业务上下文（学段/学科），并提供直观的导航与各模块状态监控。
-->

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：computed (响应式计算)
 * - 路由跳转：useRouter (Vue Router)
 * - 状态管理：useContextStore (Pinia, 用于获取当前学段学科上下文)
 * - UI 组件：ElMessage (Element Plus 提示)
 * - 图标库：lucide-vue-next (Lucide 图标集)
 */
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useContextStore } from '@/stores/context';
import { ElMessage } from 'element-plus';
import {
  Layout,
  GitMerge,
  Archive,
  Activity,
  Bug,
  ArrowRight,
  Zap,
  Upload
} from 'lucide-vue-next';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 路由与状态初始化 ---
const router = useRouter();
const contextStore = useContextStore();

// --- 3. 核心代码强调：核心模块入口配置 ---
// 定义了系统中 6 大中心的入口信息，控制模块的可用性(enabled)与路由跳转
const modules = computed(() => [
  { 
    id: 'upload', 
    title: '上传管理', 
    sub: 'Upload Manager',
    desc: '快速上传题目文件，实时查看上传状态与结果。', 
    icon: Upload, 
    color: 'bg-green-600', 
    gradient: 'from-green-500 to-green-600',
    lightColor: 'bg-green-50 group-hover:bg-green-100',
    textColor: 'text-green-600',
    stats: '可用',
    route: '/upload',
    enabled: true
  },
  {
    id: 'check',
    title: '同步工作台',
    sub: 'Check & Sync',
    desc: '管理已上传试题批次，进行内容检视、格式校验与质量同步。',
    icon: Layout,
    color: 'bg-blue-600',
    gradient: 'from-blue-500 to-blue-600',
    lightColor: 'bg-blue-50 group-hover:bg-blue-100',
    textColor: 'text-blue-600',
    stats: '可用',
    route: '/check',
    enabled: true
  }, 
  {
    id: 'refine',
    title: '标化中心',
    sub: 'Standardization Hub',
    desc: '对已入库题目进行知识点打标、AI 解析编写与人工审核。',
    icon: GitMerge,
    color: 'bg-indigo-600',
    gradient: 'from-indigo-500 to-indigo-600',
    lightColor: 'bg-indigo-50 group-hover:bg-indigo-100',
    textColor: 'text-indigo-600',
    stats: '可用',
    route: '/refine',
    enabled: true
  },
{ 
    id: 'library', 
    title: '题库管理', 
    sub: 'Asset Archive',
    desc: '浏览已过审的精品题库，导出试卷，记录教学与教研心得。', 
    icon: Archive, 
    color: 'bg-emerald-600', 
    gradient: 'from-emerald-500 to-emerald-600',
    lightColor: 'bg-emerald-50 group-hover:bg-emerald-100',
    textColor: 'text-emerald-600',
    stats: '可用',
    route: '/library',
    enabled: true
  },
  { 
    id: 'P4', 
    title: '全局看板', 
    sub: 'Monitor Dashboard',
    desc: '宏观监控题目流转效率、错误分布与学科覆盖率统计。', 
    icon: Activity, 
    color: 'bg-amber-500', 
    gradient: 'from-amber-400 to-amber-500',
    lightColor: 'bg-amber-50 group-hover:bg-amber-100',
    textColor: 'text-amber-600',
    stats: '待规划',
    route: '',
    enabled: false
  },
  { 
    id: 'P5', 
    title: '日志反馈', 
    sub: 'AI Iteration',
    desc: '聚合错误日志，生成 Prompt 修正指令，闭环训练 AI 清洗能力。', 
    icon: Bug, 
    color: 'bg-rose-500', 
    gradient: 'from-rose-500 to-rose-600',
    lightColor: 'bg-rose-50 group-hover:bg-rose-100',
    textColor: 'text-rose-600',
    stats: '待规划',
    route: '',
    enabled: false
  },
]);

// --- 导航跳转处理 ---
const handleNavigate = (module: any) => {
  if (module.enabled && module.route) {
    router.push(module.route);
  } else {
    // 简单的提示逻辑，实际可使用 ElMessage
    console.warn(`Module ${module.id} is not ready yet.`);
  }
};

// --- 数据转换工具 ---
const getGradeLabel = (g: string | null) => {
  if (g === 'junior') return '初中';
  if (g === 'senior') return '高中';
  return '';
};
</script>

<template>
  <div class="absolute top-16 left-0 right-0 bottom-0 bg-slate-50 overflow-y-auto">
    <div class="max-w-7xl mx-auto px-6 py-12 md:py-16">
      
      <!-- ==========================================
           2. 主要功能代码分区注释 - 页面渲染区
           ========================================== -->

      <!-- [Hero Section] 欢迎语与业务上下文展示 -->
      <!-- 3. 核心代码强调：动态展示当前选中的学段与学科 -->
      <div class="text-center mb-16 animate-fade-in-up">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-bold uppercase tracking-wide mb-6 shadow-sm">
          <Zap :size="14" class="fill-current" /> ZyCloud Core v2.4
        </div>
        <h1 class="text-4xl md:text-6xl font-extrabold text-slate-900 mb-6 tracking-tight">
          <template v-if="contextStore.grade && contextStore.subject">
             <span class="text-indigo-600">{{ getGradeLabel(contextStore.grade) }}{{ contextStore.subjectName }}</span> 
             <span class="mx-3 text-slate-300">·</span>
             智能化教研协作平台
          </template>
          <template v-else>
             智能化教研协作平台
          </template>
        </h1>
        <p class="text-lg md:text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
          连接 <span class="text-indigo-600 font-semibold">AI 数据清洗</span> 与 <span class="text-indigo-600 font-semibold">人工专家教研</span> 的流水线。<br class="hidden md:block" />从本地代码扫描到最终资产归档，提供全链路的质量控制与效率工具。
        </p>
      </div>

      <!-- [Main Work Modules] 核心功能入口网格 -->
      <!-- 3. 核心代码强调：循环渲染 modules，根据 enabled 状态动态切换样式与点击行为 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
        <div 
          v-for="(m, idx) in modules"
          :key="m.id"
          @click="handleNavigate(m)"
          class="group bg-white rounded-3xl p-8 shadow-sm transition-all duration-300 border border-slate-100 flex flex-col relative overflow-hidden"
          :class="m.enabled ? 'hover:shadow-2xl hover:-translate-y-1 cursor-pointer' : 'opacity-60 cursor-not-allowed grayscale-[0.5]'"
          :style="{ animationDelay: `${idx * 100}ms` }"
        >
          <!-- 模块图标与标识 -->
          <div class="flex items-start justify-between mb-6 relative z-10">
            <div class="w-16 h-16 rounded-2xl flex items-center justify-center transition-colors shadow-inner"
              :class="[m.lightColor, m.textColor]"
            >
              <component :is="m.icon" :size="32" />
            </div>
            <div class="flex items-center gap-2">
               <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-50 px-2 py-1 rounded-md border border-slate-100">{{ m.id }}</span>
            </div>
          </div>
          
          <!-- 模块文本信息 -->
          <div class="relative z-10 flex-1">
            <h3 class="text-2xl font-bold text-slate-800 mb-1 transition-colors"
               :class="m.enabled ? 'group-hover:text-indigo-600' : ''"
            >
              {{ m.title }}
            </h3>
            <div class="text-xs font-mono text-slate-400 mb-4 uppercase tracking-wider">{{ m.sub }}</div>
            <p class="text-sm text-slate-600 leading-relaxed mb-6">
              {{ m.desc }}
            </p>
          </div>

          <!-- 底部状态与交互引导 -->
          <div class="relative z-10 mt-auto flex items-center justify-between border-t border-slate-100 pt-4">
             <div class="text-xs font-semibold text-slate-500 flex items-center gap-1.5">
                <div class="w-1.5 h-1.5 rounded-full" :class="m.color"></div>
                {{ m.stats }}
             </div>
             <div class="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-slate-300 transition-colors"
                :class="m.enabled ? 'group-hover:bg-slate-900 group-hover:text-white' : ''"
             >
                <ArrowRight :size="16" />
             </div>
          </div>

          <!-- 背景装饰效果 -->
          <div class="absolute -right-8 -bottom-8 w-40 h-40 rounded-full opacity-0 transition-opacity duration-500 bg-gradient-to-br"
            :class="[m.gradient, m.enabled ? 'group-hover:opacity-5' : '']"
          />
        </div>
      </div>

      <!-- [Footer Info] 版权信息区 -->
      <div class="mt-24 text-center border-t border-slate-200 pt-10">
        <p class="text-xs text-slate-400 font-mono">
          © 2026 ZyCloud Research Team. Powered by Vue 3.4 & Tailwind.
        </p>
      </div>

    </div>
  </div>
</template>


<style scoped>
/* Tailwind handles most styles */
.animate-fade-in-up {
  animation: fadeInUp 0.5s ease-out forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
