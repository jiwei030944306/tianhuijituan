/**
 * 字段展示配置类型定义
 *
 * @description 定义题目预览中各字段的展示配置，支持数据驱动的渲染方式
 */

import type { Component } from 'vue';

// ==================== 字段类型枚举 ====================

/**
 * 字段显示类型
 */
export type FieldType =
  | 'text'           // 纯文本
  | 'badge'          // 标签样式
  | 'badge-list'     // 标签列表
  | 'date'           // 日期时间
  | 'rich-text'      // 富文本（支持 LaTeX）
  | 'code'           // 代码块
  | 'image'          // 图片
  | 'grid'           // 网格布局
  | 'section'        // 分组容器
  | 'status'         // 状态标识
  | 'stem'           // 题干（特殊样式，大字体+衬线体）
  | 'options'        // 选项列表（选择题选项）
  | 'answer-box'     // 答案盒子（绿色背景）
  | 'analysis-box';  // 解析盒子（黄色背景）

// ==================== 字段值类型 ====================

/**
 * 字段值类型（支持多种数据格式）
 */
export type FieldValue =
  | string
  | number
  | boolean
  | string[]
  | null
  | undefined
  | Record<string, any>;

// ==================== 字段配置接口 ====================

/**
 * 单个字段配置
 */
export interface FieldConfig {
  /** 字段键名（对应 Question 对象的属性） */
  key: string;

  /** 显示标签 */
  label: string;

  /** 字段类型 */
  type: FieldType;

  /** 所属分组 */
  group: FieldGroup;

  /** 显示顺序（同组内） */
  order?: number;

  /** 图标组件 */
  icon?: Component;

  /** 是否必填（影响空值显示） */
  required?: boolean;

  /** 空值显示文本 */
  emptyText?: string;

  /** 格式化函数 */
  formatter?: (value: FieldValue) => string;

  /** 自定义渲染函数 */
  render?: (value: FieldValue, question: Record<string, any>) => any;

  /** 条件显示函数（返回 false 则不渲染） */
  condition?: (question: Record<string, any>) => boolean;

  /** 样式配置 */
  style?: FieldStyleConfig;

  /** 子字段配置（用于 grid、section 等复杂类型） */
  children?: FieldConfig[];
}

/**
 * 字段样式配置
 */
export interface FieldStyleConfig {
  /** 背景颜色 */
  bgColor?: string;

  /** 边框颜色 */
  borderColor?: string;

  /** 文字颜色 */
  textColor?: string;

  /** 标签颜色 */
  labelColor?: string;

  /** 额外的 CSS 类名 */
  className?: string;

  /** 是否紧凑模式 */
  compact?: boolean;
}

/**
 * 字段分组配置
 */
export interface FieldGroupConfig {
  /** 分组标识 */
  id: FieldGroup;

  /** 分组标题 */
  title: string;

  /** 分组图标 */
  icon?: Component;

  /** 分组样式 */
  style?: FieldStyleConfig;

  /** 分组显示顺序 */
  order: number;

  /** 是否默认展开 */
  defaultExpanded?: boolean;
}

/**
 * 字段分组枚举
 */
export type FieldGroup =
  | 'system'         // 系统信息
  | 'classification' // 分类信息
  | 'source'         // 来源信息
  | 'manual'         // 人工确认字段
  | 'ai'             // AI 生成字段
  | 'content'        // 题目内容（题干、选项等）
  | 'answer'         // 答案与解析
  | 'time'           // 时间信息
  | 'error';         // 错误信息

// ==================== 字段分组配置 ====================

/**
 * 预定义的分组配置
 */
export const FIELD_GROUPS: Record<FieldGroup, FieldGroupConfig> = {
  system: {
    id: 'system',
    title: '系统信息',
    order: 1,
    style: {
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      labelColor: 'text-slate-400',
    },
  },
  classification: {
    id: 'classification',
    title: '分类信息',
    order: 2,
    style: {
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      labelColor: 'text-blue-400',
    },
  },
  source: {
    id: 'source',
    title: '来源信息',
    order: 3,
    style: {
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      labelColor: 'text-slate-400',
    },
  },
  manual: {
    id: 'manual',
    title: '人工确认字段',
    order: 4,
    style: {
      bgColor: 'bg-green-50/30',
      borderColor: 'border-green-100',
      labelColor: 'text-green-700',
    },
  },
  ai: {
    id: 'ai',
    title: 'AI 生成字段',
    order: 5,
    style: {
      bgColor: 'bg-purple-50/30',
      borderColor: 'border-purple-100',
      labelColor: 'text-purple-700',
    },
  },
  content: {
    id: 'content',
    title: '题目内容',
    order: 6,
    style: {
      bgColor: 'bg-white',
      borderColor: 'border-slate-200',
      labelColor: 'text-slate-400',
    },
  },
  answer: {
    id: 'answer',
    title: '答案与解析',
    order: 7,
    style: {
      bgColor: 'bg-green-50/30',
      borderColor: 'border-green-100',
      labelColor: 'text-green-600',
    },
  },
  time: {
    id: 'time',
    title: '时间信息',
    order: 8,
    style: {
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      labelColor: 'text-slate-400',
    },
  },
  error: {
    id: 'error',
    title: '错误信息',
    order: 0, // 错误信息优先显示
    style: {
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      labelColor: 'text-red-700',
    },
  },
};

// ==================== 工具函数 ====================

/**
 * 根据分组获取排序后的字段列表
 * @param fields - 字段配置数组
 * @param group - 分组标识
 * @returns 排序后的字段列表
 */
export function getFieldsByGroup(fields: FieldConfig[], group: FieldGroup): FieldConfig[] {
  return fields
    .filter(f => f.group === group)
    .sort((a, b) => (a.order || 0) - (b.order || 0));
}

/**
 * 获取所有分组并按顺序排序
 * @param fields - 字段配置数组
 * @returns 排序后的分组列表
 */
export function getSortedGroups(fields: FieldConfig[]): FieldGroup[] {
  const usedGroups = new Set(fields.map(f => f.group));
  return Object.values(FIELD_GROUPS)
    .filter(g => usedGroups.has(g.id))
    .sort((a, b) => a.order - b.order);
}

/**
 * 检查分组是否有可见字段
 * @param fields - 字段配置数组
 * @param group - 分组标识
 * @param question - 题目数据
 * @returns 是否有可见字段
 */
export function hasVisibleFields(fields: FieldConfig[], group: FieldGroup, question: Record<string, any>): boolean {
  return getFieldsByGroup(fields, group).some(field => {
    // 检查条件
    if (field.condition && !field.condition(question)) {
      return false;
    }
    // 检查值是否存在
    const value = question[field.key];
    return value !== undefined && value !== null && value !== '';
  });
}