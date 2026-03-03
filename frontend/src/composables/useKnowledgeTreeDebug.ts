/**
 * 知识树调试 Composable
 * 使用方法:
 * import { useKnowledgeTreeDebug } from '@/composables/useKnowledgeTreeDebug';
 *
 * // 在 setup 中使用
 * useKnowledgeTreeDebug({
 *   knowledgeTree,      // ref<KnowledgeNode[]>
 *   getKnowledgeTree,   // function
 *   knowledgeGroups     // computed
 * });
 */

import { watch, onMounted, type Ref, type ComputedRef } from 'vue';
import type { KnowledgeNode } from '@/components/common/KnowledgePointSelector.vue';

interface DebugOptions {
  knowledgeTree: Ref<KnowledgeNode[]>;
  knowledgeGroups?: ComputedRef<any[]>;
  currentSubject?: Ref<string> | string;
  currentGrade?: Ref<string> | string;
  getKnowledgeTree?: (subject: string, educationLevel: string) => KnowledgeNode[];
}

export function useKnowledgeTreeDebug(options: DebugOptions) {
  const { knowledgeTree, knowledgeGroups, currentSubject, currentGrade, getKnowledgeTree } = options;

  // 调试日志函数
  const logDebugInfo = () => {
    console.group('🔍 [KnowledgeTree Debug]');

    // 1. 检查 knowledgeTree.value
    console.group('1️⃣ knowledgeTree ref');
    console.log('knowledgeTree:', knowledgeTree);
    console.log('knowledgeTree.value:', knowledgeTree.value);
    console.log('类型:', typeof knowledgeTree.value);
    console.log('是数组?:', Array.isArray(knowledgeTree.value));
    console.log('长度:', knowledgeTree.value?.length);

    if (knowledgeTree.value?.length > 0) {
      console.log('第一项:', knowledgeTree.value[0]);
      console.log('结构预览:', knowledgeTree.value.map(n => ({
        id: n.id,
        name: n.name,
        childrenCount: n.children?.length || 0
      })));
    } else {
      console.warn('⚠️ knowledgeTree.value 为空数组!');
    }
    console.groupEnd();

    // 2. 检查 getKnowledgeTree 调用
    console.group('2️⃣ getKnowledgeTree 函数');
    if (getKnowledgeTree) {
      const subject = typeof currentSubject === 'string' ? currentSubject : currentSubject?.value;
      const grade = typeof currentGrade === 'string' ? currentGrade : currentGrade?.value;

      console.log('当前学科:', subject);
      console.log('当前年级:', grade);

      // 确定学段
      const educationLevel = (grade === 'junior' || grade?.includes('七') || grade?.includes('八') || grade?.includes('九'))
        ? '初中'
        : '高中';
      console.log('计算学段:', educationLevel);

      // 直接调用 getKnowledgeTree 查看返回值
      const result = getKnowledgeTree(subject || '数学', educationLevel);
      console.log('getKnowledgeTree 返回值:', result);
      console.log('返回值长度:', result?.length);
    } else {
      console.log('getKnowledgeTree 函数未提供');
    }
    console.groupEnd();

    // 3. 检查 knowledgeGroups computed
    console.group('3️⃣ knowledgeGroups computed');
    if (knowledgeGroups) {
      console.log('knowledgeGroups:', knowledgeGroups);
      console.log('knowledgeGroups.value:', knowledgeGroups.value);
      console.log('长度:', knowledgeGroups.value?.length);

      if (knowledgeGroups.value?.length > 0) {
        console.log('第一项:', knowledgeGroups.value[0]);
      } else {
        console.warn('⚠️ knowledgeGroups.value 为空数组!');
      }
    } else {
      console.log('knowledgeGroups 未提供');
    }
    console.groupEnd();

    console.groupEnd();
  };

  // 挂载到 window 便于控制台调试
  onMounted(() => {
    (window as any).__KNOWLEDGE_TREE_DEBUG__ = {
      ...options,
      refresh: logDebugInfo
    };
    console.log('💡 知识树调试工具已挂载到 window.__KNOWLEDGE_TREE_DEBUG__');
    console.log('   在控制台运行 window.__KNOWLEDGE_TREE_DEBUG__.refresh() 重新检查');
  });

  // 监听变化
  watch(() => knowledgeTree.value, (newVal, oldVal) => {
    console.group('[KnowledgeTree Watch]');
    console.log('knowledgeTree 变化:');
    console.log('  旧值长度:', oldVal?.length);
    console.log('  新值长度:', newVal?.length);
    console.log('  新值:', newVal);
    console.groupEnd();
  }, { immediate: true, deep: true });

  // 立即输出一次
  onMounted(() => {
    setTimeout(logDebugInfo, 0);
  });

  return {
    logDebugInfo,
    refresh: logDebugInfo
  };
}

export default useKnowledgeTreeDebug;
