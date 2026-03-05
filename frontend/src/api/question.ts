/**
 * 题目API服务
 * 封装与后端API的交互
 * 优化：添加请求取消和去重机制，防止重复请求堆积
 */

import axios, { type CancelTokenSource } from 'axios';
import type { Question, QuestionFilters, UploadResponse, StatisticsData } from '@/types/question';
import { apiClient } from './base';

// 请求取消令牌管理
const cancelTokens: Map<string, CancelTokenSource> = new Map();

/**
 * 取消指定key的请求
 * @param key 请求标识符
 */
function cancelRequest(key: string) {
  const source = cancelTokens.get(key);
  if (source) {
    source.cancel(`请求已取消: ${key}`);
    cancelTokens.delete(key);
  }
}

/**
 * 创建新的取消令牌
 * @param key 请求标识符
 * @returns CancelTokenSource
 */
function createCancelToken(key: string): CancelTokenSource {
  // 取消旧请求
  cancelRequest(key);

  // 创建新令牌
  const source = axios.CancelToken.source();
  cancelTokens.set(key, source);
  return source;
}

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 忽略取消请求的错误
    if (axios.isCancel(error)) {
      console.log('请求已取消:', error.message);
      return Promise.reject({ cancelled: true, message: error.message });
    }

    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

/**
 * 题目API服务
 */
export const questionApi = {
  /**
   * 获取题目列表
   * @param filters 筛选条件
   */
  async getList(filters?: QuestionFilters): Promise<Question[]> {
    const source = createCancelToken('getList');
    // 转换筛选参数格式
    const params: Record<string, any> = {};
    if (filters?.subject) params.subject = filters.subject;
    if (filters?.grade) params.grade = filters.grade;
    if (filters?.educationLevel) params.education_level = filters.educationLevel;
    if (filters?.type) params.type = filters.type;
    if (filters?.difficulty) params.difficulty = filters.difficulty;
    if (filters?.status) params.status = filters.status;
    if (filters?.isDuplicate !== undefined) params.is_duplicate = filters.isDuplicate;

    const response = await apiClient.get('/api/questions/', {
      params,
      cancelToken: source.token
    });
    return response as Question[];
  },

  /**
   * 获取题目详情
   * @param id 题目ID
   */
  async getDetail(id: string): Promise<Question> {
    const source = createCancelToken(`getDetail-${id}`);
    const response = await apiClient.get(`/api/questions/${id}`, {
      cancelToken: source.token
    });
    return response as Question;
  },

  /**
   * 上传文件夹
   * @param formData 表单数据（包含JSON文件、图片、分类信息）
   * @param onProgress 进度回调
   */
  async uploadFolder(
    formData: FormData,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> {
    // 上传请求不使用取消令牌，避免中断上传
    const response = await apiClient.post('/api/questions/upload-folder', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000, // 上传可能需要更长时间
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      }
    });
    return response.data as UploadResponse;
  },

/**
   * 删除题目
   * @param id 题目ID
   */
  async delete(id: string): Promise<void> {
    const source = createCancelToken(`delete-${id}`);
    await apiClient.delete(`/api/questions/${id}`, {
      cancelToken: source.token
    });
  },

  /**
   * 获取统计数据
   */
  async getStatistics(): Promise<StatisticsData> {
    const source = createCancelToken('getStatistics');
    const response = await apiClient.get('/api/questions/statistics', {
      cancelToken: source.token
    });
    return response as StatisticsData;
  },

  /**
   * 批量更新题目
   * @param batchId 批次ID
   * @param questions 要更新的题目列表
   */
  async bulkUpdate(batchId: string, questions: Partial<Question>[]): Promise<{ success: boolean; updated_count: number }> {
    // 批量更新不使用取消令牌，确保完成
    const response = await apiClient.post(`/api/questions/batch/${batchId}/bulk-update`, {
      batch_id: batchId,
      questions
    });
    return response as { success: boolean; updated_count: number };
  },

  /**
   * 取消所有待处理的请求
   */
  cancelAll() {
    cancelTokens.forEach((source, key) => {
      source.cancel(`批量取消请求: ${key}`);
    });
    cancelTokens.clear();
  }
};

/**
 * 获取图片完整URL
 * @param path 图片路径（如：legacy/1/xxx.jpg）
 */
export function getImageUrl(path: string): string {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) ?? 'http://localhost:8000'
  return `${API_BASE}/static/${path}`;
}
