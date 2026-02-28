/**
 * 题型映射工具
 * 统一处理所有题型值的中文映射
 */

/**
 * 题型类型定义（涵盖所有可能的题型值）
 */
export type QuestionType =
  | 'single_choice'    // 单选题
  | 'multiple_choice'  // 多选题
  | 'fill_blank'       // 填空题（数据库格式）
  | 'fill_in'          // 填空题（前端格式）
  | 'calculation'      // 计算题
  | 'application'      // 应用题
  | 'subjective'       // 主观题/解答题
  | 'unknown';         // 未知题型

/**
 * 题型中文映射
 */
export const TYPE_LABELS: Record<QuestionType, string> = {
  'single_choice': '单选',
  'multiple_choice': '多选',
  'fill_blank': '填空',
  'fill_in': '填空',
  'calculation': '计算',
  'application': '应用',
  'subjective': '解答',
  'unknown': '未知'
};

/**
 * 题型颜色映射（用于 UI 样式）
 */
export const TYPE_COLORS: Record<QuestionType, string> = {
  'single_choice': 'text-blue-600',
  'multiple_choice': 'text-orange-600',
  'fill_blank': 'text-emerald-600',
  'fill_in': 'text-emerald-600',
  'calculation': 'text-purple-600',
  'application': 'text-pink-600',
  'subjective': 'text-slate-600',
  'unknown': 'text-slate-400'
};

/**
 * 题型背景色映射（用于标签样式）
 */
export const TYPE_BG_COLORS: Record<QuestionType, string> = {
  'single_choice': 'bg-blue-50',
  'multiple_choice': 'bg-orange-50',
  'fill_blank': 'bg-emerald-50',
  'fill_in': 'bg-emerald-50',
  'calculation': 'bg-purple-50',
  'application': 'bg-pink-50',
  'subjective': 'bg-slate-50',
  'unknown': 'bg-slate-100'
};

/**
 * 获取题型中文标签
 * @param type 题型值
 * @returns 中文标签
 */
export function getTypeLabel(type: string | undefined | null): string {
  if (!type) return TYPE_LABELS.unknown;
  return TYPE_LABELS[type as QuestionType] || type;
}

/**
 * 获取题型颜色类名
 * @param type 题型值
 * @returns Tailwind 颜色类名
 */
export function getTypeColor(type: string | undefined | null): string {
  if (!type) return TYPE_COLORS.unknown;
  return TYPE_COLORS[type as QuestionType] || TYPE_COLORS.unknown;
}

/**
 * 获取题型背景色类名
 * @param type 题型值
 * @returns Tailwind 背景色类名
 */
export function getTypeBgColor(type: string | undefined | null): string {
  if (!type) return TYPE_BG_COLORS.unknown;
  return TYPE_BG_COLORS[type as QuestionType] || TYPE_BG_COLORS.unknown;
}

/**
 * 标准化题型值（统一为数据库格式）
 * @param type 原始题型值
 * @returns 标准化后的题型值
 */
export function normalizeType(type: string): QuestionType {
  const typeMap: Record<string, QuestionType> = {
    'fill_in': 'fill_blank',
  };
  return typeMap[type] || (type as QuestionType);
}