<!-- 
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 门户页 (Landing.vue)
  本页面是系统的入口门户，负责用户教研场景的选择（学段与学科）。
  它是系统初始化的第一步，确保后续所有操作都在正确的业务上下文（Context）中进行。
-->

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col relative overflow-y-auto pt-16">
    <!-- Background Decor -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
      <div class="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full bg-indigo-200/20 blur-3xl"></div>
      <div class="absolute bottom-[-10%] left-[-5%] w-[500px] h-[500px] rounded-full bg-blue-200/20 blur-3xl"></div>
    </div>

    <div class="flex-1 flex flex-col items-center justify-center p-6 z-10 py-16">
      <div class="max-w-5xl w-full">
        
        <!-- ==========================================
             2. 主要功能代码分区注释 - 页面渲染区
             ========================================== -->

        <!-- [Hero Section] 动态欢迎语区 -->
        <!-- 3. 核心代码强调：根据登录状态动态切换标题与副标题，提升用户归属感 -->
        <div class="text-center mb-10 animate-fade-in-down">
          <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-slate-200 text-slate-600 text-xs font-bold uppercase tracking-wide mb-6 shadow-sm">
            <Zap :size="14" class="fill-indigo-500 text-indigo-500" /> ZyCloud Core v2.4
          </div>
          <h1 class="text-4xl md:text-6xl font-extrabold mb-4 tracking-tight transition-all duration-500">
            <span 
              :class="isGradientTitle 
                ? 'text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 animate-fade-in' 
                : 'text-slate-900'"
            >
              {{ pageTitle }}
            </span>
          </h1>
          <p class="text-lg text-slate-500 max-w-2xl mx-auto animate-fade-in transition-all duration-500">
            {{ pageSubtitle }}
          </p>
        </div>

        <!-- [Context Selection Card] 业务场景选择区 -->
        <div class="bg-white rounded-3xl shadow-xl border border-slate-100 p-8 md:p-10 backdrop-blur-sm bg-white/90 animate-fade-in-up">
          
          <!-- [Step 1] 学段选择 -->
          <div class="mb-8">
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs">1</span>
              选择学段 (Level)
            </h3>
            <div class="flex gap-4">
              <button 
                @click="setLevel('初中')"
                class="flex-1 relative p-4 rounded-xl border-2 transition-all flex items-center justify-center gap-3 group"
                :class="level === '初中' ? 'border-indigo-600 bg-indigo-50/50' : 'border-slate-100 hover:border-indigo-200 hover:bg-slate-50'"
              >
                <div 
                  class="w-10 h-10 rounded-lg flex items-center justify-center transition-colors"
                  :class="level === '初中' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-400 group-hover:text-indigo-600'"
                >
                  <School :size="20" />
                </div>
                <span class="font-bold text-lg" :class="level === '初中' ? 'text-indigo-900' : 'text-slate-600'">初中 (Middle)</span>
                <div v-if="level === '初中'" class="absolute top-2 right-2 text-indigo-600">
                  <div class="w-2 h-2 rounded-full bg-indigo-600"></div>
                </div>
              </button>

              <button 
                @click="setLevel('高中')"
                class="flex-1 relative p-4 rounded-xl border-2 transition-all flex items-center justify-center gap-3 group"
                :class="level === '高中' ? 'border-indigo-600 bg-indigo-50/50' : 'border-slate-100 hover:border-indigo-200 hover:bg-slate-50'"
              >
                <div 
                  class="w-10 h-10 rounded-lg flex items-center justify-center transition-colors"
                  :class="level === '高中' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-400 group-hover:text-indigo-600'"
                >
                  <GraduationCap :size="20" />
                </div>
                <span class="font-bold text-lg" :class="level === '高中' ? 'text-indigo-900' : 'text-slate-600'">高中 (High)</span>
                <div v-if="level === '高中'" class="absolute top-2 right-2 text-indigo-600">
                  <div class="w-2 h-2 rounded-full bg-indigo-600"></div>
                </div>
              </button>
            </div>
          </div>

          <!-- [Step 2] 学科选择 -->
          <!-- 3. 核心代码强调：根据 Step 1 的学段动态过滤学科网格内容 -->
          <div class="mb-10">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <span class="w-5 h-5 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs">2</span>
                选择{{ level }}学科 (Subject)
              </h3>
              <span v-if="subject" class="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded">已选: {{ subject }}</span>
            </div>
            
            <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-4 gap-3">
              <button 
                v-for="sub in currentSubjects"
                :key="sub.id"
                @click="setSubject(sub.name)"
                class="p-4 rounded-xl border-2 transition-all flex flex-col items-center gap-3"
                :class="subject === sub.name ? 'border-indigo-600 bg-indigo-50/50 shadow-md transform scale-[1.02]' : 'border-slate-50 bg-slate-50/50 hover:bg-white hover:border-indigo-200'"
              >
                <div 
                  class="w-10 h-10 rounded-full flex items-center justify-center"
                  :class="[sub.bg, sub.color]"
                >
                  <component :is="sub.icon" :size="20" />
                </div>
                <span class="text-sm font-bold" :class="subject === sub.name ? 'text-indigo-900' : 'text-slate-600'">{{ sub.name }}</span>
              </button>
            </div>
          </div>

          <!-- [Action] 入口动作按钮 -->
          <button 
            @click="handleEnter"
            :disabled="!level || !subject"
            class="w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-lg"
            :class="level && subject ? 'bg-indigo-600 text-white hover:bg-indigo-700 hover:scale-[1.01] shadow-indigo-500/30' : 'bg-slate-200 text-slate-400 cursor-not-allowed'"
          >
            {{ buttonText }} <ArrowRight :size="20" />
          </button>

        </div>

        <!-- [Global Resources] 全局工具入口区 -->
        <div class="mt-12 animate-fade-in-up" style="animation-delay: 100ms">
          <h3 class="text-center text-xs font-bold text-slate-400 uppercase tracking-widest mb-6">Global System Resources</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <button 
              @click="onNavigate('DOCS')"
              class="flex items-center gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-300 transition-all group text-left"
            >
              <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                <BookOpen :size="24" />
              </div>
              <div>
                <div class="font-bold text-slate-700 group-hover:text-blue-700">使用文档</div>
                <div class="text-xs text-slate-400">Docs & Specs</div>
              </div>
            </button>

            <button
              @click="onNavigate('SHOWCASE')"
              class="flex items-center gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-purple-300 transition-all group text-left"
            >
              <div class="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                <FlaskConical :size="24" />
              </div>
              <div>
                <div class="font-bold text-slate-700 group-hover:text-purple-700">组件工坊</div>
                <div class="text-xs text-slate-400">Showcase Hub</div>
              </div>
            </button>

            <button 
              @click="onNavigate('DB_EXPLORER')"
              class="flex items-center gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-slate-400 transition-all group text-left"
            >
              <div class="w-12 h-12 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                <HardDrive :size="24" />
              </div>
              <div>
                <div class="font-bold text-slate-700 group-hover:text-slate-900">底层数据管理</div>
                <div class="text-xs text-slate-400">DB Admin</div>
              </div>
            </button>
          </div>
        </div>
        
        <!-- [Footer Info] 版权标识 -->
        <div class="mt-8 flex items-center justify-center gap-4 text-slate-400 text-xs font-mono">
          <span>ZyCloud Core System v2.4 • Powered by Vue 3.4</span>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：ref, computed, watch (响应式编程)
 * - 路由跳转：useRouter
 * - 状态管理：useContextStore (用于初始化业务上下文), useUserStore (鉴权与用户信息)
 * - 图标库：lucide-vue-next (Lucide 图标集)
 */
import { ref, computed, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useContextStore } from '@/stores/context';
import { useUserStore } from '@/stores/user';

import {
  BookOpen, ArrowRight, Zap, GraduationCap, School, Atom, Calculator,
  Languages, FlaskConical, Globe, Dna, Feather, Hammer, HardDrive
} from 'lucide-vue-next';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 状态与 Store 初始化 ---
const router = useRouter();
const contextStore = useContextStore();
const userStore = useUserStore();

// --- 类型定义 ---
type Level = '初中' | '高中';

interface SubjectConfig {
  name: string;
  icon: any;
  color: string;
  bg: string;
}

// --- 3. 核心代码强调：学科字典配置 (The Subject Dictionary) ---
// 该字典定义了全站支持的所有学科及其对应的 UI 表现形式
const SUBJECT_CONFIG: Record<string, SubjectConfig> = {
  chinese: { name: '语文', icon: Feather, color: 'text-red-600', bg: 'bg-red-100' },
  math: { name: '数学', icon: Calculator, color: 'text-blue-600', bg: 'bg-blue-100' },
  english: { name: '英语', icon: Languages, color: 'text-orange-600', bg: 'bg-orange-100' },
  physics: { name: '物理', icon: Atom, color: 'text-purple-600', bg: 'bg-purple-100' },
  chemistry: { name: '化学', icon: FlaskConical, color: 'text-emerald-600', bg: 'bg-emerald-100' },
  biology: { name: '生物', icon: Dna, color: 'text-rose-600', bg: 'bg-rose-100' },
  geography: { name: '地理', icon: Globe, color: 'text-cyan-600', bg: 'bg-cyan-100' },
  politics: { name: '道德与法治', icon: School, color: 'text-pink-600', bg: 'bg-pink-100' },
  technology: { name: '通用技术', icon: Hammer, color: 'text-slate-600', bg: 'bg-slate-100' },
};

// --- 3. 核心代码强调：学段学科映射逻辑 ---
// 用于过滤各学段下可见的学科列表
const LEVEL_MAP: Record<Level, string[]> = {
  '初中': ['chinese', 'math', 'english', 'physics', 'chemistry', 'biology', 'geography', 'politics'],
  '高中': ['chinese', 'math', 'english', 'physics', 'chemistry', 'biology', 'geography', 'technology']
};

// --- 局部响应式变量 ---
const level = ref<Level>('初中');
const subject = ref<string | null>(null);

// --- 动态计算属性区 ---
const currentSubjects = computed(() => {
  return LEVEL_MAP[level.value].map(key => ({
    id: key,
    ...SUBJECT_CONFIG[key]
  }));
});

// 动态标题文本
const pageTitle = computed(() => {
  if (userStore.isLoggedIn && userStore.currentUser) {
    return `欢迎回来，${userStore.currentUser.name}`;
  }
  return '智研题库协作云';
});

// 动态副标题文本
const pageSubtitle = computed(() => {
  if (userStore.isLoggedIn && userStore.currentUser) {
    return '您的工作台已准备就绪，请确认学科环境。';
  }
  return '请选择教研场景以初始化工作台环境';
});

// 按钮文案
const buttonText = computed(() => {
  if (userStore.isLoggedIn && userStore.currentUser) {
    return `进入 ${userStore.currentUser.name} 的工作台`;
  }
  return '进入智能化教研平台';
});

// 标题样式控制
const isGradientTitle = computed(() => {
  return userStore.isLoggedIn && userStore.currentUser !== null;
});

// --- 交互方法区 ---
const setLevel = (newLevel: Level) => {
  level.value = newLevel;
  subject.value = null; // 重置学科，强制重新选择
};

const setSubject = (newSubject: string) => {
  subject.value = newSubject;
};

// --- 3. 核心代码强调：上下文环境初始化 (Context Setup) ---
// 用户点击进入时，将选中的学段学科同步至全局 Store 与 LocalStorage
const handleEnter = async () => {
  if (level.value && subject.value) {
    console.log(`Entering system with: ${level.value} - ${subject.value}`);
    contextStore.setContext(level.value === '初中' ? 'junior' : 'senior', subject.value);

    // 强制等待 Vue 响应式更新与存储操作完成，确保后续页面加载时 context 已就绪
    await nextTick();
    await new Promise(resolve => setTimeout(resolve, 50));

    if (contextStore.grade && contextStore.subject) {
      router.push('/home');
    } else {
      console.error('Context setup failed, cannot navigate');
    }
  }
};

// 外部工具导航
const onNavigate = (view: string) => {
  if (view === 'LAB') {
    router.push('/lab');
  } else if (view === 'SHOWCASE') {
    router.push('/showcase');
  } else if (view === 'DOCS') {
    console.warn('DOCS module not implemented');
  } else if (view === 'DB_EXPLORER') {
    console.warn('DB_EXPLORER module not implemented');
  }
};

// --- 3. 核心代码强调：登录后的自动预选逻辑 (Auto-Selection Watcher) ---
// 根据用户的教研背景信息，自动预填学段和学科，减少用户操作次数
watch(() => userStore.isLoggedIn, (isLoggedIn) => {
  if (isLoggedIn && userStore.currentUser) {
    const user = userStore.currentUser;
    if (user.role === 'admin') return; // 管理员保持手动选择
    
    if (user.level) {
      const newLevel = user.level === 'junior' ? '初中' : '高中';
      level.value = newLevel as Level;
    }
    
    if (user.subject && user.subject !== 'placeholder') {
      const subjectConfig = SUBJECT_CONFIG[user.subject];
      if (subjectConfig) {
        subject.value = subjectConfig.name;
      }
    }
  }
}, { immediate: true });
</script>


<style scoped>
/* 淡入动画 */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}

/* 渐变色动画效果（可选） */
@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradient-shift 3s ease infinite;
}
</style>
