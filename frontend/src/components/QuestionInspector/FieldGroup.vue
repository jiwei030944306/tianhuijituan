/**
 * 字段分组展示组件
 *
 * @description 根据 FieldGroupConfig 渲染一个完整的字段分组，包含标题和所有子字段
 * 支持 'default' | 'inline' | 'compact' 三种显示模式
 */

<script setup lang="ts">
import { computed } from 'vue';
import FieldRenderer from './FieldRenderer.vue';
import type { FieldConfig, FieldGroupConfig } from './FieldConfig';
import { FIELD_GROUPS, getFieldsByGroup } from './FieldConfig';

// ==================== Props 定义 ====================

interface Props {
  group: string;  // 分组标识
  fields: FieldConfig[];  // 所有字段配置
  question: Record<string, any>;  // 题目数据
  allFields?: FieldConfig[];  // 用于子字段查找的完整字段列表
  mode?: 'default' | 'inline' | 'compact'; // 新增：显示模式
}

const props = withDefaults(defineProps<Props>(), {
  allFields: () => [],
  mode: 'default'
});

// ==================== 计算属性 ====================

const groupConfig = computed((): FieldGroupConfig | undefined => {
  return FIELD_GROUPS[props.group as keyof typeof FIELD_GROUPS];
});

const groupFields = computed((): FieldConfig[] => {
  return getFieldsByGroup(props.fields, props.group as keyof typeof FIELD_GROUPS);
});

const hasVisibleFields = computed((): boolean => {
  // 检查分组内是否有可见字段
  return groupFields.value.some(field => {
    // 如果配置了 condition 函数，则必须满足条件
    if (field.condition) {
      return field.condition(props.question);
    }
    // 没有配置 condition，则始终显示（即使值为空）
    return true;
  });
});
</script>

<template>
  <div v-if="hasVisibleFields && groupConfig" :class="{ 'mb-6': mode === 'default' }">

    <!-- 模式 1: Inline (用于头部元数据区，不显示标题，水平排列) -->
    <template v-if="mode === 'inline'">
      <div class="flex flex-wrap gap-2">
         <template v-for="field in groupFields" :key="field.key">
            <FieldRenderer
              :config="field"
              :value="question[field.key]"
              :question="question"
            />
         </template>
      </div>
    </template>

    <!-- 模式 2: Compact (用于紧凑区域，如时间信息) -->
    <template v-else-if="mode === 'compact'">
       <div class="space-y-1">
          <template v-for="field in groupFields" :key="field.key">
             <!-- Compact 模式下如果是 Section，直接渲染内容 -->
             <template v-if="field.type === 'section'">
                 <FieldRenderer
                  :config="field"
                  :value="question[field.key]"
                  :question="question"
                >
                  <template #default="{ children, question: q }">
                    <FieldGroup
                      v-for="child in children"
                      :key="child.key"
                      :group="child.group"
                      :fields="[child]"
                      :question="q"
                      :all-fields="allFields"
                      mode="compact"
                    />
                  </template>
                </FieldRenderer>
             </template>
             <FieldRenderer
                v-else
                :config="field"
                :value="question[field.key]"
                :question="question"
             />
          </template>
       </div>
    </template>

    <!-- 模式 3: Default (默认，带左侧标题的列表布局) -->
    <template v-else>
      <div class="space-y-3">
        <!-- 注意：现在外部布局已经处理了卡片和标题，这里只负责渲染内容 -->
        <!-- 如果是 content 分组，直接渲染字段，不带左侧标签 -->
        <div v-if="group === 'content' || group === 'answer'" class="space-y-4">
           <template v-for="field in groupFields" :key="field.key">
              <FieldRenderer
                :config="field"
                :value="question[field.key]"
                :question="question"
              />
           </template>
        </div>

        <!-- 其他分组保持原有的左侧标题布局 (如果需要的话，或者改为流式) -->
        <!-- 由于外部 PreviewTab 已经按卡片分好了，这里直接渲染内容列表即可 -->
        <div v-else class="flex flex-col gap-3">
          <template v-for="field in groupFields" :key="field.key">

            <!-- section 类型使用特殊处理 -->
            <template v-if="field.type === 'section'">
              <FieldRenderer
                :config="field"
                :value="question[field.key]"
                :question="question"
              >
                <template #default="{ children, question: q }">
                  <FieldGroup
                    v-for="child in children"
                    :key="child.key"
                    :group="child.group"
                    :fields="[child]"
                    :question="q"
                    :all-fields="allFields"
                  />
                </template>
              </FieldRenderer>
            </template>

            <!-- 其他类型直接渲染 -->
            <FieldRenderer
              v-else
              :config="field"
              :value="question[field.key]"
              :question="question"
            />
          </template>
        </div>
      </div>
    </template>

  </div>
</template>
