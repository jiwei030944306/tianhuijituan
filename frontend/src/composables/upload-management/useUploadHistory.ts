/**
 * 上传历史记录管理 Composable
 * 职责: 加载历史、删除记录、分页、查看详情
 * 优化: 使用axios实例，支持请求取消
 */
import { ref, computed } from 'vue';
import { apiClient } from '@/api/base';
import axios from 'axios';
import { apiClient } from '@/api/base';

// 请求取消令牌
let cancelTokenSource: axios.CancelTokenSource | null = null;

// 类型定义
export interface HistoryItem {
  batch_id: string;
  display_name: string;
  teacher_name: string;
  file_count: number;
  image_count: number;
  timestamp: string;
  status: string;
  dominant_type?: string;  // 主要题型
  type_distribution?: {
    single_choice?: number;
    multiple_choice?: number;
    fill_blank?: number;
    fill_in?: number;
    calculation?: number;
    application?: number;
    subjective?: number;
  };
}

export function useUploadHistory(folderCode: () => string, addLog: (msg: string, level: string) => void) {
  // 状态
  const history = ref<HistoryItem[]>([]);
  const loadingHistory = ref(false);
  const currentPage = ref(1);
  const pageSize = ref(20);

  // 批次详情相关
  const showDetailDialog = ref(false);
  const currentDetail = ref<HistoryItem | null>(null);

  // 计算属性 - 累计统计
  const totalBatches = computed(() => history.value.length);
  const totalQuestions = computed(() => history.value.reduce((sum, item) => sum + item.file_count, 0));
  const totalImages = computed(() => history.value.reduce((sum, item) => sum + item.image_count, 0));

  // 计算属性 - 分页后的历史记录
  const pagedHistory = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    return history.value.slice(start, end);
  });

  // 加载历史记录
  const refreshHistory = async () => {
    const code = folderCode();
    if (!code) return;

    // 取消上一次请求
    if (cancelTokenSource) {
      cancelTokenSource.cancel('新请求已发起');
    }
    cancelTokenSource = axios.CancelToken.source();

    loadingHistory.value = true;
  try {
      const response = await apiClient.get(`/api/questions/upload-history`, {
        params: { folder_code: code },
        cancelToken: cancelTokenSource.token
      });

      history.value = response.data.records || [];
    } catch (error: unknown) {
      // 忽略取消请求的错误
      if (axios.isCancel(error as any)) {
        console.log('请求已取消:', (error as any).message);
        return;
      }
      const message = error instanceof Error ? error.message : String(error);
      addLog(`获取历史记录失败: ${message}`, 'error');
      history.value = [];
    } finally {
      loadingHistory.value = false;
    }
  };

  // 删除历史记录
  const handleDeleteRecord = async (batchId: string) => {
    if (!confirm('确定要删除这条导入记录吗？注意：这不会删除已入库的题目。')) {
      return;
    }

    try {
      await apiClient.delete(`/api/questions/batch/${batchId}`);
      addLog('删除记录成功', 'success');
      await refreshHistory();
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      addLog(`删除记录失败: ${message}`, 'error');
    }
  };

  // 查看批次详情
  const viewDetail = async (batchId: string) => {
    try {
      addLog(`查看批次详情: ${batchId}`, 'info');

      const batchInfo = history.value.find(item => item.batch_id === batchId);

      if (batchInfo) {
        currentDetail.value = {
          ...batchInfo,
          files: []
        };
        showDetailDialog.value = true;
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      addLog(`获取批次详情失败: ${message}`, 'error');
    }
  };

  // 分页切换处理
  const handlePageChange = (page: number) => {
    currentPage.value = page;
  };

  const handleSizeChange = (size: number) => {
    pageSize.value = size;
    currentPage.value = 1;
  };

  return {
    // 状态
    history,
    loadingHistory,
    currentPage,
    pageSize,
    showDetailDialog,
    currentDetail,

    // 计算属性
    totalBatches,
    totalQuestions,
    totalImages,
    pagedHistory,

    // 方法
    refreshHistory,
    handleDeleteRecord,
    viewDetail,
    handlePageChange,
    handleSizeChange,
  };
}
