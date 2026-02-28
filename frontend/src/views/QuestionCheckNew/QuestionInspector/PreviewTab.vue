<script setup lang="ts">
/**
 * 题目预览标签页组件
 *
 * 功能：
 * - 纯粹的从上到下的数据展示
 * - 按字段分组渲染，清晰直观
 * - 方便与 JSON 数据进行对比
 *
 * @component PreviewTab
 */

import { computed } from 'vue';
import type { Question } from '@/types/question';
import FieldGroup from '@/components/QuestionInspector/FieldGroup.vue';
import { QUESTION_FIELDS } from '@/components/QuestionInspector/FieldConfigs';
import { getSortedGroups } from '@/components/QuestionInspector/FieldConfig';

// ==================== Props 定义 ====================

interface Props {
  question: Question;  // 题目数据
}

const props = defineProps<Props>();

// ==================== 计算属性 ====================

/**
 * 获取排序后的分组列表
 */
const sortedGroups = computed(() => {
  return getSortedGroups(QUESTION_FIELDS);
});

</script>

<template>
  <div class="bg-slate-50 p-6 animate-fade-in">
    <div class="max-w-4xl mx-auto space-y-6">

      <!-- 遍历所有分组，按顺序从上到下展示 -->
      <template v-for="group in sortedGroups" :key="group.id">
        <div class="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
          <!-- 分组标题 -->
          <div
            class="px-4 py-3 border-b border-slate-100 flex items-center gap-2"
            :class="group.style?.bgColor || 'bg-slate-50'"
          >
            <component
              v-if="group.icon"
              :is="group.icon"
              :size="16"
              :class="group.style?.labelColor"
            />
            <span class="font-bold text-sm text-slate-700">{{ group.title }}</span>
            <span class="text-xs text-slate-400 font-mono ml-auto opacity-60">group: {{ group.id }}</span>
          </div>

          <!-- 分组内容 -->
          <div class="p-4">
            <FieldGroup
              :group="group.id"
              :fields="QUESTION_FIELDS"
              :question="question"
              :all-fields="QUESTION_FIELDS"
            />
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.2s ease-out;
}
</style>
