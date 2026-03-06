<!--
  1. 页面简介 (Page Introduction)
  智研题库协作云 - 底层数据管理 (DbExplorer.vue)
  本页面是系统的底层数据管理模块，提供数据库表结构浏览、数据查询、系统配置等功能。
  用于管理员和开发者查看和管理系统底层数据。
-->

<template>
  <div class="min-h-screen bg-slate-50 pt-16 flex">
    <!-- 左侧标签栏 -->
    <aside class="w-56 bg-white border-r border-slate-200 flex-shrink-0">
      <div class="p-4 border-b border-slate-100">
        <div class="flex items-center gap-2">
          <HardDrive :size="18" class="text-slate-500" />
          <span class="font-bold text-slate-700">数据管理</span>
        </div>
      </div>
      <nav class="p-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all mb-1"
          :class="activeTab === tab.id
            ? 'bg-indigo-50 text-indigo-700 font-medium'
            : 'text-slate-600 hover:bg-slate-50'"
        >
          <component :is="tab.icon" :size="18" />
          <span>{{ tab.name }}</span>
        </button>
      </nav>
    </aside>

    <!-- 右侧内容区 -->
    <main class="flex-1 overflow-hidden flex flex-col">

      <!-- ==================== 数据表模块 ==================== -->
      <div v-if="activeTab === 'tables'" class="flex-1 flex overflow-hidden">
        <!-- 左侧：表列表面板 -->
        <div class="w-72 bg-white border-r border-slate-200 flex flex-col">
          <!-- 表列表头部 -->
          <div class="p-3 border-b border-slate-100 flex items-center justify-between">
            <span class="text-sm font-bold text-slate-700">数据库表</span>
            <button
              @click="refreshTables"
              class="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
              title="刷新"
            >
              <RefreshCw :size="14" />
            </button>
          </div>

          <!-- 表列表 -->
          <div class="flex-1 overflow-auto">
            <div
              v-for="table in dbTables"
              :key="table.name"
              class="border-b border-slate-100"
            >
              <!-- 表名行 -->
              <div
                @click="selectTable(table.name)"
                class="flex items-center gap-2 px-3 py-2.5 cursor-pointer transition-colors"
                :class="selectedTable === table.name ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-slate-50 text-slate-700'"
              >
                <ChevronRight
                  :size="14"
                  class="transition-transform"
                  :class="expandedTables.includes(table.name) ? 'rotate-90' : ''"
                  @click.stop="toggleTableExpand(table.name)"
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
              <span v-if="currentTableData.length > 0" class="text-xs text-slate-400">
                {{ currentTableData.length }} 行
              </span>
            </div>
            <div class="flex-1"></div>
            <div class="flex items-center gap-2">
              <input
                v-model="searchKeyword"
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
            <table v-if="currentTableColumns.length > 0" class="w-full text-sm">
              <thead class="bg-slate-50 sticky top-0">
                <tr>
                  <th class="px-3 py-2 text-left font-medium text-slate-600 border-b border-slate-200 w-10">
                    <input type="checkbox" class="rounded" />
                  </th>
                  <th
                    v-for="col in currentTableColumns"
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
                  v-for="(row, index) in currentTableData"
                  :key="index"
                  class="hover:bg-slate-50 border-b border-slate-100"
                >
                  <td class="px-3 py-2">
                    <input type="checkbox" class="rounded" />
                  </td>
                  <td
                    v-for="col in currentTableColumns"
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
          <div v-if="currentTableData.length > 0" class="p-3 border-t border-slate-200 flex items-center justify-between">
            <span class="text-xs text-slate-500">显示 1-{{ currentTableData.length }} 条，共 {{ currentTableData.length }} 条</span>
            <div class="flex items-center gap-1">
              <button class="px-2 py-1 text-xs rounded border border-slate-200 hover:bg-slate-50">上一页</button>
              <button class="px-2 py-1 text-xs rounded bg-indigo-600 text-white">1</button>
              <button class="px-2 py-1 text-xs rounded border border-slate-200 hover:bg-slate-50">下一页</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== 数据查询模块 ==================== -->
      <div v-if="activeTab === 'query'" class="flex-1 p-6 overflow-auto">
        <h3 class="font-bold text-slate-700 text-lg mb-4">SQL 查询</h3>
        <textarea
          v-model="queryText"
          rows="8"
          class="w-full px-4 py-3 bg-slate-900 text-green-400 font-mono text-sm rounded-xl border border-slate-700 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="SELECT * FROM questions LIMIT 10;"
        ></textarea>
        <div class="flex gap-3 mt-4">
          <button
            @click="executeQuery"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            <Play :size="16" class="inline mr-1" />
            执行查询
          </button>
          <button
            @click="queryText = ''"
            class="px-4 py-2 bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 transition-colors"
          >
            清空
          </button>
        </div>

        <!-- Query Result -->
        <div v-if="queryResult" class="mt-6">
          <h4 class="font-bold text-slate-700 mb-3">查询结果</h4>
          <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table class="w-full text-sm">
              <thead class="bg-slate-50">
                <tr>
                  <th
                    v-for="col in queryResultColumns"
                    :key="col"
                    class="px-4 py-2 text-left font-medium text-slate-600 border-b border-slate-200"
                  >
                    {{ col }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in queryResultData" :key="index" class="border-b border-slate-100 hover:bg-slate-50">
                  <td
                    v-for="col in queryResultColumns"
                    :key="col"
                    class="px-4 py-2 text-slate-700"
                  >
                    {{ row[col] }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ==================== 系统配置模块 ==================== -->
      <div v-if="activeTab === 'config'" class="flex-1 p-6 overflow-auto">
        <h3 class="font-bold text-slate-700 text-lg mb-4">系统配置项</h3>
        <div class="space-y-3">
          <div
            v-for="config in mockConfigs"
            :key="config.key"
            class="flex items-center justify-between p-4 bg-white rounded-xl border border-slate-200"
          >
            <div>
              <div class="font-medium text-slate-700">{{ config.key }}</div>
              <div class="text-sm text-slate-500">{{ config.description }}</div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm font-mono bg-slate-100 px-3 py-1 rounded border border-slate-200">
                {{ config.value }}
              </span>
              <button class="text-slate-400 hover:text-indigo-600 transition-colors">
                <Settings :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== 系统日志模块 ==================== -->
      <div v-if="activeTab === 'logs'" class="flex-1 p-6 overflow-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-slate-700 text-lg">系统日志</h3>
          <select
            v-model="logLevel"
            class="px-3 py-1.5 text-sm bg-white text-slate-600 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">全部级别</option>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
          </select>
        </div>

        <div class="space-y-2">
          <div
            v-for="(log, index) in filteredLogs"
            :key="index"
            class="flex items-start gap-3 p-3 bg-white rounded-lg border border-slate-200"
          >
            <span
              class="text-xs px-2 py-0.5 rounded font-mono"
              :class="getLogLevelClass(log.level)"
            >
              {{ log.level }}
            </span>
            <div class="flex-1">
              <div class="text-sm text-slate-700">{{ log.message }}</div>
              <div class="text-xs text-slate-400 mt-1">{{ log.timestamp }}</div>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：ref, computed (响应式编程)
 * - 图标库：lucide-vue-next (Lucide 图标集)
 */
import { ref, computed } from 'vue';
import {
  HardDrive, Table, Search, Settings, FileText,
  RefreshCw, Play, ChevronRight, Plus, Pencil, Trash2,
  ArrowUpDown, Key, Hash, Type, Calendar, ToggleLeft
} from 'lucide-vue-next';

// ==========================================
// 类型定义
// ==========================================

interface Tab {
  id: string;
  name: string;
  icon: any;
}

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

interface ConfigItem {
  key: string;
  value: string;
  description: string;
}

interface LogItem {
  level: 'INFO' | 'WARN' | 'ERROR';
  message: string;
  timestamp: string;
}

interface TableRow {
  [key: string]: any;
}

// ==========================================
// 响应式状态
// ==========================================

const tabs: Tab[] = [
  { id: 'query', name: '数据查询', icon: Search },
  { id: 'tables', name: '数据表', icon: Table },
  { id: 'config', name: '系统配置', icon: Settings },
  { id: 'logs', name: '系统日志', icon: FileText }
];

const activeTab = ref('query');
const queryText = ref('');
const logLevel = ref('all');
const searchKeyword = ref('');

// 数据表相关状态
const selectedTable = ref<string | null>(null);
const expandedTables = ref<string[]>([]);

// ==========================================
// 模拟数据库结构
// ==========================================

const dbTables: DbTable[] = [
  {
    name: 'users',
    rowCount: 156,
    columns: [
      { name: 'id', type: 'uuid', pk: true },
      { name: 'name', type: 'varchar' },
      { name: 'email', type: 'varchar' },
      { name: 'role', type: 'varchar' },
      { name: 'level', type: 'varchar' },
      { name: 'subject', type: 'varchar' },
      { name: 'created_at', type: 'timestamp' },
      { name: 'updated_at', type: 'timestamp' }
    ]
  },
  {
    name: 'questions',
    rowCount: 12453,
    columns: [
      { name: 'id', type: 'uuid', pk: true },
      { name: 'title', type: 'text' },
      { name: 'content', type: 'jsonb' },
      { name: 'subject', type: 'varchar' },
      { name: 'grade', type: 'varchar' },
      { name: 'difficulty', type: 'int' },
      { name: 'status', type: 'varchar' },
      { name: 'created_by', type: 'uuid' },
      { name: 'created_at', type: 'timestamp' }
    ]
  },
  {
    name: 'knowledge_points',
    rowCount: 892,
    columns: [
      { name: 'id', type: 'uuid', pk: true },
      { name: 'name', type: 'varchar' },
      { name: 'parent_id', type: 'uuid' },
      { name: 'subject', type: 'varchar' },
      { name: 'grade', type: 'varchar' },
      { name: 'level', type: 'int' },
      { name: 'path', type: 'varchar' }
    ]
  },
  {
    name: 'question_versions',
    rowCount: 45621,
    columns: [
      { name: 'id', type: 'uuid', pk: true },
      { name: 'question_id', type: 'uuid' },
      { name: 'version', type: 'int' },
      { name: 'content', type: 'jsonb' },
      { name: 'changed_by', type: 'uuid' },
      { name: 'changed_at', type: 'timestamp' }
    ]
  },
  {
    name: 'uploads',
    rowCount: 234,
    columns: [
      { name: 'id', type: 'uuid', pk: true },
      { name: 'filename', type: 'varchar' },
      { name: 'file_type', type: 'varchar' },
      { name: 'file_size', type: 'bigint' },
      { name: 'status', type: 'varchar' },
      { name: 'uploaded_by', type: 'uuid' },
      { name: 'created_at', type: 'timestamp' }
    ]
  },
  {
    name: 'system_logs',
    rowCount: 15678,
    columns: [
      { name: 'id', type: 'bigserial', pk: true },
      { name: 'level', type: 'varchar' },
      { name: 'message', type: 'text' },
      { name: 'user_id', type: 'uuid' },
      { name: 'ip_address', type: 'varchar' },
      { name: 'created_at', type: 'timestamp' }
    ]
  }
];

// ==========================================
// 模拟表数据
// ==========================================

const mockTableData: Record<string, TableRow[]> = {
  users: [
    { id: 'a1b2c3d4', name: '张三', email: 'zhangsan@example.com', role: 'teacher', level: '高中', subject: '数学', created_at: '2026-01-15 09:30:00', updated_at: '2026-03-01 14:20:00' },
    { id: 'e5f6g7h8', name: '李四', email: 'lisi@example.com', role: 'teacher', level: '初中', subject: '物理', created_at: '2026-01-20 10:15:00', updated_at: '2026-02-28 16:45:00' },
    { id: 'i9j0k1l2', name: '王五', email: 'wangwu@example.com', role: 'admin', level: null, subject: null, created_at: '2025-12-01 08:00:00', updated_at: '2026-03-05 11:30:00' },
    { id: 'm3n4o5p6', name: '赵六', email: 'zhaoliu@example.com', role: 'teacher', level: '高中', subject: '化学', created_at: '2026-02-01 13:45:00', updated_at: '2026-03-02 09:10:00' },
    { id: 'q7r8s9t0', name: '孙七', email: 'sunqi@example.com', role: 'teacher', level: '初中', subject: '语文', created_at: '2026-02-10 15:30:00', updated_at: '2026-03-03 17:00:00' }
  ],
  questions: [
    { id: 'q001', title: '求函数 f(x)=x²+2x-3 的最小值', content: '{"type": "calculation", "answer": "-4"}', subject: '数学', grade: '高一', difficulty: 2, status: 'published', created_by: 'a1b2c3d4', created_at: '2026-02-15 10:00:00' },
    { id: 'q002', title: '牛顿第二定律的应用', content: '{"type": "choice", "options": ["A", "B", "C", "D"]}', subject: '物理', grade: '高二', difficulty: 3, status: 'published', created_by: 'e5f6g7h8', created_at: '2026-02-16 14:30:00' },
    { id: 'q003', title: '氧化还原反应方程式配平', content: '{"type": "fill", "blanks": 3}', subject: '化学', grade: '高一', difficulty: 2, status: 'draft', created_by: 'm3n4o5p6', created_at: '2026-02-20 09:15:00' }
  ],
  knowledge_points: [
    { id: 'kp001', name: '函数与方程', parent_id: null, subject: '数学', grade: '高中', level: 1, path: '/函数与方程' },
    { id: 'kp002', name: '二次函数', parent_id: 'kp001', subject: '数学', grade: '高中', level: 2, path: '/函数与方程/二次函数' },
    { id: 'kp003', name: '牛顿运动定律', parent_id: null, subject: '物理', grade: '高中', level: 1, path: '/牛顿运动定律' }
  ],
  uploads: [
    { id: 'u001', filename: '高一数学试卷.docx', file_type: 'docx', file_size: 256000, status: 'completed', uploaded_by: 'a1b2c3d4', created_at: '2026-03-01 09:00:00' },
    { id: 'u002', filename: '物理题库.xlsx', file_type: 'xlsx', file_size: 128000, status: 'processing', uploaded_by: 'e5f6g7h8', created_at: '2026-03-05 14:30:00' }
  ],
  system_logs: [
    { id: 1, level: 'INFO', message: '用户 admin 登录成功', user_id: 'i9j0k1l2', ip_address: '192.168.1.100', created_at: '2026-03-06 09:45:23' },
    { id: 2, level: 'INFO', message: '题库同步任务完成', user_id: null, ip_address: null, created_at: '2026-03-06 09:42:15' },
    { id: 3, level: 'WARN', message: '知识点树存在孤立节点', user_id: null, ip_address: null, created_at: '2026-03-06 09:38:00' }
  ],
  question_versions: [
    { id: 'qv001', question_id: 'q001', version: 1, content: '{"title": "原始版本"}', changed_by: 'a1b2c3d4', changed_at: '2026-02-15 10:00:00' },
    { id: 'qv002', question_id: 'q001', version: 2, content: '{"title": "修订版本"}', changed_by: 'a1b2c3d4', changed_at: '2026-02-20 15:30:00' }
  ]
};

// ==========================================
// 模拟配置和日志数据
// ==========================================

const mockConfigs: ConfigItem[] = [
  { key: 'APP_VERSION', value: '2.4.0', description: '系统版本号' },
  { key: 'MAX_UPLOAD_SIZE', value: '50MB', description: '最大上传文件大小' },
  { key: 'SESSION_TIMEOUT', value: '3600s', description: '会话超时时间' },
  { key: 'AI_MODEL', value: 'claude-sonnet-4.6', description: '默认 AI 模型' }
];

const mockLogs: LogItem[] = [
  { level: 'INFO', message: '用户 admin 登录成功', timestamp: '2026-03-06 09:45:23' },
  { level: 'INFO', message: '题库同步任务完成，新增 23 题', timestamp: '2026-03-06 09:42:15' },
  { level: 'WARN', message: '知识点树存在孤立节点', timestamp: '2026-03-06 09:38:00' },
  { level: 'ERROR', message: 'AI 服务连接超时', timestamp: '2026-03-06 09:30:45' },
  { level: 'INFO', message: '系统备份完成', timestamp: '2026-03-06 09:00:00' }
];

// ==========================================
// 查询结果相关
// ==========================================

const queryResultColumns = ref<string[]>([]);
const queryResultData = ref<TableRow[]>([]);

// ==========================================
// 计算属性
// ==========================================

const filteredLogs = computed(() => {
  if (logLevel.value === 'all') return mockLogs;
  return mockLogs.filter(log => log.level === logLevel.value);
});

const currentTableColumns = computed(() => {
  if (!selectedTable.value) return [];
  const table = dbTables.find(t => t.name === selectedTable.value);
  return table?.columns || [];
});

const currentTableData = computed(() => {
  if (!selectedTable.value) return [];
  return mockTableData[selectedTable.value] || [];
});

// ==========================================
// 交互方法
// ==========================================

const refreshTables = () => {
  console.log('Refreshing tables...');
};

const selectTable = (tableName: string) => {
  selectedTable.value = tableName;
};

const toggleTableExpand = (tableName: string) => {
  const index = expandedTables.value.indexOf(tableName);
  if (index > -1) {
    expandedTables.value.splice(index, 1);
  } else {
    expandedTables.value.push(tableName);
  }
};

const executeQuery = () => {
  if (!queryText.value.trim()) return;
  // 模拟查询结果
  queryResultColumns.value = ['id', 'title', 'subject', 'grade', 'difficulty'];
  queryResultData.value = [
    { id: 'q001', title: '求函数 f(x)=x²+2x-3 的最小值', subject: '数学', grade: '高一', difficulty: 2 },
    { id: 'q002', title: '牛顿第二定律的应用', subject: '物理', grade: '高二', difficulty: 3 }
  ];
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

const getLogLevelClass = (level: string) => {
  switch (level) {
    case 'INFO': return 'bg-blue-100 text-blue-600';
    case 'WARN': return 'bg-amber-100 text-amber-600';
    case 'ERROR': return 'bg-red-100 text-red-600';
    default: return 'bg-slate-100 text-slate-600';
  }
};
</script>

<style scoped>
/* 组件样式使用 Tailwind CSS */
</style>