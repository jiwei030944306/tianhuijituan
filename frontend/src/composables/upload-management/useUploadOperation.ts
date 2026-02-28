/**
 * 上传操作逻辑 Composable
 * 职责: 文件上传、冲突检测、进度管理
 */
import { ref } from 'vue';
import type { Ref } from 'vue';

// 类型定义
export interface ConflictInfo {
  conflict: boolean;
  existing_record?: {
    batch_id: string;
    display_name: string;
    uploaded_at: string;
    file_count: number;
  };
  message: string;
  options: string[];
}

export interface ContextStore {
  subject?: string;
  grade?: string;
}

export function useUploadOperation(
  contextInfo: {
    folderCode: () => string;
    currentSubject: () => string;
    currentGrade: () => string;
    currentTeacher: () => string;
    contextStore: ContextStore;
  },
  addLog: (msg: string, level: string) => void,
  refreshHistory: () => Promise<void>,
  debuggerRef?: Ref<any>
) {
  // 状态
  const files = ref<File[]>([]);
  const uploading = ref(false);
  const progress = ref(0);
  const uploadComplete = ref(false);
  const fileInputRef = ref<HTMLInputElement | null>(null);

  // 冲突相关
  const conflictInfo = ref<ConflictInfo>({ conflict: false, message: '', options: [] });
  const showConflictDialog = ref(false);
  const pendingFile = ref<File | null>(null);
  const displayName = ref('');
  const pendingDisplayName = ref('');
  const pendingConflictAction = ref('new');
  let resolvePendingFile: ((value: void) => void) | null = null;

  // 文件选择
  const handleFileSelect = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      const newFiles = Array.from(target.files).filter(f =>
        f.name.endsWith('.zip') || f.name.endsWith('.json')
      );
      if (newFiles.length === 0) {
        addLog('仅支持 .zip 和 .json 格式文件', 'warning');
        return;
      }
      files.value.push(...newFiles);
      uploadComplete.value = false;
      displayName.value = newFiles[0].name.replace(/\.[^/.]+$/, '');
      target.value = '';
    }
  };

  // 移除文件
  const removeFile = (index: number) => {
    files.value.splice(index, 1);
  };

  // 清空文件
  const clearFiles = () => {
    files.value = [];
  };

  // 执行上传
  const performUpload = async (file: File, conflictAction: string, folderDisplayName?: string) => {
    const formData = new FormData();
    formData.append('json_file', file);
    formData.append('folder_name', folderDisplayName || displayName.value || file.name.replace(/\.[^/.]+$/, ''));
    formData.append('subject', contextInfo.currentSubject());
    formData.append('subject_code', contextInfo.contextStore.subject || '');
    formData.append('grade', contextInfo.contextStore.grade === 'senior' ? '11' : '8');
    formData.append('education_level', contextInfo.currentGrade());
    formData.append('folder_code', contextInfo.folderCode());
    formData.append('teacher_name', contextInfo.currentTeacher());
    formData.append('conflict_action', conflictAction);

    addLog(`开始上传: ${file.name}`, 'info');
    debuggerRef?.value?.logUploadRequest(formData);

    const uploadStartTime = Date.now();
    const response = await fetch('/api/questions/upload-folder', {
      method: 'POST',
      body: formData
    });
    const uploadDuration = Date.now() - uploadStartTime;

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '上传失败');
    }

    const result = await response.json();
    debuggerRef?.value?.logUploadResponse(result, uploadDuration);

    addLog(`上传成功: ${result.batch_id}`, 'success');

    await refreshHistory();
  };

  // 开始上传
  const handleUpload = async () => {
    if (files.value.length === 0) return;

    if (!contextInfo.folderCode() || contextInfo.folderCode() === '-') {
      addLog('环境信息不完整，请重新选择学科学段', 'error');
      return;
    }

    if (!contextInfo.currentTeacher() || contextInfo.currentTeacher() === '未知教师') {
      addLog('未登录用户无法上传文件', 'error');
      return;
    }

    uploading.value = true;
    progress.value = 0;
    uploadComplete.value = false;

    if (debuggerRef?.value) {
      debuggerRef.value.clearEntries();
    }

    addLog(`开始处理 ${files.value.length} 个文件`, 'info');

    try {
      for (let i = 0; i < files.value.length; i++) {
        const file = files.value[i];
        const currentDisplayName = file.name.replace(/\.[^/.]+$/, '');

        addLog(`[${i + 1}/${files.value.length}] 处理文件: ${file.name}`, 'info');

        addLog(`[${i + 1}/${files.value.length}] 开始冲突检测...`, 'info');
        debuggerRef?.value?.logInfo('冲突检测', `开始冲突检测请求 (${i + 1}/${files.value.length})`, {
          original_filename: file.name,
          folder_code: contextInfo.folderCode(),
          teacher_name: contextInfo.currentTeacher()
        });

        const checkResponse = await fetch('/api/questions/check-conflict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            original_filename: file.name,
            folder_code: contextInfo.folderCode(),
            teacher_name: contextInfo.currentTeacher()
          })
        });

        if (!checkResponse.ok) {
          throw new Error(`冲突检测失败: ${file.name}`);
        }

        const conflictData = await checkResponse.json();
        debuggerRef?.value?.logConflictCheck(
          { original_filename: file.name },
          conflictData,
          ((i + 1) / files.value.length) * 100
        );

        let conflictAction = 'new';
        let actualDisplayName = currentDisplayName;

        if (conflictData.conflict) {
          addLog(`[${i + 1}/${files.value.length}] 发现冲突: ${conflictData.message}`, 'warning');

          uploading.value = false;
          conflictInfo.value = conflictData;
          showConflictDialog.value = true;
          pendingFile.value = file;
          pendingDisplayName.value = currentDisplayName;

          await new Promise<void>((resolve) => {
            resolvePendingFile = resolve;
          });

          if (!pendingFile.value) {
            addLog(`[${i + 1}/${files.value.length}] 用户取消上传该文件`, 'warning');
            continue;
          }

          conflictAction = pendingConflictAction.value;
          actualDisplayName = pendingDisplayName.value;
        } else {
          addLog(`[${i + 1}/${files.value.length}] 无冲突，继续上传`, 'success');
        }

        addLog(`[${i + 1}/${files.value.length}] 开始上传...`, 'info');
        await performUpload(file, conflictAction, actualDisplayName);

        progress.value = ((i + 1) / files.value.length) * 100;
        addLog(`[${i + 1}/${files.value.length}] 处理完成`, 'success');
      }

      addLog('所有文件处理完成', 'success');
      uploadComplete.value = true;

    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      addLog(`处理失败: ${message}`, 'error');
      debuggerRef?.value?.logUploadError(error, '上传处理');
    } finally {
      uploading.value = false;
    }
  };

  // 冲突解决回调
  const handleConflictResolve = async (action: 'overwrite' | 'rename' | 'cancel') => {
    showConflictDialog.value = false;

    if (action === 'cancel') {
      addLog('用户取消上传该文件', 'info');
      pendingFile.value = null;
      if (resolvePendingFile) {
        resolvePendingFile();
        resolvePendingFile = null;
      }
      return;
    }

    if (action === 'rename') {
      const newName = prompt('请输入新的文件夹名称:', pendingDisplayName.value + '_副本');
      if (newName) {
        pendingDisplayName.value = newName;
      } else {
        pendingFile.value = null;
        if (resolvePendingFile) {
          resolvePendingFile();
          resolvePendingFile = null;
        }
        return;
      }
    }

    pendingConflictAction.value = action;

    uploading.value = true;
    if (resolvePendingFile) {
      resolvePendingFile();
      resolvePendingFile = null;
    }
  };

  return {
    // 状态
    files,
    uploading,
    progress,
    uploadComplete,
    fileInputRef,
    displayName,

    // 冲突相关
    conflictInfo,
    showConflictDialog,
    pendingFile,
    pendingDisplayName,
    pendingConflictAction,

    // 方法
    handleFileSelect,
    removeFile,
    clearFiles,
    handleUpload,
    performUpload,
    handleConflictResolve,
  };
}
