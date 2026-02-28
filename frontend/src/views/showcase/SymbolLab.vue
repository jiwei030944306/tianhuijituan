<!--
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 符号实验室 (SymbolLab.vue)
  本页面作为 LaTeX 公式渲染测试工具，提供从基础代数到复杂结构的全字符集压力测试与速查手册。
-->
<template>
  <div class="absolute top-16 left-0 right-0 bottom-0 bg-slate-50 overflow-y-auto">
    <div class="max-w-7xl mx-auto px-6 py-10">

      <!-- [Header Section] 页面标题与说明 -->
      <div class="flex items-center gap-4 mb-10">
         <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 text-white flex items-center justify-center shadow-lg shadow-indigo-200">
           <FlaskConical :size="32" />
         </div>
         <div>
           <h1 class="text-3xl font-extrabold text-slate-800">符号实验室 (Symbol Lab)</h1>
           <p class="text-slate-500 mt-1 flex items-center gap-2">
              <Sigma :size="16" /> KaTeX 渲染引擎全字符集压力测试与速查手册
           </p>
         </div>
</div>

      <div class="space-y-8 pb-20">
          <!-- [Intro Alert] 使用说明提示框 -->
          <div class="bg-indigo-50 border border-indigo-100 rounded-xl p-4 flex items-start gap-3">
              <TestTube class="text-indigo-600 shrink-0 mt-0.5" :size="20" />
              <div class="text-sm text-indigo-900 leading-relaxed">
                  本实验室用于测试系统对各类数学公式的渲染兼容性。点击任意卡片下方的代码即可复制 LaTeX 源码。
                  <br/>
                  <strong>提示：</strong>在题目编辑框中输入 <code>$$公式$$</code> 可启用块级公式渲染。
              </div>
</div>

          <!-- [Symbol Cards Grid] 符号卡片展示区（2列布局） -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <LatexCard 
                  title="基础代数 (Algebra)" 
                  :items="[
                      'x^2', '\\sqrt{x}', '\\sqrt[3]{x}', 
                      '\\frac{a}{b}', '\\pm 5', '\\times', 
                      '\\div', '\\neq', '\\approx',
                      '\\infty', '\\cdot', 'x^{-1}',
                      '|x|', 'n!', '\\log_a b'
                  ]" 
              />

              <LatexCard 
                  title="希腊字母 (Greek Letters)" 
                  :items="[
                      '\\alpha', '\\beta', '\\gamma', 
                      '\\theta', '\\lambda', '\\pi', 
                      '\\Delta', '\\Omega', '\\phi', 
                      '\\epsilon', '\\sigma', '\\mu',
                      '\\rho', '\\tau', '\\psi'
                  ]" 
              />

              <LatexCard 
                  title="微积分 (Calculus)" 
                  :items="[
                      '\\int_a^b', '\\sum_{i=1}^n', '\\lim_{x\\to\\infty}', 
                      '\\frac{dy}{dx}', '\\partial x', '\\oint_C', 
                      '\\prod', '\\nabla', 'f\'(x)',
                      '\\iint', '\\to', 'dx'
                  ]" 
              />

              <LatexCard 
                  title="集合与逻辑 (Sets & Logic)" 
                  :items="[
                      '\\in', '\\notin', '\\subset', 
                      '\\cup', '\\cap', '\\forall', 
                      '\\exists', '\\therefore', '\\because',
                      '\\mathbb{R}', '\\mathbb{Z}', '\\emptyset',
                      '\\subseteq', '\\setminus', '\\implies'
                  ]" 
              />
          </div>

          <LatexCard 
              title="几何与箭头 (Geometry & Arrows)" 
              :items="[
                  '\\angle ABC', '\\triangle', '\\perp', 
                  '\\parallel', '\\circ', '\\rightarrow', 
                  '\\Rightarrow', '\\iff', '\\vec{a}',
                  '\\leftrightarrow', '\\updownarrow', '\\mapsto',
                  '\\sim', '\\cong', '30^\\circ'
              ]" 
/>

          <!-- [Advanced Block Math Test] 复杂结构压力测试（矩阵、分段函数、复杂方程） -->
          <div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
              <div class="bg-slate-50 px-4 py-2 border-b border-slate-100 font-bold text-slate-700 text-xs uppercase tracking-wider flex items-center gap-2">
                  <Braces :size="14"/> 复杂结构压力测试 (Complex Structures)
              </div>
              <div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                      <div class="text-xs text-slate-400 mb-3 font-bold uppercase">矩阵 (Matrices)</div>
                      <div class="p-6 bg-slate-50 rounded-xl border border-slate-100 text-center hover:bg-white hover:border-indigo-200 transition-all flex items-center justify-center min-h-[120px]">
                          <MathText text="$$ \begin{pmatrix} a & b \\ c & d \end{pmatrix} \times \begin{bmatrix} 1 \\ 0 \end{bmatrix} $$" />
                      </div>
                  </div>
                  <div>
                      <div class="text-xs text-slate-400 mb-3 font-bold uppercase">分段函数 (Cases)</div>
                      <div class="p-6 bg-slate-50 rounded-xl border border-slate-100 text-center hover:bg-white hover:border-indigo-200 transition-all flex items-center justify-center min-h-[120px]">
                          <MathText text="$$ f(x) = \begin{cases} x^2 & x > 0 \\ -x & x \le 0 \end{cases} $$" />
                      </div>
                  </div>
                  <div>
                      <div class="text-xs text-slate-400 mb-3 font-bold uppercase">复杂方程 (Quadratic)</div>
                      <div class="p-6 bg-slate-50 rounded-xl border border-slate-100 text-center hover:bg-white hover:border-indigo-200 transition-all flex items-center justify-center min-h-[120px]">
                          <MathText text="$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$" />
                      </div>
                  </div>
              </div>
          </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 4. 引用挂载说明
 * - 图标库：lucide-vue-next（UI 图标组件）
 * - 数学公式渲染：MathText.vue（KaTeX 渲染组件）
 * - LaTeX 卡片：LatexCard.vue（可复用的符号展示卡片组件）
 */
import {
  Sigma, FlaskConical, TestTube, Braces
} from 'lucide-vue-next';
import MathText from '@/components/common/MathText.vue';
import LatexCard from '@/components/LatexCard.vue';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 组件引入模块 ---
// 本页面为纯展示型组件，无需额外的业务逻辑处理
// 所有数据直接在模板中通过 props 传递给子组件
</script>
