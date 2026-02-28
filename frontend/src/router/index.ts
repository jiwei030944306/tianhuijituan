import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useContextStore } from '@/stores/context';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/landing'
  },
  {
    path: '/landing',
    name: 'Landing',
    component: () => import('@/views/Landing.vue')
  },
  {
    path: '/lab',
    name: 'SymbolLab',
    component: () => import('@/views/showcase/SymbolLab.vue'),
    meta: { hideNavbar: true }
  },
  {
    path: '/latex-tester',
    name: 'LaTeXTester',
    component: () => import('@/views/showcase/SymbolLab.vue'),
    meta: { hideNavbar: true }
  },
  {
    path: '/showcase',
    name: 'Showcase',
    component: () => import('@/views/Showcase.vue'),
    meta: { hideNavbar: true }
  },
  {
    path: '/theme-preview',
    name: 'ThemePreview',
    component: () => import('@/views/showcase/ThemePreview.vue'),
    meta: { hideNavbar: true }
  },
  {
    path: '/question-card-showcase',
    name: 'QuestionCardShowcase',
    component: () => import('@/views/showcase/QuestionCardShowcase.vue'),
    meta: { hideNavbar: true }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/check',
    name: 'QuestionCheck',
    component: () => import('@/views/QuestionCheckNew.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'UploadManagement',
    component: () => import('@/views/UploadManagement.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/refine',
    name: 'QuestionRefine',
    component: () => import('@/views/QuestionRefine.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/library',
    name: 'QuestionLibrary',
    component: () => import('@/views/QuestionLibrary.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-test',
    name: 'AITest',
    component: () => import('@/views/showcase/AITest.vue'),
    meta: { hideNavbar: true }
  },
  {
    path: '/system/monitor',
    name: 'SystemMonitor',
    component: () => import('@/views/SystemMonitor/index.vue'),
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫：检查登录状态及环境上下文
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const contextStore = useContextStore();

  // 1. 检查路由是否需要登录
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn || !userStore.currentUser) {
      // 未登录，跳转到 Landing 页
      next('/landing');
      return;
    }

    // 2. 检查是否选择了环境（学段/学科）
    // 排除 Landing 页面本身，防止死循环
    // Home 页及其他业务页面必须有 context (grade & subject)
    // 注意：Store 中使用的是 grade 字段，而不是 level
    if (to.path !== '/landing' && (!contextStore.grade || !contextStore.subject)) {
      // 虽然登录了，但没有选择学段和学科，强制跳转回 Landing 选择
      console.warn('Router Guard: Context not set (grade/subject missing), redirecting to Landing');
      next('/landing');
      return;
    }
  }

  next();
});

export default router;