/**
 * 题目字段配置定义
 *
 * @description 基于数据驱动的字段配置，定义所有 Question 字段的展示规则
 */

import { Hash, Star, Clock, Calendar, CheckCircle, Info } from 'lucide-vue-next';
import type { Component } from 'vue';
import type { FieldConfig } from './FieldConfig';
import { gradeLabels } from '@/types/question';
import type { Difficulty } from '@/types/question';

// ==================== 工具函数 ====================

/**
 * 获取难度标签文本
 */
function getDifficultyLabel(difficulty: Difficulty | string | undefined): string {
  return difficulty || '未知';
}

/**
 * 获取年级标签文本
 */
function getGradeLabel(grade: number | undefined): string {
  return grade !== undefined ? gradeLabels[grade] || `${grade}年级` : '未知';
}

/**
 * 格式化日期时间
 */
function formatDateTime(dateStr: string | undefined): string {
  if (!dateStr) return '未知';
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  } catch {
    return dateStr;
  }
}

// ==================== 字段配置数组 ====================

/**
 * 题目字段配置列表
 * 添加新字段时，只需在此数组中添加配置即可
 */
export const QUESTION_FIELDS: FieldConfig[] = [
  // ==================== 错误信息 ====================
  {
    key: 'status',
    label: '错误信息',
    type: 'section',
    group: 'error',
    order: 0,
    icon: undefined,
    condition: (q) => q.status === 'error',
    children: [
      {
        key: 'statusMessage',
        label: '错误消息',
        type: 'text',
        group: 'error',
        order: 1,
        emptyText: '题目数据存在问题，无法进入标化流程',
      },
      {
        key: 'comment',
        label: '备注',
        type: 'text',
        group: 'error',
        order: 2,
        emptyText: '无',
      },
    ],
  },

  // ==================== 系统信息 ====================
  {
    key: 'id',
    label: 'ID',
    type: 'badge',
    group: 'system',
    order: 1,
    style: {
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      textColor: 'text-slate-600',
    },
  },
  {
    key: 'status',
    label: '状态',
    type: 'badge',
    group: 'system',
    order: 2,
    style: {
      bgColor: 'bg-white',
      borderColor: 'border-slate-200',
      textColor: 'text-slate-600',
    },
  },
  {
    key: 'questionNumber',
    label: '题号',
    type: 'badge',
    group: 'system',
    order: 3,
    style: {
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      textColor: 'text-slate-600',
    },
  },
  {
    key: 'type',
    label: '题型',
    type: 'badge',
    group: 'system',
    order: 4,
    style: {
      bgColor: 'bg-white',
      borderColor: 'border-slate-200',
      textColor: 'text-slate-600',
    },
  },
  {
    key: 'version',
    label: '修改版本号',
    type: 'badge',
    group: 'system',
    order: 5,
    formatter: (val) => `v${val}`,
    style: {
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      textColor: 'text-slate-600',
    },
  },

  // ==================== 分类信息 ====================
  {
    key: 'subject',
    label: '科目',
    type: 'badge',
    group: 'classification',
    order: 1,
    icon: Info,
    style: {
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-700 font-medium',
    },
  },
  {
    key: 'educationLevel',
    label: '学段',
    type: 'badge',
    group: 'classification',
    order: 2,
    icon: Info,
    style: {
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-700 font-medium',
    },
  },
  {
    key: 'grade',
    label: '年级',
    type: 'badge',
    group: 'classification',
    order: 3,
    icon: Info,
    formatter: getGradeLabel,
    style: {
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-700 font-medium',
    },
  },

  // ==================== 来源信息 ====================
  {
    key: 'source',
    label: '上传文件来源',
    type: 'badge',
    group: 'source',
    order: 1,
    style: {
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      textColor: 'text-slate-600',
    },
  },
  {
    key: 'sourceFolder',
    label: '服务器文件夹来源',
    type: 'badge',
    group: 'source',
    order: 2,
    style: {
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      textColor: 'text-slate-600',
      className: 'font-mono',
    },
  },

  // ==================== 人工确认字段 ====================
  {
    key: 'manual-section',
    label: '人工确认字段',
    type: 'section',
    group: 'manual',
    order: 1,
    icon: CheckCircle,
    children: [
      {
        key: 'status',
        label: '确认状态',
        type: 'status',
        group: 'manual',
        order: 1,
        render: (val) => ({
          text: val === 'confirmed' ? '已确认' : '待确认',
          color: val === 'confirmed' ? 'bg-green-100 text-green-700' : 'bg-slate-200 text-slate-600',
        }),
      },
      {
        key: 'difficulty',
        label: '难度',
        type: 'badge',
        group: 'manual',
        order: 2,
        formatter: getDifficultyLabel,
        style: {
          bgColor: 'bg-white',
          borderColor: 'border-slate-200',
          textColor: 'text-slate-600',
        },
      },
      {
        key: 'topics',
        label: '知识点',
        type: 'badge-list',
        group: 'manual',
        order: 3,
        icon: Hash,
        style: {
          bgColor: 'bg-indigo-50',
          borderColor: 'border-indigo-200',
          textColor: 'text-indigo-700 font-medium',
        },
      },
      {
        key: 'category',
        label: '题类',
        type: 'badge',
        group: 'manual',
        order: 4,
        icon: Star,
        style: {
          bgColor: 'bg-amber-50',
          borderColor: 'border-amber-200',
          textColor: 'text-amber-700 font-medium',
        },
      },
      {
        key: 'grade',
        label: '年级',
        type: 'badge',
        group: 'manual',
        order: 5,
        formatter: getGradeLabel,
        style: {
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          textColor: 'text-blue-700 font-medium',
        },
      },
      {
        key: 'confirmedAt',
        label: '确认时间',
        type: 'date',
        group: 'manual',
        order: 6,
        icon: Clock,
        formatter: formatDateTime,
      },
      {
        key: 'comment',
        label: '人工备注',
        type: 'rich-text',
        group: 'manual',
        order: 7,
      },
    ],
  },

  // ==================== AI 生成字段 ====================
  {
    key: 'ai-section',
    label: 'AI 生成字段',
    type: 'section',
    group: 'ai',
    order: 1,
    children: [
      {
        key: 'isAiOptimized',
        label: '是否经过AI优化',
        type: 'badge',
        group: 'ai',
        order: 1,
        formatter: (val) => val ? '是' : '否',
        style: {
          bgColor: (val) => val ? 'bg-green-100' : 'bg-slate-100',
          textColor: (val) => val ? 'text-green-700' : 'text-slate-500',
        }
      },
      {
        key: 'aiModel',
        label: 'AI 模型',
        type: 'badge',
        group: 'ai',
        order: 2,
        emptyText: '未选择模型',
        style: {
          bgColor: 'bg-slate-50',
          borderColor: 'border-slate-200',
          textColor: 'text-slate-600',
          className: 'text-[10px]',
        },
      },
      {
        key: 'aiOptimizedAt',
        label: 'AI 处理时间',
        type: 'date',
        group: 'ai',
        order: 3,
        emptyText: '未处理',
        formatter: formatDateTime,
      },
      {
        key: 'ai-grid',
        label: 'AI 建议值',
        type: 'grid',
        group: 'ai',
        order: 4,
        children: [
          {
            key: 'aiGrade',
            label: 'AI 建议年级',
            type: 'badge',
            group: 'ai',
            formatter: getGradeLabel,
            emptyText: '未生成',
            style: {
              bgColor: 'bg-purple-50',
              borderColor: 'border-purple-200',
              textColor: 'text-purple-700 font-medium',
            },
          },
          {
            key: 'aiDifficulty',
            label: 'AI 建议难度',
            type: 'badge',
            group: 'ai',
            formatter: getDifficultyLabel,
            emptyText: '未生成',
            style: {
              bgColor: 'bg-purple-50',
              borderColor: 'border-purple-200',
              textColor: 'text-purple-700 font-medium',
            },
          },
        ],
      },
      {
        key: 'aiTopics',
        label: 'AI 建议知识点',
        type: 'badge-list',
        group: 'ai',
        order: 5,
        emptyText: '未生成知识点',
        style: {
          bgColor: 'bg-purple-50',
          borderColor: 'border-purple-200',
          textColor: 'text-purple-700 font-medium',
        },
      },
      {
        key: 'aiCategory',
        label: 'AI 建议题类',
        type: 'badge',
        group: 'ai',
        order: 6,
        emptyText: '未生成题类',
        style: {
          bgColor: 'bg-purple-50',
          borderColor: 'border-purple-200',
          textColor: 'text-purple-700 font-medium',
        },
      },
      {
        key: 'aiAnalysis',
        label: 'AI 生成解析',
        type: 'rich-text',
        group: 'ai',
        order: 7,
        emptyText: '暂无 AI 解析',
      },
      {
        key: 'aiReasoning',
        label: 'AI 推理链',
        type: 'code',
        group: 'ai',
        order: 8,
        emptyText: '暂无推理过程',
      },
    ],
  },

  // ==================== 题目内容 ====================
  {
    key: 'stemImages',
    label: '题干图片',
    type: 'image',
    group: 'content',
    order: 1,
  },
  {
    key: 'stem',
    label: '题干',
    type: 'stem',
    group: 'content',
    order: 2,
  },
  {
    key: 'options',
    label: '选项',
    type: 'options',
    group: 'content',
    order: 3,
  },

  // ==================== 答案与解析 ====================
  {
    key: 'answer',
    label: '正确答案',
    type: 'answer-box',
    group: 'answer',
    order: 1,
  },
  {
    key: 'analysis',
    label: '原始解析',
    type: 'analysis-box',
    group: 'answer',
    order: 2,
  },

  // ==================== 时间信息 ====================
  {
    key: 'time-section',
    label: '时间信息',
    type: 'section',
    group: 'time',
    order: 1,
    icon: Calendar,
    children: [
      {
        key: 'createdAt',
        label: '创建时间',
        type: 'date',
        group: 'time',
        order: 2,
        formatter: formatDateTime,
      },
      {
        key: 'updatedAt',
        label: '更新时间',
        type: 'date',
        group: 'time',
        order: 3,
        formatter: formatDateTime,
      },
    ],
  },
];