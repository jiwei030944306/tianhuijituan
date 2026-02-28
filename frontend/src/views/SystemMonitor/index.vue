<script setup lang="ts">
/**
 * 系统监控页面
 * 
 * 展示后端服务健康状态、API性能指标、错误日志和数据库状态
 */
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh, Delete, Monitor, Timer, Warning, Document } from '@element-plus/icons-vue';
import { monitorApi } from '@/api/monitor';
import type {
  HealthResponse,
  PerformanceResponse,
  ErrorLogResponse,
  DatabaseResponse,
  MonitorCard
} from '@/types/monitor';

// ==================== 状态定义 ====================

const loading = ref(false);
const health = ref<HealthResponse | null>(null);
const performance = ref<PerformanceResponse | null>(null);
const errors = ref<ErrorLogResponse | null>(null);
const database = ref<DatabaseResponse | null>(null);
const lastRefresh = ref<string | null>(null);
const autoRefresh = ref(true);
const refreshInterval = ref<number | null>(null);
const selectedHours = ref(1);

// ==================== 计算属性 ====================

/** 顶部状态卡片 */
const statusCards = computed<MonitorCard[]>(() => {
  const cards: MonitorCard[] = [];
  
  // 服务状态卡片
  if (health.value) {
    const statusMap: Record<string, { text: string; color: string }> = {
      healthy: { text: '正常', color: 'success' },
      degraded: { text: '降级', color: 'warning' },
      unhealthy: { text: '异常', color: 'danger' }
    };
    const statusInfo = statusMap[health.value.status] || { text: '未知', color: 'info' };
    cards.push({
      title: '服务状态',
      value: statusInfo.text,
      status: statusInfo.color as 'success' | 'warning' | 'danger' | 'info',
      icon: 'Monitor',
      description: `运行时间: ${formatUptime(health.value.uptime_seconds)}`
    });
  }
  
  // 请求数量卡片
  if (performance.value) {
    cards.push({
      title: '请求数量',
      value: performance.value.summary.total_requests,
      unit: '次',
      status: 'info',
      icon: 'Timer',
      description: `最近 ${selectedHours.value} 小时`
    });
  }
  
  // 平均响应时间卡片
  if (performance.value) {
    const avgMs = performance.value.summary.avg_response_time_ms;
    let status: 'success' | 'warning' | 'danger' | 'info' = 'success';
    if (avgMs > 500) status = 'warning';
    if (avgMs > 1000) status = 'danger';
    
    cards.push({
      title: '平均响应',
      value: avgMs.toFixed(0),
      unit: 'ms',
      status,
      icon: 'Timer',
      description: `最大: ${performance.value.summary.max_ms?.toFixed(0) || 0}ms`
    });
  }
  
  // 错误率卡片
  if (performance.value) {
    const errorRate = performance.value.summary.error_rate_percent;
    let status: 'success' | 'warning' | 'danger' | 'info' = 'success';
    if (errorRate > 1) status = 'warning';
    if (errorRate > 5) status = 'danger';
    
    cards.push({
      title: '错误率',
      value: errorRate.toFixed(1),
      unit: '%',
      status,
      icon: 'Warning',
      description: `${performance.value.summary.slow_requests_count} 慢请求`
    });
  }
  
  return cards;
});

// ==================== 方法 ====================

/** 格式化运行时间 */
function formatUptime(seconds: number): string {
  if (seconds < 60) return `${Math.floor(seconds)}秒`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时`;
  return `${Math.floor(seconds / 86400)}天`;
}

/** 格式化时间 */
function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

/** 刷新所有数据 */
async function refreshAll() {
  loading.value = true;
  try {
    const data = await monitorApi.getAll(selectedHours.value);
    health.value = data.health;
    performance.value = data.performance;
    errors.value = data.errors;
    database.value = data.database;
    lastRefresh.value = new Date().toLocaleString('zh-CN');
  } catch (error) {
    console.error('获取监控数据失败:', error);
    ElMessage.error('获取监控数据失败');
  } finally {
    loading.value = false;
  }
}

/** 清理过期日志 */
async function handleClearLogs() {
  try {
    const result = await monitorApi.clearLogs(7);
    ElMessage.success(result.message);
    await refreshAll();
  } catch (error) {
    console.error('清理日志失败:', error);
    ElMessage.error('清理日志失败');
  }
}

/** 获取状态标签类型 */
function getStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  if (status === 'ok' || status === 'healthy') return 'success';
  if (status === 'warning' || status === 'degraded') return 'warning';
  if (status === 'error' || status === 'unhealthy') return 'danger';
  return 'info';
}

/** 启动自动刷新 */
function startAutoRefresh() {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value);
  }
  refreshInterval.value = window.setInterval(() => {
    if (autoRefresh.value) {
      refreshAll();
    }
  }, 30000); // 30秒刷新一次
}

// ==================== 生命周期 ====================

onMounted(() => {
  refreshAll();
  startAutoRefresh();
});

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value);
  }
});
</script>

<template>
  <div class="system-monitor">
    <!-- 页面标题 -->
    <div class="monitor-header">
      <h2>
        <el-icon><Monitor /></el-icon>
        系统监控
      </h2>
      <div class="header-actions">
        <el-select v-model="selectedHours" size="small" style="width: 120px" @change="refreshAll">
          <el-option :value="1" label="最近1小时" />
          <el-option :value="6" label="最近6小时" />
          <el-option :value="24" label="最近24小时" />
        </el-select>
        <el-switch v-model="autoRefresh" active-text="自动刷新" />
        <el-button :icon="Refresh" @click="refreshAll" :loading="loading">刷新</el-button>
        <el-button :icon="Delete" @click="handleClearLogs" type="danger" plain>清理日志</el-button>
      </div>
    </div>

    <!-- 最后刷新时间 -->
    <div v-if="lastRefresh" class="last-refresh">
      最后更新: {{ lastRefresh }}
    </div>

    <!-- 状态卡片 -->
    <div class="status-cards">
      <el-card v-for="(card, index) in statusCards" :key="index" class="status-card" :class="`status-${card.status}`">
        <div class="card-content">
          <div class="card-title">{{ card.title }}</div>
          <div class="card-value">
            {{ card.value }}<span v-if="card.unit" class="unit">{{ card.unit }}</span>
          </div>
          <div v-if="card.description" class="card-description">{{ card.description }}</div>
        </div>
      </el-card>
    </div>

    <!-- 主要内容区域 -->
    <div class="monitor-content">
      <!-- 左侧：API性能 + 数据库状态 -->
      <div class="left-panel">
        <!-- API 性能指标 -->
        <el-card class="panel-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Timer /></el-icon> API 性能指标</span>
            </div>
          </template>
          <el-table v-if="performance?.endpoints?.length" :data="performance.endpoints" size="small" max-height="300">
            <el-table-column prop="path" label="接口路径" min-width="150" show-overflow-tooltip />
            <el-table-column prop="method" label="方法" width="80" />
            <el-table-column prop="count" label="请求数" width="80" />
            <el-table-column label="平均耗时" width="100">
              <template #default="{ row }">
                <span :class="{ 'text-warning': row.avg_ms > 500, 'text-danger': row.avg_ms > 1000 }">
                  {{ row.avg_ms.toFixed(0) }}ms
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="max_ms" label="最大耗时" width="100">
              <template #default="{ row }">{{ row.max_ms.toFixed(0) }}ms</template>
            </el-table-column>
            <el-table-column prop="error_count" label="错误数" width="80">
              <template #default="{ row }">
                <span :class="{ 'text-danger': row.error_count > 0 }">{{ row.error_count }}</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无性能数据" />
        </el-card>

        <!-- 数据库状态 -->
        <el-card class="panel-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> 数据库状态</span>
              <el-tag v-if="database" :type="getStatusType(database.status)" size="small">
                {{ database.status === 'connected' ? '已连接' : '断开' }}
              </el-tag>
            </div>
          </template>
          <div v-if="database" class="database-info">
            <div class="info-row">
              <span class="label">连接延迟:</span>
              <span class="value">{{ database.latency_ms.toFixed(2) }}ms</span>
            </div>
            <div class="info-row">
              <span class="label">数据库大小:</span>
              <span class="value">{{ database.db_size_mb.toFixed(2) }} MB</span>
            </div>
            <el-divider content-position="left">表统计</el-divider>
            <el-table :data="database.tables" size="small" max-height="200">
              <el-table-column prop="name" label="表名" />
              <el-table-column prop="row_count" label="记录数" width="100" />
            </el-table>
          </div>
          <el-empty v-else description="暂无数据库状态" />
        </el-card>
      </div>

      <!-- 右侧：错误日志 -->
      <div class="right-panel">
        <el-card class="panel-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Warning /></el-icon> 错误日志</span>
              <el-tag v-if="errors" type="info" size="small">共 {{ errors.total }} 条</el-tag>
            </div>
          </template>
          <div v-if="errors?.items?.length" class="error-list">
            <div v-for="item in errors.items" :key="item.id" class="error-item">
              <div class="error-header">
                <el-tag :type="item.status_code >= 500 ? 'danger' : 'warning'" size="small">
                  {{ item.status_code }}
                </el-tag>
                <span class="error-method">{{ item.method }}</span>
                <span class="error-path">{{ item.path }}</span>
                <span class="error-time">{{ formatTime(item.timestamp) }}</span>
              </div>
              <div class="error-message">{{ item.error_message }}</div>
              <div v-if="item.error_stack" class="error-stack">
                <el-collapse>
                  <el-collapse-item title="查看堆栈">
                    <pre>{{ item.error_stack }}</pre>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无错误日志" />
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.system-monitor {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.monitor-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.last-refresh {
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.status-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-success {
  border-left: 4px solid #67c23a;
}

.status-warning {
  border-left: 4px solid #e6a23c;
}

.status-danger {
  border-left: 4px solid #f56c6c;
}

.status-info {
  border-left: 4px solid #409eff;
}

.card-content {
  text-align: center;
  padding: 8px;
}

.card-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.card-value .unit {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
  margin-left: 4px;
}

.card-description {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.monitor-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.panel-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-warning {
  color: #e6a23c;
}

.text-danger {
  color: #f56c6c;
}

.database-info {
  padding: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: #606266;
}

.info-row .value {
  font-weight: 500;
  color: #303133;
}

.error-list {
  max-height: 500px;
  overflow-y: auto;
}

.error-item {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.error-item:last-child {
  border-bottom: none;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.error-method {
  font-weight: 500;
  color: #409eff;
}

.error-path {
  flex: 1;
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.error-time {
  font-size: 12px;
  color: #909399;
}

.error-message {
  font-size: 13px;
  color: #303133;
  background-color: #fef0f0;
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.error-stack pre {
  font-size: 11px;
  background-color: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .status-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .monitor-content {
    grid-template-columns: 1fr;
  }
  
  .status-cards {
    grid-template-columns: 1fr;
  }
  
  .monitor-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    flex-wrap: wrap;
  }
}
</style>