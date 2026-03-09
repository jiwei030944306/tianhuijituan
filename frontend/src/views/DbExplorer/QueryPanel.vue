<!--
  数据查询模块组件
  提供 SQL 查询执行功能
-->

<template>
  <div class="flex-1 p-6 overflow-auto">
    <h3 class="font-bold text-slate-700 text-lg mb-4">SQL 查询</h3>
    <textarea
      v-model="localQueryText"
      rows="8"
      class="w-full px-4 py-3 bg-slate-900 text-green-400 font-mono text-sm rounded-xl border border-slate-700 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
      placeholder="SELECT * FROM questions LIMIT 10;"
      :disabled="loading"
    ></textarea>
    <div class="flex gap-3 mt-4">
      <button
        @click="handleExecute"
        :disabled="loading || !localQueryText.trim()"
        class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Play v-if="!loading" :size="16" class="inline mr-1" />
        <Loader2 v-else :size="16" class="inline mr-1 animate-spin" />
        {{ loading ? '执行中...' : '执行查询' }}
      </button>
      <button
        @click="handleClear"
        :disabled="loading"
        class="px-4 py-2 bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 transition-colors disabled:opacity-50"
      >
        清空
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
      <div class="flex items-center gap-2 text-red-700">
        <AlertCircle :size="18" />
        <span class="font-medium">查询错误</span>
      </div>
      <p class="mt-2 text-sm text-red-600">{{ error }}</p>
    </div>

    <!-- 执行信息 -->
    <div v-if="lastExecutionTime !== null" class="mt-4 text-sm text-slate-500">
      执行时间: {{ lastExecutionTime.toFixed(2) }} ms
    </div>

    <!-- 查询结果 -->
    <div v-if="resultColumns.length > 0" class="mt-6">
      <h4 class="font-bold text-slate-700 mb-3">查询结果 ({{ resultTotal }} 行)</h4>
      <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50">
              <tr>
                <th
                  v-for="col in resultColumns"
                  :key="col"
                  class="px-4 py-2 text-left font-medium text-slate-600 border-b border-slate-200 whitespace-nowrap"
                >
                  {{ col }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, index) in resultData"
                :key="index"
                class="border-b border-slate-100 hover:bg-slate-50"
              >
                <td
                  v-for="col in resultColumns"
                  :key="col"
                  class="px-4 py-2 text-slate-700 whitespace-nowrap"
                >
                  {{ formatValue(row[col]) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 空结果提示 -->
    <div v-else-if="hasExecuted && !loading && !error" class="mt-6 text-center text-slate-500 py-8">
      查询成功，但未返回任何数据
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Play, Loader2, AlertCircle } from 'lucide-vue-next';
import { dbExplorerApi } from '@/api/dbExplorer';

// ==========================================
// 类型定义
// ==========================================

interface TableRow {
  [key: string]: any;
}

// ==========================================
// Props & Emits
// ==========================================

const props = defineProps<{
  queryText: string;
}>();

const emit = defineEmits<{
  (e: 'update:queryText', value: string): void;
}>();

// ==========================================
// 状态
// ==========================================

const localQueryText = ref(props.queryText);
const loading = ref(false);
const error = ref<string | null>(null);
const resultColumns = ref<string[]>([]);
const resultData = ref<TableRow[]>([]);
const resultTotal = ref(0);
const lastExecutionTime = ref<number | null>(null);
const hasExecuted = ref(false);

// ==========================================
// 监听器
// ==========================================

watch(localQueryText, (newValue) => {
  emit('update:queryText', newValue);
});

watch(() => props.queryText, (newValue) => {
  localQueryText.value = newValue;
});

// ==========================================
// 方法
// ==========================================

async function handleExecute() {
  if (!localQueryText.value.trim() || loading.value) return;

  loading.value = true;
  error.value = null;
  hasExecuted.value = true;

  try {
    const response = await dbExplorerApi.executeQuery(localQueryText.value.trim());

    if (response.success && response.result) {
      resultColumns.value = response.result.columns;
      resultData.value = response.result.rows;
      resultTotal.value = response.result.total;
    } else {
      error.value = response.error || '查询执行失败';
      resultColumns.value = [];
      resultData.value = [];
      resultTotal.value = 0;
    }

    lastExecutionTime.value = response.execution_time_ms;
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '网络请求失败';
    resultColumns.value = [];
    resultData.value = [];
    resultTotal.value = 0;
  } finally {
    loading.value = false;
  }
}

function handleClear() {
  localQueryText.value = '';
  error.value = null;
  resultColumns.value = [];
  resultData.value = [];
  resultTotal.value = 0;
  lastExecutionTime.value = null;
  hasExecuted.value = false;
}

function formatValue(value: any): string {
  if (value === null) return 'NULL';
  if (value === undefined) return '';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}
</script>