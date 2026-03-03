<script setup lang="ts">
import { computed } from 'vue';
import { ChevronRight, ChevronDown, Tag } from 'lucide-vue-next';
import type { KnowledgeNode } from '@/components/common/KnowledgePointSelector.vue';

// 数据结构
interface KnowledgeGroup {
  id: string;
  name: string;
  count: number;
  expanded: boolean;
  children: KnowledgeSubGroup[];
}

interface KnowledgeSubGroup {
  id: string;
  name: string;
  count: number;
  expanded: boolean;
  children: KnowledgeLeaf[];
}

interface KnowledgeLeaf {
  id: string;
  name: string;
  count: number;
  selected: boolean;
}

interface Props {
  knowledgeTree: KnowledgeNode[];
  knowledgeStats: Record<string, number>;
  selectedTopics: string[];
  expandedGroups: Set<string>;
  expandedSubGroups: Set<string>;
}

interface Emits {
  (e: 'toggle-topic', topicName: string): void;
  (e: 'toggle-group', groupId: string): void;
  (e: 'toggle-subgroup', groupId: string, subGroupId: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  knowledgeTree: () => [],
  knowledgeStats: () => ({}),
  selectedTopics: () => [],
  expandedGroups: () => new Set<string>(),
  expandedSubGroups: () => new Set<string>()
});

const emit = defineEmits<Emits>();

// 构建树形结构
const knowledgeGroups = computed<KnowledgeGroup[]>(() => {
  const tree = props.knowledgeTree;
  
  const buildSubGroup = (nodes: KnowledgeNode[], parentId: string): KnowledgeSubGroup[] => {
    return nodes.map(node => {
      const leaves = node.children ? node.children.map(leaf => ({
        id: leaf.id,
        name: leaf.name,
        count: props.knowledgeStats[leaf.name] || 0,
        selected: props.selectedTopics.includes(leaf.name)
      })) : [];
      
      const total = leaves.reduce((sum, leaf) => sum + leaf.count, 0);
      
      return {
        id: node.id,
        name: node.name,
        count: total,
        expanded: true,  // 默认展开
        children: leaves
      };
    });
  };
  
  return tree.map(node => {
    const subGroups = node.children ? buildSubGroup(node.children, node.id) : [];
    const total = subGroups.reduce((sum, sg) => sum + sg.count, 0);
    
    return {
      id: node.id,
      name: node.name,
      count: total,
      expanded: true,  // 默认展开
      children: subGroups
    };
  });
});

const toggleGroup = (groupId: string) => {
  emit('toggle-group', groupId);
};

const toggleSubGroup = (groupId: string, subGroupId: string) => {
  emit('toggle-subgroup', groupId, subGroupId);
};

const toggleTopic = (topicName: string) => {
  emit('toggle-topic', topicName);
};
</script>

<template>
  <div class="space-y-3">
    <!-- 主分类 -->
    <div v-for="group in knowledgeGroups" :key="group.id" class="space-y-2">
      <!-- 主标签 -->
      <div
        class="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer transition-colors"
        @click="toggleGroup(group.id)"
      >
        <div class="flex items-center gap-2">
          <component
            :is="group.expanded ? ChevronDown : ChevronRight"
            :size="16"
            class="text-slate-400"
          />
          <span class="text-sm font-semibold text-slate-700">{{ group.name }}</span>
        </div>
        <span
          v-if="group.count > 0"
          class="text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 font-medium"
        >
          {{ group.count }}
        </span>
        <span v-else class="text-xs px-2 py-0.5 rounded-full bg-slate-200 text-slate-500">
          0
        </span>
      </div>

      <!-- 子分类 -->
      <div v-if="group.expanded" class="ml-4 space-y-2 border-l-2 border-slate-200 pl-3">
        <div
          v-for="subGroup in group.children"
          :key="subGroup.id"
          class="space-y-1.5"
        >
          <!-- 子标签 -->
          <div
            class="flex items-center justify-between px-2.5 py-1.5 rounded-md hover:bg-slate-50 cursor-pointer transition-colors"
            @click="toggleSubGroup(group.id, subGroup.id)"
          >
            <div class="flex items-center gap-2">
              <component
                :is="subGroup.expanded ? ChevronDown : ChevronRight"
                :size="14"
                class="text-slate-400"
              />
              <span class="text-xs font-medium text-slate-600">{{ subGroup.name }}</span>
            </div>
            <span
              v-if="subGroup.count > 0"
              class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-200 text-slate-600"
            >
              {{ subGroup.count }}
            </span>
          </div>

          <!-- 叶子节点（具体知识点） -->
          <div v-if="subGroup.expanded" class="ml-5 space-y-1">
            <button
              v-for="leaf in subGroup.children"
              :key="leaf.id"
              @click.stop="toggleTopic(leaf.name)"
              :class="[
                'inline-flex items-center justify-between w-full px-2.5 py-1.5 rounded-md text-xs transition-all duration-200',
                leaf.selected
                  ? 'bg-indigo-100 text-indigo-700 border border-indigo-200 shadow-sm'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50 hover:border-slate-300'
              ]"
            >
              <div class="flex items-center gap-1.5">
                <Tag :size="12" v-if="leaf.selected" />
                <span class="truncate">{{ leaf.name }}</span>
              </div>
              <span
                :class="[
                  'text-[10px] px-1.5 py-0.5 rounded-full',
                  leaf.count > 0
                    ? leaf.selected
                      ? 'bg-indigo-200 text-indigo-800'
                      : 'bg-slate-200 text-slate-600'
                    : 'bg-slate-100 text-slate-400'
                ]"
              >
                {{ leaf.count }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
