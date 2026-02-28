<script setup lang="ts">
/**
 * 批次详情对话框组件
 * 显示上传批次的详细信息
 */
import { Document } from '@element-plus/icons-vue';

interface DetailData {
  batch_id: string;
  display_name: string;
  teacher_name: string;
  status: string;
  timestamp: string;
  file_count: number;
  image_count: number;
  files?: string[];
}

interface Props {
  visible: boolean;
  detailData: DetailData | null;
}

interface Emits {
  (e: 'update:visible', value: boolean): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    title="批次详情"
    width="600px"
  >
    <div v-if="detailData">
      <h3 class="text-sm font-bold text-slate-700 mb-3">批次信息</h3>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="批次ID">{{ detailData.batch_id }}</el-descriptions-item>
        <el-descriptions-item label="批次名称">{{ detailData.display_name }}</el-descriptions-item>
        <el-descriptions-item label="上传教师">{{ detailData.teacher_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag type="success" size="small">{{ detailData.status === 'completed' ? '已完成' : '处理中' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="导入时间" :span="2">
          {{ new Date(detailData.timestamp).toLocaleString() }}
        </el-descriptions-item>
      </el-descriptions>

      <h3 class="text-sm font-bold text-slate-700 mb-3 mt-6">数据统计</h3>
      <el-row :gutter="16">
        <el-col :span="12">
          <div class="bg-indigo-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-black text-indigo-600">{{ detailData.file_count }}</div>
            <div class="text-xs text-slate-500 mt-1">试题数量</div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="bg-emerald-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-black text-emerald-600">{{ detailData.image_count }}</div>
            <div class="text-xs text-slate-500 mt-1">图片数量</div>
          </div>
        </el-col>
      </el-row>

      <h3 class="text-sm font-bold text-slate-700 mb-3 mt-6">文件列表</h3>
      <div v-if="detailData.files && detailData.files.length > 0" class="space-y-2">
        <div v-for="(file, index) in detailData.files" :key="index" class="flex items-center gap-2 p-2 bg-slate-50 rounded">
          <el-icon><Document /></el-icon>
          <span class="text-sm text-slate-600">{{ file }}</span>
        </div>
      </div>
      <div v-else class="text-center text-slate-400 py-4">
        暂无文件列表
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
/* 组件样式使用 Tailwind CSS */
</style>
