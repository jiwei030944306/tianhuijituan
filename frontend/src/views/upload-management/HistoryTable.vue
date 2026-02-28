<script setup lang="ts">
/**
 * 历史记录表格组件
 * 显示上传历史记录,支持分页、查看详情、删除
 */
import { List, Check, Document } from '@element-plus/icons-vue';
import { getTypeLabel, getTypeColor, getTypeBgColor } from '@/utils/typeMapping';

interface HistoryItem {
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

interface Props {
  history: HistoryItem[];
  currentPage: number;
  pageSize: number;
}

interface Emits {
  (e: 'view-detail', batchId: string): void;
  (e: 'delete-record', batchId: string): void;
  (e: 'page-change', page: number): void;
  (e: 'size-change', size: number): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// 格式化题型分布显示
function formatTypeDistribution(distribution: HistoryItem['type_distribution']): string {
  if (!distribution) return '';
  const parts: string[] = [];
  if (distribution.single_choice) parts.push(`${distribution.single_choice}单选`);
  if (distribution.multiple_choice) parts.push(`${distribution.multiple_choice}多选`);
  if (distribution.fill_blank || distribution.fill_in) parts.push(`${(distribution.fill_blank || 0) + (distribution.fill_in || 0)}填空`);
  if (distribution.calculation) parts.push(`${distribution.calculation}计算`);
  if (distribution.application) parts.push(`${distribution.application}应用`);
  if (distribution.subjective) parts.push(`${distribution.subjective}解答`);
  return parts.join(', ');
}
</script>

<template>
  <!-- HISTORY TABLE -->
  <div class="absolute inset-0 flex flex-col">
    <div class="flex-1 overflow-auto">
      <table class="w-full text-left border-collapse">
<thead class="bg-slate-50 sticky top-0 z-10 border-b border-slate-200">
          <tr>
            <th class="px-5 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">批次名称</th>
            <th class="px-5 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">上传教师</th>
            <th class="px-5 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider w-32">题型分布</th>
            <th class="px-5 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider w-20">试题</th>
            <th class="px-5 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider w-20">图片</th>
            <th class="px-5 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider w-40">导入时间</th>
            <th class="px-5 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider w-20">状态</th>
            <th class="px-5 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider w-32 text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
<tr v-if="history.length === 0">
            <td colspan="8" class="px-5 py-16 text-center text-slate-400">
              <div class="flex flex-col items-center gap-2">
                <el-icon class="text-4xl opacity-20"><List /></el-icon>
                <span>暂无导入记录</span>
              </div>
            </td>
          </tr>
<tr
            v-for="record in history"
            :key="record.batch_id"
            class="hover:bg-slate-50 transition-colors group"
          >
            <td class="px-5 py-3">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-md bg-green-50 text-green-600 flex items-center justify-center font-bold text-xs shrink-0">
                  ZIP
                </div>
                <div>
                  <div class="text-sm font-bold text-slate-700 truncate max-w-xs" :title="record.display_name">
                    {{ record.display_name }}
                  </div>
                  <div class="text-[10px] text-slate-400 font-mono">{{ record.batch_id }}</div>
                </div>
              </div>
            </td>
            <td class="px-5 py-3 text-xs text-slate-600">
              {{ record.teacher_name }}
            </td>
            <td class="px-5 py-3">
              <div v-if="record.dominant_type" class="flex flex-col gap-1">
                <span
                  :class="[
                    'inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold',
                    getTypeBgColor(record.dominant_type),
                    getTypeColor(record.dominant_type)
                  ]"
                >
                  {{ getTypeLabel(record.dominant_type) }}
                </span>
                <span v-if="record.type_distribution" class="text-[10px] text-slate-400">
                  {{ formatTypeDistribution(record.type_distribution) }}
                </span>
              </div>
              <span v-else class="text-xs text-slate-400">-</span>
            </td>
            <td class="px-5 py-3 text-xs font-mono text-slate-600">
              {{ record.file_count }}
            </td>
            <td class="px-5 py-3 text-xs font-mono text-slate-600">
              {{ record.image_count }}
            </td>
            <td class="px-5 py-3 text-xs text-slate-500">
              {{ new Date(record.timestamp).toLocaleString() }}
            </td>
            <td class="px-5 py-3">
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-50 text-green-600 border border-green-100">
                <el-icon><Check /></el-icon>
                完成
              </span>
            </td>
            <td class="px-5 py-3 text-right">
              <el-button size="small" @click="emit('view-detail', record.batch_id)">
                查看
              </el-button>
              <el-button size="small" type="danger" @click="emit('delete-record', record.batch_id)">
                删除
              </el-button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- 分页组件 -->
    <div class="border-t border-slate-200 p-4 bg-white">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="history.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="emit('size-change', $event)"
        @current-change="emit('page-change', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
/* 组件样式使用 Tailwind CSS */
</style>
