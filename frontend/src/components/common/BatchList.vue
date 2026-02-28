<script setup lang="ts">
// ==================== Props 定义 ====================

interface BatchFile {
  batch_id: string;
  display_name: string;
  file_count: number;
}

interface Props {
  files: BatchFile[];            // 批次文件列表
  selectedFile: string | null;   // 选中的批次ID
  visibleFiles: BatchFile[];     // 可见的批次列表
  uploadsCollapsed: boolean;     // 上传列表是否折叠
}

const props = defineProps<Props>();

// ==================== Events 定义 ====================

const emit = defineEmits<{
  'file-select': [batchId: string];      // 选择批次
  'toggle-collapse': [];                  // 切换折叠状态
}>();

// ==================== 方法 ====================

// 选择批次
const selectBatch = (batchId: string) => {
  emit('file-select', batchId);
};

// 切换折叠
const toggleCollapse = () => {
  emit('toggle-collapse');
};
</script>

<template>
  <!-- 批次列表 -->
  <div class="flex flex-col h-full bg-white border-r border-slate-200">
    <!-- 头部 -->
    <div class="h-14 border-b border-slate-200 px-4 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-2 text-slate-700 font-bold">
        <span class="text-sm">批次列表</span>
        <span v-if="files.length > 0" class="text-xs font-mono text-slate-400">({{ files.length }})</span>
      </div>
      <button
        @click="toggleCollapse"
        class="p-1 rounded hover:bg-slate-100 text-slate-500 transition-colors"
        :title="uploadsCollapsed ? '展开上传列表' : '折叠上传列表'"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          :class="['transition-transform', uploadsCollapsed ? 'rotate-180' : '']"
        >
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>
    </div>

    <!-- 批次列表内容 -->
    <div class="flex-1 overflow-auto">
      <!-- 无批次 -->
      <div v-if="visibleFiles.length === 0" class="flex flex-col items-center justify-center h-full text-slate-400 px-4">
        <p class="text-xs text-center">暂无批次数据</p>
      </div>

      <!-- 批次列表 -->
      <div v-else class="p-2 space-y-1">
        <div
          v-for="file in visibleFiles"
          :key="file.batch_id"
          @click="selectBatch(file.batch_id)"
          :class="[
            'p-3 rounded-lg cursor-pointer transition-all border',
            selectedFile === file.batch_id
              ? 'bg-blue-50 border-blue-500 text-blue-900 shadow-sm'
              : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300'
          ]"
        >
          <div class="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              :class="selectedFile === file.batch_id ? 'text-blue-600' : 'text-slate-400'"
            >
              <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"></path>
            </svg>
            <div class="flex-1 min-w-0">
              <div
                :class="[
                  'text-xs truncate',
                  selectedFile === file.batch_id ? 'font-bold' : 'font-medium'
                ]"
                :title="file.display_name"
              >
                {{ file.display_name }}
              </div>
              <div :class="[
                'text-[10px] mt-0.5',
                selectedFile === file.batch_id ? 'text-blue-500' : 'text-slate-400'
              ]">
                {{ file.file_count }} 个文件
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 批次列表样式 */
</style>
