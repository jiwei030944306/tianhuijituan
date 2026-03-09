<!--
  数据表模块组件
  提供数据库表结构浏览、数据查看功能
-->

<template>
  <div class="flex-1 flex overflow-hidden">
    <!-- 左侧：表列表面板 -->
    <div class="w-72 bg-white border-r border-slate-200 flex flex-col">
      <!-- 表列表头部 -->
      <div class="p-3 border-b border-slate-100 flex items-center justify-between">
        <span class="text-sm font-bold text-slate-700">数据库表</span>
        <button
          @click="emit('refresh')"
          class="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
          title="刷新"
        >
          <RefreshCw :size="14" />
        </button>
      </div>

      <!-- 表列表 -->
      <div class="flex-1 overflow-auto">
        <div
          v-for="table in tables"
          :key="table.name"
          class="border-b border-slate-100"
        >
          <!-- 表名行 -->
          <div
            @click="emit('select', table.name)"
            class="flex items-center gap-2 px-3 py-2.5 cursor-pointer transition-colors"
            :class="selectedTable === table.name ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-700'"
          >
            <ChevronRight
              :size="14"
              class="transition-transform"
              :class="expandedTables.includes(table.name) ? 'rotate-90' : ''"
              @click.stop="toggleExpand(table.name)"
            />
            <Table :size="14" />
            <span class="text-sm font-medium flex-1">{{ table.name }}</span>
            <span class="text-xs text-slate-400">{{ table.rowCount }}</span>
          </div>

          <!-- 字段列表（展开时显示） -->
          <div
            v-if="expandedTables.includes(table.name)"
            class="bg-slate-50 py-1"
          >
            <div
              v-for="column in table.columns"
              :key="column.name"
              class="flex items-center gap-2 px-3 py-1.5 pl-8 text-sm"
            >
              <component
                :is="getColumnIcon(column.type)"
                :size="12"
                :class="getColumnColor(column.type)"
              />
              <span class="text-slate-600">{{ column.name }}</span>
              <span class="text-xs text-slate-400 ml-auto">{{ column.type }}</span>
              <span v-if="column.pk" class="text-xs bg-amber-100 text-amber-600 px-1 rounded">PK</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：数据展示面板 -->
    <div class="flex-1 flex flex-col bg-white">
      <!-- 工具栏 -->
      <div class="p-3 border-b border-slate-200 flex items-center gap-3">
        <div class="flex items-center gap-2">
          <span class="text-sm font-bold text-slate-700">{{ selectedTable || '选择表' }}</span>
          <span v-if="tableData.length > 0" class="text-xs text-slate-400">
            {{ tableData.length }} 行
          </span>
        </div>
        <div class="flex-1"></div>
        <div class="flex items-center gap-2">
          <input
            :value="searchKeyword"
            @input="emit('update:searchKeyword', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="搜索..."
            class="px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent w-48"
          />
          <button
            class="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-1"
          >
            <Plus :size="14" />
            新增
          </button>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="flex-1 overflow-auto">
        <table v-if="columns.length > 0" class="w-full text-sm">
          <thead class="bg-slate-50 sticky top-0">
            <tr>
              <th class="px-3 py-2 text-left font-medium text-slate-600 border-b border-slate-200 w-10">
                <input type="checkbox" class="rounded" />
              </th>
              <th
                v-for="col in columns"
                :key="col.name"
                class="px-3 py-2 text-left font-medium text-slate-600 border-b border-slate-200 whitespace-nowrap"
              >
                <div class="flex items-center gap-1">
                  {{ col.name }}
                  <button class="text-slate-400 hover:text-slate-600">
                    <ArrowUpDown :size="12" />
                  </button>
                </div>
              </th>
              <th class="px-3 py-2 text-left font-medium text-slate-600 border-b border-slate-200 w-20">
                操作
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, index) in tableData"
              :key="index"
              class="hover:bg-slate-50 border-b border-slate-100"
            >
              <td class="px-3 py-2">
                <input type="checkbox" class="rounded" />
              </td>
              <td
                v-for="col in columns"
                :key="col.name"
                class="px-3 py-2 text-slate-700 max-w-xs truncate"
                :title="String(row[col.name])"
              >
                {{ row[col.name] }}
              </td>
              <td class="px-3 py-2">
                <div class="flex items-center gap-1">
                  <button class="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-indigo-600" title="编辑">
                    <Pencil :size="14" />
                  </button>
                  <button class="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-red-600" title="删除">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 空状态 -->
        <div v-else class="flex-1 flex items-center justify-center text-slate-400">
          <div class="text-center">
            <Table :size="48" class="mx-auto mb-3 opacity-50" />
            <p>选择左侧表查看数据</p>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="tableData.length > 0" class="p-3 border-t border-slate-200 flex items-center justify-between">
        <span class="text-xs text-slate-500">显示 1-{{ tableData.length }} 条，共 {{ tableData.length }} 条</span>
        <div class="flex items-center gap-1">
          <button class="px-2 py-1 text-xs rounded border border-slate-200 hover:bg-slate-50">上一页</button>
          <button class="px-2 py-1 text-xs rounded bg-indigo-600 text-white">1</button>
          <button class="px-2 py-1 text-xs rounded border border-slate-200 hover:bg-slate-50">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  Table, RefreshCw, ChevronRight, Plus, Pencil, Trash2,
  ArrowUpDown, Key, Hash, Type, Calendar, ToggleLeft
} from 'lucide-vue-next';

// ==========================================
// 类型定义
// ==========================================

interface TableColumn {
  name: string;
  type: string;
  pk?: boolean;
}

interface DbTable {
  name: string;
  rowCount: number;
  columns: TableColumn[];
}

interface TableRow {
  [key: string]: any;
}

// ==========================================
// Props & Emits
// ==========================================

defineProps<{
  tables: DbTable[];
  selectedTable: string | null;
  columns: TableColumn[];
  tableData: TableRow[];
  searchKeyword: string;
}>();

const emit = defineEmits<{
  (e: 'select', tableName: string): void;
  (e: 'refresh'): void;
  (e: 'update:searchKeyword', value: string): void;
}>();

// ==========================================
// 本地状态
// ==========================================

const expandedTables = ref<string[]>([]);

// ==========================================
// 方法
// ==========================================

const toggleExpand = (tableName: string) => {
  const index = expandedTables.value.indexOf(tableName);
  if (index > -1) {
    expandedTables.value.splice(index, 1);
  } else {
    expandedTables.value.push(tableName);
  }
};

const getColumnIcon = (type: string) => {
  if (type.includes('uuid') || type.includes('serial')) return Key;
  if (type.includes('int') || type.includes('bigint')) return Hash;
  if (type.includes('timestamp') || type.includes('date')) return Calendar;
  if (type.includes('bool')) return ToggleLeft;
  return Type;
};

const getColumnColor = (type: string) => {
  if (type.includes('uuid') || type.includes('serial')) return 'text-amber-500';
  if (type.includes('int') || type.includes('bigint')) return 'text-blue-500';
  if (type.includes('timestamp') || type.includes('date')) return 'text-purple-500';
  if (type.includes('bool')) return 'text-green-500';
  return 'text-slate-500';
};
</script>