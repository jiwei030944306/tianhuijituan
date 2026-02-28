<template>
  <el-dialog
    v-model="visible"
    title="文件上传冲突"
    width="500px"
    :close-on-click-modal="false"
    :show-close="false"
  >
    <div class="conflict-content">
      <el-alert
        type="warning"
        :closable="false"
        show-icon
      >
        <template #title>
          {{ conflictInfo.message }}
        </template>
      </el-alert>
      
      <div class="existing-info" v-if="conflictInfo.existing_record">
        <h4>已有文件信息：</h4>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="名称">
            {{ conflictInfo.existing_record.display_name }}
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">
            {{ formatTime(conflictInfo.existing_record.uploaded_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="题目数量">
            {{ conflictInfo.existing_record.file_count }} 道
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="warning" @click="handleRename">
        重命名上传
      </el-button>
      <el-button type="danger" @click="handleOverwrite">
        覆盖已有文件
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface ExistingRecordInfo {
  batch_id: string;
  display_name: string;
  uploaded_at: string;
  file_count: number;
}

interface ConflictInfo {
  conflict: boolean;
  existing_record?: ExistingRecordInfo;
  message: string;
  options: string[];
}

const props = defineProps<{
  modelValue: boolean;
  conflictInfo: ConflictInfo;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'resolve', action: 'overwrite' | 'rename' | 'cancel'): void;
}>();

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const handleOverwrite = () => {
  emit('resolve', 'overwrite');
  visible.value = false;
};

const handleRename = () => {
  emit('resolve', 'rename');
  visible.value = false;
};

const handleCancel = () => {
  emit('resolve', 'cancel');
  visible.value = false;
};

const formatTime = (time: string) => {
  try {
    return new Date(time).toLocaleString('zh-CN');
  } catch {
    return time;
  }
};
</script>

<style scoped>
.conflict-content {
  padding: 10px 0;
}

.existing-info {
  margin-top: 20px;
}

.existing-info h4 {
  margin-bottom: 10px;
  color: #606266;
}
</style>
