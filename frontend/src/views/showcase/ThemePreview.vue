<!--
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 主题预览 (ThemePreview.vue)
  本页面作为 ZyCloud 设计系统的展示中心，提供色彩系统、排版规范、通用组件和业务组件的预览与参考。
-->
<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <!-- [Header Section] 顶部导航栏 -->
    <div class="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between shrink-0 sticky top-0 z-20 shadow-sm">
      <div class="flex items-center gap-4">
        <button @click="$router.back()" class="p-2 rounded-lg hover:bg-slate-50 text-slate-500 transition-colors">
          <ArrowLeft :size="20" />
        </button>
        <div>
          <h1 class="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Palette :size="20" class="text-indigo-600" />
            ZyCloud 设计系统
          </h1>
          <p class="text-xs text-slate-400 font-mono">v2.4 • System Guidelines</p>
        </div>
      </div>

      <!-- [Tabs] 标签页切换器 -->
      <div class="flex bg-slate-100 p-1 rounded-lg">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="currentTab = tab.id"
          :class="[
            'px-6 py-2 text-sm font-medium rounded-md transition-all',
            currentTab === tab.id
              ? 'bg-white text-indigo-600 shadow-sm font-bold'
              : 'text-slate-500 hover:text-slate-700'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- [Content] 内容展示区 -->
    <div class="flex-1 overflow-y-auto p-8">
      <div class="max-w-6xl mx-auto">

        <!-- [Tab 1: Foundation] 基础风格标签页 -->
        <div v-if="currentTab === 'foundation'" class="space-y-16 animate-fade-in">

          <!-- Colors 色彩系统 -->
          <section>
            <SectionTitle title="色彩系统" subtitle="Color Palette" />

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <ColorGroup
                title="主品牌色 (Primary) - 靛蓝"
                color="indigo"
                :shades="[50, 100, 500, 600, 900]"
                :hexs="['#eef2ff', '#e0e7ff', '#6366f1', '#4f46e5', '#312e81']"
              />
              <ColorGroup
                title="成功/上传 (Success) - 绿色"
                color="green"
                :shades="[50, 100, 500, 600]"
                :hexs="['#f0fdf4', '#dcfce7', '#22c55e', '#16a34a']"
              />
              <ColorGroup
                title="信息/检视 (Info) - 蓝色"
                color="blue"
                :shades="[50, 100, 500, 600]"
                :hexs="['#eff6ff', '#dbeafe', '#3b82f6', '#2563eb']"
              />
              <ColorGroup
                title="中性色 (Neutral) - 灰蓝"
                color="slate"
                :shades="[50, 100, 200, 500, 900]"
                :hexs="['#f8fafc', '#f1f5f9', '#e2e8f0', '#64748b', '#0f172a']"
              />
            </div>
          </section>

          <!-- Typography 排版规范 -->
          <section class="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div>
              <SectionTitle title="排版规范" subtitle="Typography" />
              <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-8">
                <div class="space-y-1">
                  <div class="text-4xl font-extrabold text-slate-900">大标题 H1</div>
                  <code class="text-xs text-slate-400">text-4xl font-extrabold text-slate-900</code>
                </div>
                <div class="space-y-1">
                  <div class="text-2xl font-bold text-slate-800">模块标题 H2</div>
                  <code class="text-xs text-slate-400">text-2xl font-bold text-slate-800</code>
                </div>
                <div class="space-y-1">
                  <div class="text-lg font-bold text-slate-800">卡片标题 H3</div>
                  <code class="text-xs text-slate-400">text-lg font-bold text-slate-800</code>
                </div>
                <div class="space-y-1">
                  <div class="text-base font-medium text-slate-700">小标题 H4</div>
                  <code class="text-xs text-slate-400">text-base font-medium text-slate-700</code>
                </div>
                <div class="space-y-1">
                  <p class="text-base text-slate-600 leading-relaxed">
                    这是正文文本 (Body)。ZyCloud 使用系统默认字体栈，确保在各平台上的原生体验。
                    正文颜色通常使用 text-slate-600，行高 leading-relaxed 以保证阅读舒适度。
                  </p>
                  <code class="text-xs text-slate-400">text-base text-slate-600 leading-relaxed</code>
                </div>
                <div class="space-y-1">
                  <p class="text-xs text-slate-400 uppercase tracking-wider font-bold">Caption Label</p>
                  <code class="text-xs text-slate-400">text-xs text-slate-400 uppercase tracking-wider font-bold</code>
                </div>
              </div>
            </div>

            <!-- Radius & Shadows 圆角与阴影 -->
            <div>
              <SectionTitle title="圆角与阴影" subtitle="Radius & Shadows" />
              <div class="grid grid-cols-2 gap-6">
                <div class="aspect-video bg-white rounded-md border border-slate-200 shadow-sm flex flex-col items-center justify-center gap-2 p-4 text-center hover:shadow-md transition-shadow">
                  <span class="text-sm font-bold text-slate-700">小圆角 (Small)</span>
                  <code class="text-xs text-slate-400">rounded-md<br>shadow-sm</code>
                </div>
                <div class="aspect-video bg-white rounded-lg border border-slate-200 shadow flex flex-col items-center justify-center gap-2 p-4 text-center hover:shadow-md transition-shadow">
                  <span class="text-sm font-bold text-slate-700">中圆角 (Medium)</span>
                  <code class="text-xs text-slate-400">rounded-lg<br>shadow</code>
                </div>
                <div class="aspect-video bg-white rounded-xl border border-slate-200 shadow-md flex flex-col items-center justify-center gap-2 p-4 text-center hover:shadow-lg transition-shadow">
                  <span class="text-sm font-bold text-slate-700">大圆角 (Large)</span>
                  <code class="text-xs text-slate-400">rounded-xl<br>shadow-md</code>
                </div>
                <div class="aspect-video bg-white rounded-2xl border border-slate-200 shadow-lg flex flex-col items-center justify-center gap-2 p-4 text-center hover:shadow-xl transition-shadow">
                  <span class="text-sm font-bold text-slate-700">超大圆角 (Extra Large)</span>
                  <code class="text-xs text-slate-400">rounded-2xl<br>shadow-lg</code>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- [Tab 2: Components] 通用组件标签页 -->
        <div v-else-if="currentTab === 'components'" class="space-y-16 animate-fade-in">

          <!-- Buttons 按钮组件 -->
          <section>
            <SectionTitle title="按钮" subtitle="Buttons" />
            <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-8">
              <!-- Variants -->
              <div class="space-y-4">
                <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider">样式变体</h3>
                <div class="flex flex-wrap gap-4 items-center">
                  <button class="px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors shadow-sm font-medium text-sm">
                    主要按钮
                  </button>
                  <button class="px-5 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors shadow-sm font-medium text-sm flex items-center gap-2">
                    <Check :size="16" /> 成功按钮
                  </button>
                  <button class="px-5 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors shadow-sm font-medium text-sm">
                    描边按钮
                  </button>
                  <button class="px-5 py-2.5 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors font-medium text-sm">
                    轻柔按钮
                  </button>
                  <button class="px-5 py-2.5 bg-white text-slate-500 hover:text-slate-700 rounded-lg transition-colors font-medium text-sm">
                    幽灵按钮
                  </button>
                </div>
              </div>

              <!-- States -->
              <div class="space-y-4">
                <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider">状态</h3>
                <div class="flex flex-wrap gap-4 items-center">
                  <button class="px-5 py-2.5 bg-indigo-600 text-white rounded-lg opacity-50 cursor-not-allowed font-medium text-sm">
                    禁用状态
                  </button>
                  <button class="px-5 py-2.5 bg-indigo-600 text-white rounded-lg font-medium text-sm flex items-center gap-2 cursor-wait">
                    <Loader2 :size="16" class="animate-spin" />
                    加载中
                  </button>
                </div>
              </div>
            </div>
          </section>

          <!-- Inputs 输入框组件 -->
          <section>
            <SectionTitle title="输入框" subtitle="Inputs" />
            <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="space-y-4">
                <div class="space-y-1.5">
                  <label class="text-sm font-medium text-slate-700">标准输入框</label>
                  <input type="text" placeholder="请输入内容..." class="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm" />
                </div>
                <div class="space-y-1.5">
                  <label class="text-sm font-medium text-slate-700">带图标搜索框</label>
                  <div class="relative">
                    <Search :size="18" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input type="text" placeholder="搜索关键词..." class="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm" />
                  </div>
                </div>
              </div>
              <div class="space-y-4">
                <div class="space-y-1.5">
                  <label class="text-sm font-medium text-slate-700">下拉选择框</label>
                  <select class="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm bg-white">
                    <option>选项 A</option>
                    <option>选项 B</option>
                  </select>
                </div>
                <div class="space-y-1.5">
                  <label class="text-sm font-medium text-slate-700">禁用状态</label>
                  <input type="text" disabled placeholder="不可编辑" class="w-full px-4 py-2.5 border border-slate-200 bg-slate-50 text-slate-400 rounded-lg cursor-not-allowed text-sm" />
                </div>
              </div>
            </div>
          </section>

          <!-- Badges 徽章组件 -->
          <section>
            <SectionTitle title="徽章" subtitle="Badges" />
            <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
              <div class="flex flex-wrap gap-4">
                <span class="px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-bold border border-indigo-100">主要 (Primary)</span>
                <span class="px-2.5 py-1 rounded-full bg-green-50 text-green-700 text-xs font-bold border border-green-100">成功 (Success)</span>
                <span class="px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-bold border border-blue-100">信息 (Info)</span>
                <span class="px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 text-xs font-bold border border-amber-100">警告 (Warning)</span>
                <span class="px-2.5 py-1 rounded-full bg-red-50 text-red-700 text-xs font-bold border border-red-100">错误 (Error)</span>
                <span class="px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200">方形 (Square)</span>
              </div>
            </div>
          </section>
        </div>

        <!-- [Tab 3: Business] 业务组件标签页 -->
        <div v-else class="space-y-16 animate-fade-in">

          <!-- Functional Cards 功能入口卡片 -->
          <section>
            <SectionTitle title="功能入口卡片" subtitle="Entry Cards" />
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <!-- Upload Card -->
              <div class="p-6 bg-white border border-green-200 rounded-xl shadow-sm hover:shadow-md transition-all group cursor-pointer relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                  <Upload :size="80" class="text-green-600" />
                </div>
                <div class="flex items-center gap-3 mb-4">
                  <div class="w-10 h-10 rounded-lg bg-green-50 text-green-600 flex items-center justify-center">
                    <Upload :size="20" />
                  </div>
                  <div>
                    <h4 class="font-bold text-slate-800">上传管理</h4>
                    <span class="text-[10px] bg-green-50 text-green-600 px-2 py-0.5 rounded-full border border-green-100 font-bold">P0</span>
                  </div>
                </div>
                <p class="text-sm text-slate-500 leading-relaxed mb-4">
                  快速上传题目文件（ZIP/JSON），实时查看上传状态与结果。
                </p>
                <div class="flex items-center gap-2 text-xs font-bold text-green-600">
                  <span>进入模块</span>
                  <ArrowRight :size="14" class="group-hover:translate-x-1 transition-transform" />
                </div>
              </div>

              <!-- Check Card -->
              <div class="p-6 bg-white border border-blue-200 rounded-xl shadow-sm hover:shadow-md transition-all group cursor-pointer relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                  <Layout :size="80" class="text-blue-600" />
                </div>
                <div class="flex items-center gap-3 mb-4">
                  <div class="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                    <Layout :size="20" />
                  </div>
                  <div>
                    <h4 class="font-bold text-slate-800">同步工作台</h4>
                    <span class="text-[10px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full border border-blue-100 font-bold">P1</span>
                  </div>
                </div>
                <p class="text-sm text-slate-500 leading-relaxed mb-4">
                  管理已上传试题批次，进行内容检视、格式校验与质量同步。
                </p>
                <div class="flex items-center gap-2 text-xs font-bold text-blue-600">
                  <span>进入模块</span>
                  <ArrowRight :size="14" class="group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </div>
          </section>

          <!-- Stats Cards 统计卡片 -->
          <section>
            <SectionTitle title="统计卡片" subtitle="Stats Cards" />
            <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <!-- Total -->
                <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex items-center justify-between">
                  <div>
                    <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1 flex items-center gap-2">
                      <LayoutDashboard :size="12"/> 总题量
                    </div>
                    <div class="text-3xl font-black text-slate-800 tracking-tight">
                      2,048 <span class="text-sm font-normal text-slate-400">题</span>
                    </div>
                  </div>
                  <div class="w-12 h-12 rounded-full bg-green-50 text-green-500 flex items-center justify-center">
                    <PieChart :size="24"/>
                  </div>
                </div>

                <!-- Distribution -->
                <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-center gap-2">
                  <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">题型分布</div>
                  <div class="flex items-center gap-2 h-full">
                    <div class="flex-1 flex flex-col items-center p-2 bg-blue-50 rounded-md border border-blue-100">
                      <span class="text-blue-700 font-bold text-lg">80%</span>
                      <span class="text-[10px] text-blue-400">单选</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center p-2 bg-purple-50 rounded-md border border-purple-100">
                      <span class="text-purple-700 font-bold text-lg">20%</span>
                      <span class="text-[10px] text-purple-400">解答</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Question List Item 题目列表项 -->
          <section>
            <SectionTitle title="题目列表项" subtitle="List Item" />
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <table class="w-full text-left border-collapse">
                <thead class="bg-slate-50 text-xs font-bold text-slate-600 uppercase border-b border-slate-200">
                  <tr>
                    <th class="px-4 py-3 w-20">题型</th>
                    <th class="px-4 py-3">题干预览</th>
                    <th class="px-4 py-3 w-32 text-center">状态</th>
                    <th class="px-4 py-3 w-16"></th>
                  </tr>
                </thead>
                <tbody class="text-sm">
                  <tr class="group hover:bg-slate-50 cursor-pointer border-b border-slate-100">
                    <td class="px-4 py-3 font-bold text-blue-600">单选</td>
                    <td class="px-4 py-3 text-slate-700 font-medium truncate max-w-xs">
                      若函数 $f(x) = x^2 + 2x + 1$，则 $f(1)$ 的值为...
                    </td>
                    <td class="px-4 py-3 text-center">
                      <span class="px-2 py-0.5 rounded-full bg-green-50 text-green-700 text-xs font-bold border border-green-100">已入库</span>
                    </td>
                    <td class="px-4 py-3 text-center text-slate-300 group-hover:text-indigo-600">
                      <MoreHorizontal :size="16" />
                    </td>
                  </tr>
                  <tr class="group hover:bg-slate-50 cursor-pointer">
                    <td class="px-4 py-3 font-bold text-purple-600">解答</td>
                    <td class="px-4 py-3 text-slate-700 font-medium truncate max-w-xs">
                      如图，在 $\triangle ABC$ 中，$\angle C = 90^\circ$，求证...
                    </td>
                    <td class="px-4 py-3 text-center">
                      <span class="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-xs font-bold border border-amber-100">待审核</span>
                    </td>
                    <td class="px-4 py-3 text-center text-slate-300 group-hover:text-indigo-600">
                      <MoreHorizontal :size="16" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 4. 引用挂载说明
 * - 响应式：ref（Vue 3 响应式状态管理）
 * - 图标库：lucide-vue-next（UI 图标组件）
 * - 组件定义：defineComponent, h（Vue 3 内联组件定义）
 */
import { ref } from 'vue';
import {
  Palette, ArrowLeft, ArrowRight, Check, Search, Upload, Layout,
  LayoutDashboard, PieChart, MoreHorizontal, Loader2
} from 'lucide-vue-next';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 内联组件定义模块 ---

// 3. 核心代码强调：SectionTitle 组件
// 使用 defineComponent 动态创建章节标题组件，避免创建额外的 .vue 文件
import { defineComponent, h } from 'vue';

const SectionTitleComponent = defineComponent({
  props: ['title', 'subtitle'],
  render() {
    return h('div', { class: 'mb-8 flex items-end gap-3 border-b border-slate-100 pb-3' }, [
      h('h2', { class: 'text-2xl font-bold text-slate-800' }, this.title),
      h('span', { class: 'text-sm font-mono text-slate-400 uppercase tracking-wide mb-1' }, this.subtitle)
    ]);
  }
});

// 3. 核心代码强调：ColorGroup 组件
// 动态渲染色彩色板组件，支持不同色系和色阶的展示
// 使用 hexs prop 确保 Tailwind 动态类名安全（避免被 purge）
const ColorGroupComponent = defineComponent({
  props: ['title', 'color', 'shades', 'hexs'],
  render() {
    return h('div', { class: 'space-y-4' }, [
      h('h3', { class: 'font-bold text-slate-700 text-sm uppercase tracking-wide' }, this.title),
      h('div', { class: 'space-y-2' }, this.shades.map((shade: number, idx: number) => {
        const isLight = shade <= 100;
        const textColor = isLight ? `text-${this.color}-900` : 'text-white';
        // Tailwind safe list needed or dynamic style. Using style for bg to ensure it works.
        // But for preview consistency we use classes if possible.
        // Note: Dynamic classes like `bg-${color}-${shade}` might be purged by Tailwind.
        // So we use style for bg color in this specific dynamic component or safelist.
        // For this demo, let's use the hexs prop for background style to be safe.

        return h('div', {
          class: `h-12 rounded-lg flex items-center px-4 text-xs font-mono justify-between shadow-sm transition-transform hover:scale-[1.02] ${textColor} ${shade===500 ? 'ring-2 ring-offset-2 ring-'+this.color+'-200' : ''}`,
          style: { backgroundColor: this.hexs[idx] }
        }, [
          h('span', { class: 'font-bold text-sm' }, shade),
          h('span', { class: 'opacity-90' }, this.hexs[idx])
        ]);
      }))
    ]);
  }
});

// --- 状态管理模块 ---

// 3. 核心代码强调：标签页切换状态
// 当前激活的标签页 ID，用于控制三个主要区域的显示与隐藏
const currentTab = ref('foundation');

// 3. 核心代码强调：标签页配置
// 定义三个主要标签页：基础风格、通用组件、业务组件
const tabs = [
  { id: 'foundation', label: '基础风格' },
  { id: 'components', label: '通用组件' },
  { id: 'business', label: '业务组件' }
];
</script>

<style scoped>
/* 5. 样式定义 */
/* 淡入动画：用于标签页切换时的平滑过渡效果 */
.animate-fade-in {
  animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
