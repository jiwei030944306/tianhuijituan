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
      <!-- 数据查询模块 -->
      <QueryPanel
        v-if="activeTab === 'query'"
        v-model:query-text="queryText"
      />

      <!-- 数据表模块 -->
      <TableExplorer
        v-if="activeTab === 'tables'"
        :tables="dbTables"
        :selected-table="selectedTable"
        :columns="currentTableColumns"
        :table-data="currentTableData"
        v-model:search-keyword="searchKeyword"
        @select="selectTable"
        @refresh="refreshTables"
      />

      <!-- 系统配置模块 -->
      <SystemConfig
        v-if="activeTab === 'config'"
        :configs="mockConfigs"
      />

      <!-- 系统日志模块 -->
      <SystemLogs
        v-if="activeTab === 'logs'"
        :logs="filteredLogs"
        v-model:level="logLevel"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
/**
 * 4. 引用挂载说明 (Reference & Mounting)
 * - Vue 核心：ref, computed (响应式编程)
 * - 图标库：lucide-vue-next (Lucide 图标集)
 * - 子组件：TableExplorer, QueryPanel, SystemConfig, SystemLogs
 */
import { ref, computed } from 'vue';
import { HardDrive, Table, Search, Settings, FileText } from 'lucide-vue-next';

// 子组件
import TableExplorer from './DbExplorer/TableExplorer.vue';
import QueryPanel from './DbExplorer/QueryPanel.vue';
import SystemConfig from './DbExplorer/SystemConfig.vue';
import SystemLogs from './DbExplorer/SystemLogs.vue';

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
const queryText = ref('SELECT * FROM questions LIMIT 10');
const logLevel = ref('all');
const searchKeyword = ref('');
const selectedTable = ref<string | null>(null);

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
</script>

<style scoped>
/* 组件样式使用 Tailwind CSS */
</style>