<!--
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 组件工坊 (Showcase.vue)
  本页面作为系统工具与组件展示中心，提供符号实验室、试题卡片展示、主题预览等实用工具的导航入口。
-->
<template>
  <div class="absolute top-16 left-0 right-0 bottom-0 bg-slate-50 overflow-y-auto">
    <div class="max-w-7xl mx-auto px-6 py-12">

      <!-- [Header Section] 页面标题与简介 -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-50 border border-purple-100 text-purple-700 text-xs font-bold uppercase tracking-wide mb-4">
          <Box :size="14" class="fill-current" /> Showcase Hub
        </div>
        <h1 class="text-4xl md:text-5xl font-extrabold text-slate-900 mb-4 tracking-tight">
          组件工坊
        </h1>
        <p class="text-lg text-slate-600 max-w-2xl mx-auto">
          系统工具与组件展示中心，包含符号实验室、UI组件库等实用工具
        </p>
      </div>

      <!-- [Tools Grid] 工具卡片展示区 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        <!-- LaTeX Tester 卡片 -->
        <div
          @click="navigateTo('/latex-tester')"
          class="group bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-lg hover:border-purple-300 transition-all cursor-pointer"
        >
          <div class="flex items-start gap-4 mb-4">
            <div class="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Beaker :size="24" />
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-slate-800 group-hover:text-purple-700 transition-colors">符号实验室</h3>
              <p class="text-xs text-slate-400 uppercase tracking-wide mt-0.5">LaTeX Tester</p>
            </div>
          </div>
          <p class="text-sm text-slate-600 leading-relaxed">
            实时预览 LaTeX 数学公式渲染效果，支持 KaTeX 语法测试
          </p>
        </div>

<!-- Question Card Showcase 卡片 -->
        <div
          @click="navigateTo('/question-card-showcase')"
          class="group bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-lg hover:border-blue-300 transition-all cursor-pointer"
        >
          <div class="flex items-start gap-4 mb-4">
            <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <FileText :size="24" />
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-slate-800 group-hover:text-blue-700 transition-colors">试题卡片</h3>
              <p class="text-xs text-slate-400 uppercase tracking-wide mt-0.5">QuestionCard</p>
            </div>
          </div>
          <p class="text-sm text-slate-600 leading-relaxed">
            展示试题卡片组件在不同状态、难度和题型下的表现
          </p>
        </div>

        <!-- Theme Preview 卡片 -->
        <div
          @click="navigateTo('/theme-preview')"
          class="group bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-lg hover:border-emerald-300 transition-all cursor-pointer"
        >
          <div class="flex items-start gap-4 mb-4">
            <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Palette :size="24" />
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-slate-800 group-hover:text-emerald-700 transition-colors">主题预览</h3>
              <p class="text-xs text-slate-400 uppercase tracking-wide mt-0.5">Theme Preview</p>
            </div>
          </div>
          <p class="text-sm text-slate-600 leading-relaxed">
            系统配色方案与样式指南，包含色彩系统、排版规范与基础组件
          </p>
        </div>

        <!-- AI Test 卡片 -->
        <div
          @click="navigateTo('/ai-test')"
          class="group bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-lg hover:border-amber-300 transition-all cursor-pointer"
        >
          <div class="flex items-start gap-4 mb-4">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-50 to-purple-50 text-amber-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Sparkles :size="24" />
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-slate-800 group-hover:text-amber-700 transition-colors">AI 服务测试</h3>
              <p class="text-xs text-slate-400 uppercase tracking-wide mt-0.5">AI Optimizer</p>
            </div>
          </div>
          <p class="text-sm text-slate-600 leading-relaxed">
            测试 AI 接口连接、提示词效果、异步任务管理，支持多模态图片分析
          </p>
        </div>

      </div>

      <!-- [Back Button] 返回主页按钮 -->
      <div class="mt-12 text-center">
        <button
          @click="router.push('/home')"
          class="inline-flex items-center gap-2 px-6 py-2.5 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <ArrowLeft :size="16" />
          返回主页
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 4. 引用挂载说明
 * - 路由跳转：useRouter（Vue Router 路由导航）
 * - 图标库：lucide-vue-next（UI 图标组件）
 */
import { useRouter } from 'vue-router';
import { Box, Beaker, FileText, Palette, ArrowLeft, Sparkles } from 'lucide-vue-next';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 路由导航模块 ---

const router = useRouter();

// 3. 核心代码强调：工具卡片点击跳转
// 封装路由跳转逻辑，统一管理页面导航
const navigateTo = (route: string) => {
  router.push(route);
};
</script>

<style scoped>
/* Additional styles if needed */
</style>
