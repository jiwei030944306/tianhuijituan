/**
 * 字段展示组件
 *
 * @description 通用的字段渲染组件，根据 FieldConfig 配置渲染不同类型的字段
 */

<script setup lang="ts">
import { computed } from 'vue';
import MathText from '@/components/common/MathText.vue';
import type { FieldConfig, FieldValue, FieldGroupConfig } from './FieldConfig';
import { FIELD_GROUPS } from './FieldConfig';
import { Hash, Star, Clock, Calendar, CheckCircle, Info, Lightbulb } from 'lucide-vue-next';

// ==================== Props 定义 ====================

interface Props {
  config: FieldConfig;
  value: FieldValue;
  question: Record<string, any>;
}

const props = defineProps<Props>();

// ==================== 计算属性 ====================

const groupConfig = computed((): FieldGroupConfig => {
  return FIELD_GROUPS[props.config.group];
});

const displayValue = computed((): string => {
  if (props.config.formatter) {
    return props.config.formatter(props.value);
  }
  if (props.value === null || props.value === undefined) {
    return props.config.emptyText || '-';
  }
  return String(props.value);
});

const isVisible = computed((): boolean => {
  // 如果配置了 condition 函数，则必须满足条件才显示
  if (props.config.condition) {
    return props.config.condition(props.question);
  }
  // 没有配置 condition，则始终显示（即使值为空）
  return true;
});

const renderResult = computed((): any => {
  if (props.config.render) {
    return props.config.render(props.value, props.question);
  }
  return null;
});

// ==================== 工具方法 ====================

const formatDateTime = (dateStr: string | undefined): string => {
  if (!dateStr) return '未知';
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  } catch {
    return dateStr;
  }
};
</script>

<template>
  <template v-if="isVisible">
    <!-- ==================== section: 分组容器 ==================== -->
    <div
      v-if="config.type === 'section'"
      :class="[
        'space-y-3 mb-6 p-4 rounded-lg border',
        groupConfig.style?.bgColor,
        groupConfig.style?.borderColor
      ]"
    >
      <div class="flex items-center gap-2 mb-3">
        <component
          v-if="config.icon"
          :is="config.icon"
          :size="16"
          :class="groupConfig.style?.labelColor"
        />
        <span
          :class="[
            'text-xs font-bold uppercase tracking-wider',
            groupConfig.style?.labelColor
          ]"
        >
          {{ config.label }}
        </span>
      </div>
      <slot :children="config.children" :question="question" />
    </div>

    <!-- ==================== text: 纯文本 ==================== -->
    <div v-else-if="config.type === 'text'" class="text-slate-700">
      {{ displayValue }}
    </div>

    <!-- ==================== badge: 标签样式 ==================== -->
    <span
      v-else-if="config.type === 'badge'"
      :class="[
        'px-2 py-1 border rounded text-xs inline-flex items-center gap-1',
        config.style?.bgColor,
        config.style?.borderColor,
        config.style?.textColor,
        config.style?.className
      ]"
    >
      <span v-if="config.label" class="opacity-70 mr-1 font-normal">{{ config.label }}:</span>
      <span class="font-medium">{{ displayValue }}</span>
    </span>

    <!-- ==================== badge-list: 标签列表 ==================== -->
    <div v-else-if="config.type === 'badge-list'" class="space-y-1">
      <div v-if="config.label" class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{{ config.label }}</div>
      <div class="flex flex-wrap gap-2">
        <template v-if="Array.isArray(value) && value.length > 0">
          <span
            v-for="(item, idx) in value"
            :key="idx"
            :class="[
              'px-2 py-0.5 border rounded text-xs font-medium',
              config.style?.bgColor,
              config.style?.borderColor,
              config.style?.textColor
            ]"
          >
            {{ item }}
          </span>
        </template>
        <span v-else class="text-xs text-slate-300 italic">
          {{ config.emptyText || '无 (None)' }}
        </span>
      </div>
    </div>

    <!-- ==================== date: 日期时间 ==================== -->
    <div v-else-if="config.type === 'date'" class="flex items-center gap-2">
      <span v-if="config.label" class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{{ config.label }}:</span>
      <span class="text-xs text-slate-600">{{ formatDateTime(value as string) }}</span>
    </div>

    <!-- ==================== rich-text: 富文本（支持 LaTeX） ==================== -->
    <div
      v-else-if="config.type === 'rich-text'"
      class="text-sm text-slate-700 leading-relaxed"
      :class="config.key === 'stem' ? 'text-base font-serif' : ''"
    >
      <div v-if="config.label" class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">{{ config.label }}</div>
      <MathText :text="displayValue" />
    </div>

    <!-- ==================== code: 代码块 ==================== -->
    <div
      v-else-if="config.type === 'code'"
      class="space-y-1"
    >
      <div v-if="config.label" class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{{ config.label }}</div>
      <div class="text-xs text-slate-600 font-mono leading-relaxed whitespace-pre-wrap max-h-32 overflow-y-auto bg-slate-50 p-2 rounded border border-slate-200">
        {{ displayValue }}
      </div>
    </div>

    <!-- ==================== status: 状态标识 ==================== -->
    <span
      v-else-if="config.type === 'status' && renderResult"
      :class="[
        'px-2 py-0.5 text-[10px] font-bold rounded-full',
        renderResult.color
      ]"
    >
      {{ renderResult.text }}
    </span>

    <!-- ==================== grid: 网格布局 ==================== -->
    <div v-else-if="config.type === 'grid'" class="grid grid-cols-2 gap-3">
      <div
        v-for="child in config.children"
        :key="child.key"
        class="bg-white p-2 rounded border border-purple-200"
      >
        <span class="text-[10px] text-slate-400 block mb-1">{{ child.label }}</span>
        <div class="text-sm font-bold text-purple-600">
          {{ child.formatter ? child.formatter(question[child.key]) : question[child.key] || '未识别' }}
        </div>
      </div>
    </div>

    <!-- ==================== image: 图片 ==================== -->
    <div
      v-else-if="config.type === 'image' && Array.isArray(value)"
      class="space-y-2"
    >
      <div
        v-for="(img, idx) in value"
        :key="idx"
        class="bg-slate-50 border border-slate-200 rounded p-2 flex flex-col items-center"
      >
        <div class="w-full bg-white rounded mb-2 flex items-center justify-center relative overflow-hidden">
          <img
            :src="img.src"
            :alt="`${config.label} ${idx + 1}`"
            class="max-w-full max-h-48 object-contain"
            @error="(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              target.nextElementSibling?.classList.remove('hidden');
            }"
          />
          <div class="hidden absolute inset-0 flex items-center justify-center text-slate-400 text-xs flex-col bg-slate-100">
            <span class="text-[10px] px-2 text-center">图片加载失败</span>
            <span class="text-[10px] text-slate-400 mt-1 font-mono">{{ img.src }}</span>
          </div>
        </div>
        <span class="text-[10px] text-slate-500 font-mono bg-white px-2 py-0.5 rounded border border-slate-100">
          layout: {{ img.layout || 'default' }}
        </span>
      </div>
    </div>

    <!-- ==================== stem: 题干（特殊样式） ==================== -->
    <div v-else-if="config.type === 'stem'" class="text-base text-slate-800 leading-relaxed mb-6 font-serif">
      <div class="font-bold text-slate-400 uppercase tracking-wider text-xs mb-2">题干 (Stem):</div>
      <MathText :text="value as string" />
    </div>

    <!-- ==================== options: 选项列表 ==================== -->
    <div v-else-if="config.type === 'options' && Array.isArray(value)" class="space-y-3 mb-6">
      <div class="font-bold text-slate-400 uppercase tracking-wider text-xs mb-2">选项 (Options):</div>
      <div
        v-for="opt in value"
        :key="opt.key || opt.label"
        :class="[
          'flex gap-3 text-sm p-3 rounded-lg border transition-colors',
          question.answer?.includes(opt.key || opt.label || '')
            ? 'bg-green-50 border-green-200'
            : 'bg-white border-slate-200 hover:border-indigo-200'
        ]"
      >
        <span
          :class="[
            'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border',
            question.answer?.includes(opt.key || opt.label || '')
              ? 'bg-green-100 border-green-300 text-green-700'
              : 'bg-white border-slate-200 text-slate-400'
          ]"
        >
          {{ opt.key || opt.label }}
        </span>
        <div class="text-slate-700 pt-0.5 flex-1">
          <MathText :text="opt.content" />
          <div v-if="opt.image" class="mt-2">
            <img :src="opt.image" class="max-h-24 object-contain border border-slate-100 rounded" />
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== answer-box: 答案盒子（绿色背景） ==================== -->
    <div v-else-if="config.type === 'answer-box'" class="mt-8 p-4 bg-green-50/30 border border-green-100 rounded-lg text-sm">
      <div class="font-bold text-green-600 uppercase tracking-wider text-xs mb-2">正确答案 (Answer):</div>
      <div class="font-bold text-lg text-slate-800">
        <MathText :text="value as string" />
      </div>
    </div>

    <!-- ==================== analysis-box: 解析盒子（黄色背景） ==================== -->
    <div v-else-if="config.type === 'analysis-box'" class="mt-4 p-4 bg-yellow-50/50 border border-yellow-100 rounded-lg text-sm">
      <div class="font-bold text-yellow-600 uppercase tracking-wider text-xs mb-2 flex items-center gap-1">
        <Lightbulb :size="12" /> 原始解析 (Analysis)
      </div>
      <div class="text-slate-700 leading-relaxed">
        <MathText :text="value as string" />
      </div>
    </div>
  </template>
</template>