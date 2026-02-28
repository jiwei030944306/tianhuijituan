<!-- 
  1. 页面简介 (Page Introduction)
  LaTeX 公式渲染组件 (MathText.vue)
  本组件负责将包含 LaTeX 语法的文本渲染为数学公式，使用 KaTeX 库进行解析和渲染。
  支持混合文本和公式的场景，自动识别 LaTeX 语法并渲染。
-->

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - KaTeX: katex (LaTeX 公式渲染引擎)
 * - Vue 核心：computed, watch (响应式渲染)
 */
import { computed, watch, ref, onMounted } from 'vue';
import katex from 'katex';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- Props 定义 ---
interface MathTextProps {
  text: string;  // 包含 LaTeX 语法的文本
  displayMode?: 'inline' | 'block';  // 显示模式（行内/块级）
  fontSize?: string;  // 字体大小
  color?: string;  // 字体颜色
}

const props = withDefaults(defineProps<MathTextProps>(), {
  displayMode: 'inline',
  fontSize: 'text-sm',
  color: 'text-slate-800'
});

// --- 3. 核心代码强调：LaTeX 解析逻辑 ---
// 使用正则表达式识别 LaTeX 公式（$...$ 或 $$...$$），并分别渲染
const renderedHtml = computed(() => {
  if (!props.text) return '';

  // 匹配块级公式 $$...$$
  const blockPattern = /\$\$([^$]+)\$\$/g;
  // 匹配行内公式 $...$
  const inlinePattern = /\$([^$]+)\$/g;

  let result = props.text;

  // 先处理块级公式 $$...$$ → 居中显示
  const blockMatches = [...result.matchAll(blockPattern)];
  blockMatches.forEach((match) => {
    const [fullMatch, content] = match;
    const html = katex.renderToString(content, {
      displayMode: true,  // 块级公式：居中独占一行
      throwOnError: false
    });
    result = result.replace(fullMatch, html);
  });

  // 再处理行内公式 $...$ → 与文字混排
  const inlineMatches = [...result.matchAll(inlinePattern)];
  inlineMatches.forEach((match) => {
    const [fullMatch, content] = match;
    const html = katex.renderToString(content, {
      displayMode: false,  // 行内公式：与文字同行
      throwOnError: false
    });
    result = result.replace(fullMatch, html);
  });

  // 处理换行符：将 \n 转换为 <br> 标签
  result = result.replace(/\n/g, '<br>');

  return result;
});
</script>

<template>
  <!-- ==========================================
       2. 主要功能代码分区注释 - 页面渲染区
       ========================================== -->

  <!-- [MathText Container] 公式渲染容器 -->
  <span
    :class="[
      props.fontSize,
      props.color,
      props.displayMode === 'block' ? 'block my-2' : 'inline'
    ]"
    v-html="renderedHtml"
  />
</template>

<style scoped>
/* KaTeX 样式覆盖 */
span .katex {
  font-size: 1em;
}
</style>