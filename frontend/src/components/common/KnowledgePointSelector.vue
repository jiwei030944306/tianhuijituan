<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  X,
  ChevronRight,
  ChevronDown,
  Check,
  Search,
  Folder,
  Tag as TagIcon
} from 'lucide-vue-next';

// 知识点数据结构
export interface KnowledgeNode {
  id: string;
  name: string;
  children?: KnowledgeNode[];
  expanded?: boolean;
  selected?: boolean;
}

interface KnowledgePointSelectorProps {
  isOpen: boolean;
  selected?: string[];
  /** 知识点树数据，由父组件根据学科学段传入 */
  knowledgeTree?: KnowledgeNode[];
}

interface KnowledgePointSelectorEmits {
  (e: 'close'): void;
  (e: 'confirm', selected: string[]): void;
}

const props = withDefaults(defineProps<KnowledgePointSelectorProps>(), {
  selected: () => [],
  knowledgeTree: () => []
});

const emit = defineEmits<KnowledgePointSelectorEmits>();

const searchKeyword = ref('');
const selectedNodes = ref<Set<string>>(new Set(props.selected));

// 内部响应式知识点数据（深拷贝 props 数据以支持展开状态）
const knowledgeData = ref<KnowledgeNode[]>([]);

// 监听 props.knowledgeTree 变化，深拷贝并初始化展开状态
watch(() => props.knowledgeTree, (newTree) => {
  const deepCloneWithExpanded = (nodes: KnowledgeNode[]): KnowledgeNode[] => {
    return nodes.map(node => ({
      ...node,
      expanded: false,
      children: node.children ? deepCloneWithExpanded(node.children) : undefined
    }));
  };
  knowledgeData.value = deepCloneWithExpanded(newTree || []);
}, { immediate: true, deep: true });

// 监听 selected props 变化
watch(() => props.selected, (newSelected) => {
  selectedNodes.value = new Set(newSelected);
}, { immediate: true });

const filteredData = computed(() => {
  if (!searchKeyword.value) return knowledgeData.value;

  const keyword = searchKeyword.value.toLowerCase();
  const filterNodes = (nodes: KnowledgeNode[]): KnowledgeNode[] => {
    const result: KnowledgeNode[] = [];
    for (const node of nodes) {
      const nameMatch = node.name.toLowerCase().includes(keyword);
      const childrenMatch = node.children ? filterNodes(node.children) : [];

      if (nameMatch || childrenMatch.length > 0) {
        result.push({
          ...node,
          expanded: true,
          children: childrenMatch.length > 0 ? childrenMatch : node.children
        });
      }
    }
    return result;
  };
  
  return filterNodes(knowledgeData.value);
});

const toggleExpand = (node: KnowledgeNode) => {
  if (node.children && node.children.length > 0) {
    node.expanded = !node.expanded;
  }
};

const toggleSelect = (node: KnowledgeNode) => {
  if (selectedNodes.value.has(node.id)) {
    selectedNodes.value.delete(node.id);
  } else {
    selectedNodes.value.add(node.id);
  }
};

const isSelected = (nodeId: string) => {
  return selectedNodes.value.has(nodeId);
};

const hasChildren = (node: KnowledgeNode) => {
  return node.children && node.children.length > 0;
};

const handleClose = () => {
  emit('close');
};

const handleConfirm = () => {
  emit('confirm', Array.from(selectedNodes.value));
};

const handleClear = () => {
  selectedNodes.value.clear();
};

const resetExpanded = () => {
  const resetNode = (node: KnowledgeNode) => {
    if (node.children) {
      node.expanded = false;
      node.children.forEach(resetNode);
    }
  };
  knowledgeData.value.forEach(resetNode);
};
</script>

<template>
  <Transition name="modal">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4"
      @click.self="handleClose"
    >
      <div class="bg-white w-full max-w-3xl rounded-2xl shadow-2xl flex flex-col max-h-[80vh] animate-scale-in">
        <div class="p-5 border-b border-slate-200 flex justify-between items-center bg-slate-50/50">
          <h3 class="font-bold text-slate-800 flex items-center gap-2">
            <TagIcon :size="18" class="text-indigo-600" /> 选择知识点
          </h3>
          <button
            @click="handleClose"
            class="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X :size="20" />
          </button>
        </div>

        <div class="flex-1 overflow-hidden flex flex-col">
          <div class="p-4 border-b border-slate-100">
            <div class="relative">
              <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                v-model="searchKeyword"
                type="text"
                placeholder="搜索知识点..."
                class="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
          </div>

          <div class="flex-1 overflow-y-auto p-4 custom-scrollbar">
            <div v-for="category in filteredData" :key="category.id" class="mb-2">
              <div
                class="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors"
                @click="toggleExpand(category)"
              >
                <ChevronRight
                  v-if="hasChildren(category)"
                  :size="16"
                  :class="['transition-transform', category.expanded ? 'rotate-90' : '']"
                  class="text-slate-400 shrink-0"
                />
                <div v-else class="w-4"></div>
                <Folder :size="16" class="text-indigo-500 shrink-0" />
                <span class="text-sm font-medium text-slate-700">{{ category.name }}</span>
              </div>

              <div v-if="category.expanded && category.children" class="ml-4 mt-1">
                <div v-for="subcategory in category.children" :key="subcategory.id" class="mb-1">
                  <div
                    class="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors"
                    @click="toggleExpand(subcategory)"
                  >
                    <ChevronRight
                      v-if="hasChildren(subcategory)"
                      :size="14"
                      :class="['transition-transform', subcategory.expanded ? 'rotate-90' : '']"
                      class="text-slate-400 shrink-0"
                    />
                    <div v-else class="w-3.5"></div>
                    <Folder :size="14" class="text-indigo-400 shrink-0" />
                    <span class="text-xs text-slate-600">{{ subcategory.name }}</span>
                  </div>

                  <div v-if="subcategory.expanded && subcategory.children" class="ml-4 mt-1">
                    <div
                      v-for="item in subcategory.children"
                      :key="item.id"
                      class="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors group"
                      @click="toggleSelect(item)"
                    >
                      <div class="w-3.5"></div>
                      <div
                        :class="[
                          'w-4 h-4 rounded border-2 flex items-center justify-center shrink-0 transition-colors',
                          isSelected(item.id)
                            ? 'bg-indigo-500 border-indigo-500'
                            : 'border-slate-300 group-hover:border-indigo-400'
                        ]"
                      >
                        <Check
                          v-if="isSelected(item.id)"
                          :size="10"
                          class="text-white"
                        />
                      </div>
                      <span
                        :class="[
                          'text-xs',
                          isSelected(item.id) ? 'text-indigo-600 font-medium' : 'text-slate-600'
                        ]"
                      >
                        {{ item.name }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="selectedNodes.size > 0" class="p-4 border-t border-slate-100 bg-slate-50">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold text-slate-500">已选择 ({{ selectedNodes.size }})</span>
              <button
                @click="handleClear"
                class="text-xs text-red-500 hover:text-red-600 transition-colors"
              >
                清空
              </button>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="id in selectedNodes"
                :key="id"
                class="px-2 py-1 bg-indigo-50 text-indigo-600 text-xs rounded border border-indigo-100 font-medium flex items-center gap-1"
              >
                {{ id }}
                <button
                  @click="toggleSelect({ id } as KnowledgeNode)"
                  class="hover:text-indigo-800"
                >
                  <X :size="12" />
                </button>
              </span>
            </div>
          </div>
        </div>

        <div class="p-5 border-t border-slate-200 flex gap-3">
          <button
            @click="handleClose"
            class="px-6 py-2.5 border border-slate-200 text-slate-600 bg-white rounded-xl hover:bg-slate-50 font-bold text-sm transition-colors"
          >
            取消
          </button>
          <button
            @click="handleConfirm"
            class="flex-1 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 shadow-lg shadow-indigo-200 font-bold text-sm transition-all"
          >
            确认选择
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(148, 163, 184, 0.5);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(100, 116, 139, 0.8);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scale-in {
  animation: scale-in 0.3s ease-out;
}
</style>