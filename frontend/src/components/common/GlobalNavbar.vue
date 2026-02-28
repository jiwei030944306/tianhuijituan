<!-- 
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 全局导航栏 (GlobalNavbar.vue)
  本组件是系统顶部的全局导航栏，负责面包屑导航、学科学段上下文展示、用户认证及使用说明入口。
  它根据用户登录状态和当前路由动态调整导航内容，确保用户始终清楚自己所处的业务环境。
-->

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：computed, ref (响应式计算与状态)
 * - 路由：useRouter, useRoute (路由跳转与当前路径获取)
 * - 状态管理：useUserStore (用户登录信息), useContextStore (学科学段上下文)
 * - 图标库：Element Plus Icons (Lightning, ArrowRight, ArrowLeft, Grid, SwitchButton, QuestionFilled)
 * - 子组件：UserAuthWidget (用户认证), HelpGuide (使用说明弹窗)
 */
import { computed, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useContextStore } from '@/stores/context';
import {
  Lightning,
  ArrowRight,
  ArrowLeft,
  Grid,
  SwitchButton,
  QuestionFilled
} from '@element-plus/icons-vue';
import UserAuthWidget from '@/components/UserAuthWidget.vue';
import HelpGuide from '@/components/common/HelpGuide.vue';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 类型定义 ---
interface PageTitleMap {
  [key: string]: string;
}

// --- 3. 核心代码强调：页面标题映射配置 ---
// 定义系统各页面的中文标题，用于导航栏中间显示
const pageTitleMap: PageTitleMap = {
  '/home': '协作大厅',
  '/upload': '上传管理',
  '/check': '同步工作台',
  '/refine': '标化中心',
  '/library': '题库管理',
  '/monitor': '流转监控',
  '/logs': '日志反馈',
  '/': '智研题库云系统'  // 默认标题
};

// --- 响应式状态初始化 ---
const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const contextStore = useContextStore();
const showGuide = ref(false);

// --- 动态计算属性区 ---

// 判断是否为 landing 页（路径为 /landing）
const isLandingPage = computed(() => {
  return route.path === '/landing';
});

// 根据当前路由确定页面类型（用于 HelpGuide 内容适配）
const currentPageType = computed(() => {
  if (route.path === '/landing') return 'landing';
  if (route.path === '/home') return 'home';
  if (route.path === '/upload' || route.path.startsWith('/upload')) return 'upload';
  if (route.path === '/check' || route.path.startsWith('/check')) return 'check';
  if (route.path === '/refine' || route.path.startsWith('/refine')) return 'refine';
  return 'home'; // 默认返回 home 类型
});

// 当前页面标题（从映射表中获取）
const currentPageTitle = computed(() => {
  return pageTitleMap[route.path] || pageTitleMap['/'];
});

// 是否显示二级导航（landing 页不显示）
const shouldShowModuleNav = computed(() => {
  return !isLandingPage.value;
});

// --- 3. 核心代码强调：一级导航内容动态计算 ---
// 根据用户登录状态和学科学段选择状态，动态调整左侧导航内容
// 逻辑优先级：未登录 > 已登录未选学科 > 已登录已选学科
const primaryNavContent = computed(() => {
  if (isLandingPage.value) {
    return {
      show: false
    };
  }

  // 1. 未登录状态（最高优先级）
  if (!userStore.isLoggedIn) {
    return {
      show: true,
      text: '返回入口',
      icon: ArrowLeft,
      mode: 'guest'
    };
  }

  // 2. 已登录但未选择学科学段
  if (!contextStore.grade || !contextStore.subject) {
    return {
      show: true,
      text: '选择学科',
      icon: ArrowLeft,
      mode: 'select-subject'
    };
  }

  // 3. 已登录且已选择学科学段
  return {
    show: true,
    level: contextStore.levelName,
    subject: contextStore.subjectName,
    mode: 'context'
  };
});

// 用户信息（从 Store 获取）
const userInfo = computed(() => {
  return {
    name: userStore.userName || '访客',
    avatar: undefined,  // 可根据需要添加头像URL
    role: '教研组长',
    permission: 'Admin Access'
  };
});

// --- 交互方法区 ---

// 返回 landing 页
const goBackToLanding = () => {
  router.push('/landing');
};

// 返回 home 页
const goBackToHome = () => {
  router.push('/home');
};

// 退出登录
const handleLogout = () => {
  userStore.logout();
  router.push('/landing');
};
</script>

<template>
  <!-- ==========================================
       2. 主要功能代码分区注释 - 页面渲染区
       ========================================== -->

  <!-- [Header Container] 顶部固定导航栏 -->
  <header
    class="fixed top-0 left-0 right-0 h-16 bg-white border-b border-slate-200 flex items-center px-6 justify-between flex-shrink-0 z-30 shadow-sm transition-all relative"
    :class="{ 'shadow-lg': !isLandingPage }"
  >
    <!-- [Left Section] 左侧：面包屑导航 -->
    <div class="flex items-center gap-3 whitespace-nowrap z-10">
      <!-- 品牌按钮（返回 landing） -->
      <button
        @click="goBackToLanding"
        class="flex items-center gap-2 text-indigo-600 font-black text-xl tracking-tighter mr-2 select-none hover:opacity-80 transition-opacity"
        title="返回首页 (Back to Landing)"
      >
        <Lightning class="w-5 h-5 fill-current" />
        <span class="hidden xl:block">ZyCloud</span>
      </button>

      <!-- 分隔线（landing 页不显示） -->
      <div v-if="!isLandingPage" class="h-6 w-px bg-slate-200 mx-2"></div>

      <!-- 一级导航（学段·学科，landing 页不显示） -->
      <div v-if="primaryNavContent.show" class="flex items-center">
        <!-- 3. 核心代码强调：模式1 - 已登录且已选择学科学段 -->
        <!-- 显示当前学段学科，并提供返回协作大厅和切换学科的快捷入口 -->
        <template v-if="primaryNavContent.mode === 'context'">
          <button
            @click="goBackToHome"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all group"
            :class="route.path === '/home' ? 'bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200' : 'hover:bg-slate-100 text-slate-700'"
            title="回到协作大厅"
          >
            <div
              :class="route.path === '/home' ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-500'"
              class="w-5 h-5 rounded flex items-center justify-center text-xs font-bold group-hover:bg-slate-300 transition-colors"
            >
              {{ primaryNavContent.level?.charAt(0) }}
            </div>
            <span class="font-bold text-sm">{{ primaryNavContent.level }}·{{ primaryNavContent.subject }}</span>
          </button>

          <!-- 切换学科按钮 -->
          <button
            @click="goBackToLanding"
            class="ml-1 p-1.5 rounded-full text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors"
            title="切换学科 (Switch Subject)"
          >
            <SwitchButton class="w-3.5 h-3.5" />
          </button>
        </template>

        <!-- 3. 核心代码强调：模式2 - 已登录但未选择学科学段 -->
        <!-- 提示用户需要先选择学科环境 -->
        <template v-else-if="primaryNavContent.mode === 'select-subject'">
          <button
            @click="goBackToLanding"
            class="flex items-center gap-1 text-amber-600 hover:text-amber-700 text-sm font-bold transition-colors"
          >
            <ArrowLeft class="w-3.5 h-3.5" /> 选择学科
          </button>
          <div class="h-4 w-px bg-slate-200 mx-1"></div>
          <div class="font-bold text-amber-500 text-sm">
            未选环境
          </div>
        </template>

        <!-- 3. 核心代码强调：模式3 - 未登录状态 -->
        <!-- 显示访客模式并提供返回入口 -->
        <template v-else>
          <button
            @click="goBackToLanding"
            class="flex items-center gap-1 text-slate-500 hover:text-indigo-600 text-sm font-bold transition-colors"
          >
            <ArrowLeft class="w-3.5 h-3.5" /> 返回入口
          </button>
          <div class="h-4 w-px bg-slate-200 mx-1"></div>
          <div class="font-bold text-slate-400 text-sm">
            访客模式 (Global Tool)
          </div>
        </template>
      </div>
    </div>

    <!-- [Center Section] 中间：当前模块标题（绝对居中） -->
    <!-- 3. 核心代码强调：动态显示当前页面标题，帮助用户定位当前位置 -->
    <div
      v-if="shouldShowModuleNav"
      class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-2 text-slate-600 font-medium text-sm animate-fade-in-left whitespace-nowrap"
    >
      <Grid class="w-4 h-4 text-slate-400"/>
      <span>{{ currentPageTitle }}</span>
    </div>

    <!-- [Right Section] 右侧：用户认证与使用说明 -->
    <div class="flex items-center z-10 ml-auto gap-3">
      <!-- 使用说明按钮 -->
      <button
        @click="showGuide = true"
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition-all text-sm font-medium"
        title="使用说明"
      >
        <el-icon><QuestionFilled /></el-icon>
        <span class="hidden sm:inline">使用说明</span>
      </button>

      <!-- 用户信息组件 -->
      <UserAuthWidget />
    </div>
  </header>

  <!-- [Modal] 使用说明弹窗 -->
  <HelpGuide v-model="showGuide" :page-type="currentPageType" />
</template>

<style scoped>
/* 组件样式使用 Tailwind CSS，无需额外样式 */
</style>