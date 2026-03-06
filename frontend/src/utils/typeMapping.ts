/**
 * 题型映射工具
 * 统一处理所有题型值的中文映射（数字值）
 */

/**
 * 题型类型定义（数字值）
 */
export type QuestionType = 1 | 2 | 3 | 4 | 9;

/**
 * 题型常量
 */
export const QUESTION_TYPE = {
  SINGLE_CHOICE: 1,      // 选择题
  FILL_BLANK: 2,         // 填空题
  MULTIPLE_CHOICE: 3,    // 多选题
  TRUE_FALSE: 4,         // 判断题
  SHORT_ANSWER: 9,       // 解答题
} as const;

/**
 * 题型中文映射
 */
export const TYPE_LABELS: Record<number, string> = {
  1: '选择题',
  2: '填空题',
  3: '多选题',
  4: '判断题',
  9: '解答题',
};

/**
 * 题型颜色映射（用于 UI 样式）
 */
export const TYPE_COLORS: Record<number, string> = {
  1: 'text-blue-600',
  3: 'text-orange-600',
  2: 'text-emerald-600',
  4: 'text-amber-600',
  9: 'text-purple-600',
};

/**
 * 题型背景色映射（用于标签样式）
 */
export const TYPE_BG_COLORS: Record<number, string> = {
  1: 'bg-blue-50',
  3: 'bg-orange-50',
  2: 'bg-emerald-50',
  4: 'bg-amber-50',
  9: 'bg-purple-50',
};

/**
 * 获取题型中文标签
 * @param type 题型数字值
 * @returns 中文标签
 */
export function getTypeLabel(type: number | string | undefined | null): string {
  if (type === undefined || type === null) return '未知';
  return TYPE_LABELS[Number(type)] || '未知';
}

/**
 * 获取题型颜色类名
 * @param type 题型数字值
 * @returns Tailwind 颜色类名
 */
export function getTypeColor(type: number | string | undefined | null): string {
  if (type === undefined || type === null) return 'text-slate-400';
  return TYPE_COLORS[Number(type)] || 'text-slate-400';
}

/**
 * 获取题型背景色类名
 * @param type 题型数字值
 * @returns Tailwind 背景色类名
 */
export function getTypeBgColor(type: number | string | undefined | null): string {
  if (type === undefined || type === null) return 'bg-slate-100';
  return TYPE_BG_COLORS[Number(type)] || 'bg-slate-100';
}

/**
 * 获取题型选项列表
 * @returns 题型选项列表
 */
export function getTypeOptions(): { value: number; label: string }[] {
  return [
    { value: 1, label: '选择题' },
    { value: 3, label: '多选题' },
    { value: 2, label: '填空题' },
    { value: 4, label: '判断题' },
    { value: 9, label: '解答题' },
  ];
}