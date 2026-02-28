<script setup lang="ts">
/**
 * JSON 源码编辑标签页组件
 *
 * 功能：
 * - 提供可编辑的 JSON 源码视图
 * - 实时验证 JSON 格式有效性
 * - 显示 JSON 语法错误信息
 * - 支持复制和保存修改
 *
 * @component JsonTab
 * @description QuestionInspector 的 JSON 编辑标签页，提供 IDE 风格的代码编辑体验
 */

// ==================== Props 定义 ====================

interface Props {
  code: string;              // JSON 内容字符串
  jsonError: string | null;  // JSON 语法错误信息（若有）
}

const props = defineProps<Props>();

// ==================== Events 定义 ====================

const emit = defineEmits<{
  'update:code': [value: string];  // 更新 code 内容 (v-model:code)
  'save': [];                      // 保存 JSON 修改
}>();

// ==================== 方法 ====================

/**
 * 处理文本框输入事件
 * @param event - 输入事件对象
 */
const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement;
  emit('update:code', target.value);
};
</script>

<template>
  <div class="absolute inset-0 bg-[#1e1e1e] flex flex-col animate-fade-in">
    <!-- 状态栏 -->
    <div class="bg-[#252526] px-4 py-2 text-[10px] text-slate-400 flex justify-between border-b border-[#333] shrink-0">
      <span>编辑源码 (Editable Source)</span>
      <span :class="jsonError ? 'text-red-400' : 'text-green-400'">
        {{ jsonError ? `❌ Invalid JSON: ${jsonError}` : '✅ Valid JSON' }}
      </span>
    </div>

    <!-- 代码编辑器 -->
    <textarea
      :value="code"
      @input="handleInput"
      class="flex-1 w-full bg-transparent text-slate-300 font-mono text-xs p-4 resize-none focus:outline-none leading-relaxed"
      spellcheck="false"
    ></textarea>
  </div>
</template>

<style scoped>
/* 淡入动画 */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 0.2s ease-in;
}
</style>
