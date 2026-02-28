/**
 * 知识点配置索引
 * 根据学科和学段导出对应的知识点树
 */

import type { KnowledgeNode } from '@/components/common/KnowledgePointSelector.vue';
import { juniorMathKnowledgeTree } from './junior-math';

// 知识点配置映射表
// key 格式: `${subject}_${educationLevel}`
const knowledgeTreeMap: Record<string, KnowledgeNode[]> = {
  '数学_初中': juniorMathKnowledgeTree,
  // 后续添加其他学科学段的知识点配置
  // '数学_高中': seniorMathKnowledgeTree,
  // '语文_初中': juniorChineseKnowledgeTree,
  // ...
};

/**
 * 根据学科和学段获取知识点树
 * @param subject 学科
 * @param educationLevel 学段
 * @returns 知识点树，如果没有对应配置则返回空数组
 */
export function getKnowledgeTree(subject?: string, educationLevel?: string): KnowledgeNode[] {
  if (!subject || !educationLevel) {
    return [];
  }
  const key = `${subject}_${educationLevel}`;
  return knowledgeTreeMap[key] || [];
}

export type { KnowledgeNode };
