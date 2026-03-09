<!-- 
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 上传管理中心 (UploadManagement.vue)
  本页面是系统的 P0 核心功能模块，负责试题文件（ZIP/JSON）的批量上传、冲突检测及历史记录管理。
  它通过高度集成的 Composables 协调复杂的上传流、实时日志展示及数据统计。
-->

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - 核心：Vue 3 Composition API (ref, computed, onMounted)
 * - 导航：Vue Router (环境校验与跳转)
 * - 状态：Pinia (useContextStore, useUserStore 用于获取业务环境与用户信息)
 * - 业务逻辑封装 (Composables)：
 *   - useUploadLogs: 处理日志持久化与上报
 *   - useUploadHistory: 处理上传批次的分页与查询
 *   - useUploadOperation: 处理文件解析、冲突检测与上传执行
 * - 局部组件：Sidebar, StatsHeader, HistoryTable, LiveTerminal, Dialogs
 */
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useContextStore } from '@/stores/context';
import { useUserStore } from '@/stores/user';
import { Grid, Monitor, Check, Right, QuestionFilled } from '@element-plus/icons-vue';
import HelpGuide from '@/components/common/HelpGuide.vue';

// 导入页面专属组件
import UploadSidebar from './upload-management/UploadSidebar.vue';
import StatsHeader from './upload-management/StatsHeader.vue';
import HistoryTable from './upload-management/HistoryTable.vue';
import LiveTerminal from './upload-management/LiveTerminal.vue';
import BatchDetailDialog from './upload-management/BatchDetailDialog.vue';
import ConflictDialog from './upload-management/ConflictDialog.vue';
import UploadDebugger from './upload-management/UploadDebugger.vue';

// 导入 Composables
import { useUploadLogs } from '@/composables/upload-management/useUploadLogs';
import { useUploadHistory } from '@/composables/upload-management/useUploadHistory';
import { useUploadOperation } from '@/composables/upload-management/useUploadOperation';

// ==========================================
// 2. 主要功能代码分区注释 - 逻辑处理区
// ==========================================

// --- 初始化与环境校验 ---
const router = useRouter();
const contextStore = useContextStore();
const userStore = useUserStore();

// 3. 核心代码强调：严格环境校验
// 如果用户未在 Landing 页选择学段/学科，强制回退，防止数据错位
if (!contextStore.grade || !contextStore.subject) {
  router.push('/');
}

// --- 响应式状态与引用 ---
const debuggerRef = ref<InstanceType<typeof UploadDebugger> | null>(null);
const activeTab = ref<'history' | 'logs'>('history');
const showDebuggerDrawer = ref(false);
const showHelpGuide = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

// --- 3. 核心代码强调：业务上下文计算 (Context Derivation) ---
// 将全局 Store 状态映射为当前页面渲染所需的具体描述
const currentSubject = computed(() => contextStore.subjectName || '未知学科');
const currentGrade = computed(() => contextStore.levelName || '未知学段');
const currentTeacher = computed(() => userStore.currentUser?.name || contextStore.teacherName || '未知教师');
const folderCode = computed(() => contextStore.folderCode || '-');

// --- 核心业务逻辑组合 (Composables Orchestration) ---

// 1. 日志管理系统
const {
  uploadLogs,
  logSummary,
  addLog,
  restoreLogs,
  reportLogs: baseReportLogs
} = useUploadLogs();

// 2. 历史记录管理系统 (由 folderCode 驱动)
const {
  history,
  loadingHistory,
  currentPage,
  pageSize,
  showDetailDialog,
  currentDetail,
  totalBatches,
  totalQuestions,
  totalImages,
  pagedHistory,
  refreshHistory,
  handleDeleteRecord,
  viewDetail,
  handlePageChange,
  handleSizeChange
} = useUploadHistory(() => folderCode.value, addLog);

// 3. 上传核心操作流 (高度封装，支持回调)
const {
  files,
  uploading,
  progress,
  uploadComplete,
  conflictInfo,
  showConflictDialog,
  handleFileSelect,
  removeFile,
  clearFiles,
  handleUpload,
  handleConflictResolve
} = useUploadOperation(
  {
    folderCode: () => folderCode.value,  // 学科代码
    currentTeacher: () => currentTeacher.value,
    contextStore
  },
  // 回调：将上传过程中的日志同步到日志管理系统
  (msg, level) => addLog(msg, level as any, debuggerRef),
  refreshHistory,
  debuggerRef
);

// --- 辅助交互方法 ---
const reportLogs = async () => {
  const userInfo = {
    userId: userStore.currentUser?.id,
    userName: userStore.currentUser?.name || contextStore.teacherName,
    folderCode: folderCode.value
  };
  await baseReportLogs(debuggerRef, userInfo);
};

// --- 生命周期挂载 ---
onMounted(() => {
  refreshHistory();
  restoreLogs();
});

const goToProcess = () => {
  router.push('/process');
};

const openDebugger = () => {
  showDebuggerDrawer.value = true;
};

const handleFileInputClick = () => {
  fileInputRef.value?.click();
};
</script>

<template>
  <div class="absolute top-16 left-0 right-0 bottom-0 bg-slate-50 flex overflow-hidden">
    
    <!-- ==========================================
         2. 主要功能代码分区注释 - 页面渲染区
         ========================================== -->

    <!-- [Sidebar Container] 左侧边栏：环境信息、文件列表与操作入口 -->
    <UploadSidebar
      :files="files"
      :uploading="uploading"
      :progress="progress"
      :upload-logs="uploadLogs"
      :log-summary="logSummary"
      :current-grade="currentGrade"
      :current-subject="currentSubject"
      :current-teacher="currentTeacher"
      :folder-code="folderCode"
      @upload-start="handleUpload"
      @clear-files="clearFiles"
      @remove-file="removeFile"
      @open-debugger="openDebugger"
      @file-input-click="handleFileInputClick"
    />

    <!-- [Native File Input] 隐藏的文件选择器 -->
    <input
      ref="fileInputRef"
      type="file"
      accept=".zip,.json"
      multiple
      class="hidden"
      @change="handleFileSelect"
    />

    <!-- [Main Area] 右侧主显示区 -->
    <div class="flex-1 flex flex-col min-w-0 bg-slate-50">
      
      <!-- 3. 核心代码强调：多维度资产数据统计头部 (Stats Aggregation) -->
      <StatsHeader
        :total-batches="totalBatches"
        :total-questions="totalQuestions"
        :total-images="totalImages"
        @report-logs="reportLogs"
      />

      <!-- [Content Container] 内容区域：切换导入历史与实时日志 -->
      <div class="flex-1 overflow-hidden flex flex-col px-4 pb-4 bg-slate-50">

        <!-- Toolbar: Tab 切换与成功后的快速导航 -->
        <div class="flex justify-between items-center mb-3 pt-4">
          <div class="flex gap-1 bg-white p-1 rounded-lg border border-slate-200 shadow-sm">
            <button
              @click="activeTab = 'history'"
              :class="['px-4 py-1.5 text-xs font-bold rounded-md transition-all flex items-center gap-2',
                activeTab === 'history' ? 'bg-green-50 text-green-600 shadow-sm' : 'text-slate-500 hover:bg-slate-50']"
            >
              <el-icon><Grid /></el-icon> 导入历史
            </button>
            <button
              @click="activeTab = 'logs'"
              :class="['px-4 py-1.5 text-xs font-bold rounded-md transition-all flex items-center gap-2',
                activeTab === 'logs' ? 'bg-green-50 text-green-600 shadow-sm' : 'text-slate-500 hover:bg-slate-50']"
            >
              <el-icon><Monitor /></el-icon> 实时终端
              <span v-if="uploading" class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            </button>
          </div>

          <!-- 3. 核心代码强调：任务完成后的闭环引导 (Workflow Bridge) -->
          <div v-if="uploadComplete" class="flex items-center gap-2 animate-fade-in-left">
            <span class="text-xs font-bold text-green-600 bg-green-50 px-3 py-1.5 rounded-full border border-green-100 flex items-center gap-1">
              <el-icon><Check /></el-icon> 导入成功
            </span>
            <el-button type="success" size="small" class="text-xs font-bold rounded-md" @click="goToProcess">
              去处理 <el-icon><Right /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- View Display: 根据 activeTab 切换显示的子组件 - 卡片风格 -->
        <div class="flex-1 bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden relative">
          <!-- VIEW A: 导入历史表格 (数据驱动分页) -->
          <HistoryTable
            v-show="activeTab === 'history'"
            :history="pagedHistory"
            :current-page="currentPage"
            :page-size="pageSize"
            @view-detail="viewDetail"
            @delete-record="handleDeleteRecord"
            @page-change="handlePageChange"
            @size-change="handleSizeChange"
          />

          <!-- VIEW B: 实时终端日志 (IDE 风格渲染) -->
          <LiveTerminal
            v-show="activeTab === 'logs'"
            :upload-logs="uploadLogs"
            :uploading="uploading"
          />
        </div>

        <!-- 底部状态栏 -->
        <div class="mt-2 text-[10px] text-slate-400 flex justify-between px-1">
          <span>ZyCloud Data Ingestion Engine v2.1</span>
          <span>Server Status: Online</span>
        </div>
      </div>
    </div>

    <!-- [Modals & Drawers] 全局弹窗与侧滑层 -->
    
    <!-- 3. 核心代码强调：冲突检测拦截器 (Conflict Interceptor) -->
    <ConflictDialog
      v-model="showConflictDialog"
      :conflict-info="conflictInfo"
      @resolve="handleConflictResolve"
    />

    <!-- 3. 核心代码强调：深度处理调试器 (Background Task Debugger) -->
    <el-drawer v-model="showDebuggerDrawer" title="处理详情" direction="rtl" size="50%">
      <template #header>
        <div class="flex items-center gap-2">
          <el-icon class="text-green-600"><Monitor /></el-icon>
          <span class="font-bold text-slate-800">处理详情</span>
        </div>
      </template>
      <UploadDebugger ref="debuggerRef" />
    </el-drawer>

    <!-- 批次详情对话框 -->
    <BatchDetailDialog
      v-model:visible="showDetailDialog"
      :detail-data="currentDetail"
    />
  </div>
</template>


<style scoped>
@keyframes fade-in-left {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-fade-in-left {
  animation: fade-in-left 0.3s ease-out;
}
</style>
