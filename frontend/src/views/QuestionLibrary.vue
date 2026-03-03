<!--
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 题库管理 (QuestionLibrary.vue)
  本页面是系统的题库管理模块，负责浏览已过审的精品题库、导出试卷、记录教学与教研心得。
-->

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：ref, computed, onMounted (状态驱动视图)
 * - 路由跳转：useRouter (环境校验)
 * - 状态管理：useContextStore (业务上下文), useUserStore (用户信息)
 */
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useContextStore } from '@/stores/context';
import { useUserStore } from '@/stores/user';

// --- 环境校验逻辑 ---
const router = useRouter();
const contextStore = useContextStore();
const userStore = useUserStore();

if (!contextStore.grade || !contextStore.subject) {
  router.push('/');
}

const currentSubject = contextStore.subjectName || '数学';
const folderCode = contextStore.folderCode || '';

// --- 响应式状态管理 ---
const isLoading = ref(false);
const errorMsg = ref<string | null>(null);

// --- 初始化挂载 ---
onMounted(() => {
  console.log('题库管理页面加载');
});
</script>

<template>
  <div class="absolute top-16 left-0 right-0 bottom-0 bg-slate-50 overflow-y-auto">
    <div class="max-w-7xl mx-auto px-6 py-12">
      
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-900">题库管理</h1>
        <p class="text-slate-600 mt-2">浏览已过审的精品题库，导出试卷，记录教学与教研心得</p>
      </div>

      <!-- 占位内容 -->
      <div class="bg-white rounded-2xl p-12 text-center border border-slate-200">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-100 flex items-center justify-center">
          <svg class="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-slate-800 mb-2">题库管理功能开发中</h2>
        <p class="text-slate-600">此页面将提供题库浏览、试卷导出、教学笔记等功能</p>
      </div>

    </div>
  </div>
</template>

<style scoped>
</style>