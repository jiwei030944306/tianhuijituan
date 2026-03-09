/**
 * 题目类型定义
 * 定义题目相关的数据结构和枚举类型
 *
 * 字段生命周期：
 * P1 上传 → 基础内容 + 分类信息 + status(active)
 * P2-1 脚本质检 → status(error/waste) + statusMessage
 * P2-2 脚本预处理 → 非语义校验/修复/初始化
 * P2-3 AI 生成 → ai* 字段组
 * P2-4 人工确认 → grade/difficulty/topics/category/comment/confirmedAt, status(confirmed)
 */

// ==================== 枚举类型 ====================

// ==================== 难度映射（后端英文值 -> 前端中文显示）====================

// 难度英文值（5级，与后端数据库一致）
export type Difficulty = 'easy' | 'medium_easy' | 'medium' | 'medium_hard' | 'hard';

// 难度英文 -> 中文映射（5级）
export const DIFFICULTY_TO_CHINESE: Record<Difficulty, string> = {
  'easy': '易',
  'medium_easy': '较易',
  'medium': '中档',
  'medium_hard': '较难',
  'hard': '难',
};

// 难度中文 -> 英文映射（5级）
export const CHINESE_TO_DIFFICULTY: Record<string, Difficulty> = {
  '易': 'easy',
  '较易': 'medium_easy',
  '中档': 'medium',
  '较难': 'medium_hard',
  '难': 'hard',
};

// 难度选项列表（5级独立值）
export const DIFFICULTY_OPTIONS: { value: Difficulty; label: string }[] = [
  { value: 'easy', label: '易' },
  { value: 'medium_easy', label: '较易' },
  { value: 'medium', label: '中档' },
  { value: 'medium_hard', label: '较难' },
  { value: 'hard', label: '难' },
];

// 获取难度中文标签
export function getDifficultyLabel(english: string | undefined): string {
  if (!english) return '未知';
  return DIFFICULTY_TO_CHINESE[english as Difficulty] || english;
}

// 题目状态枚举
export type QuestionStatus =
  | 'active'      // 质检通过，正常
  | 'error'       // 有问题可修（如图片路径错误）
  | 'waste'       // 废题（题干/选项缺失，不可修复）
  | 'confirmed';  // 人工确认，已入库

// 学段枚举
export type EducationLevel = '初中' | '高中';

// 科目枚举（涵盖初中+高中所有学科）
export type Subject = '数学' | '语文' | '英语' | '物理' | '化学' | '生物' | '历史' | '地理' | '政治';

// 题类枚举
export type QuestionCategory = '常考题' | '易错题' | '好题' | '压轴题' | '优选题';

// ==================== 基础接口 ====================

// 选项接口
export interface Option {
  label?: string;         // 选项标识：A, B, C, D
  key?: string;           // 选项标识（兼容 key 字段）
  content: string;        // 选项内容
  isCorrect?: boolean;    // 是否正确答案
  image?: string;         // 选项图片路径
}

// 图片接口
export interface StemImage {
  src: string;            // 图片路径
  layout: 'inline' | 'block';  // 布局方式
}

// ==================== 题目主接口 ====================

export interface Question {
  // --- P1 上传时写入 ---
  id: string;                           // 题目唯一标识（后端自动生成）
  questionNumber: number;               // 题号
  stem: string;                         // 题干
  options?: Option[];                   // 选项（选择题必填）
  answer: string;                       // 答案
  analysis?: string;                    // 原始解析（可能为空）
  stemImages?: StemImage[];             // 题干关联图片
  type: string;                         // 题型（按学科分，见 QUESTION_TYPES 配置）
  subject?: Subject;                    // 学科（从 folderCode 映射注入）
  educationLevel?: EducationLevel;      // 学段（从 folderCode 映射注入）
  source?: string;                      // 来源（试卷名称）
  sourceFolder?: string;                // 来源文件夹
  createdAt?: string;                   // 创建时间
  updatedAt?: string;                   // 更新时间

  // --- P2-1 脚本质检 ---
  status: QuestionStatus;               // 质检状态
  statusMessage?: string;               // 错误或废题原因（如"题干为空""选项缺失"）

  // --- P2-2 脚本预处理（非语义） ---

  // --- P2-3 AI 生成 ---
  aiGrade?: string;                     // AI 建议年级
  aiDifficulty?: Difficulty;            // AI 建议难度
  aiTopics?: string[];                  // AI 建议知识点（1-3个）
  aiCategory?: QuestionCategory;        // AI 建议题类（常考题/易错题/好题/压轴题/优选题）
  aiAnalysis?: string;                  // AI 生成解析（支持 LaTeX）
  aiReasoning?: string;                 // AI 思考链（推理过程）
  aiModel?: string;                     // 使用的模型名称
  aiOptimizedAt?: string;               // AI 处理时间戳
  isAiOptimized?: boolean;              // 是否经过 AI 处理

  // --- P2-4 人工确认 ---
  grade?: number;                       // 最终年级（人工确认值，7-12）
  difficulty?: Difficulty;              // 最终难度（人工确认值，5级）
  topics?: string[];                    // 最终知识点（人工确认值，1-3个）
  category?: QuestionCategory;          // 最终题类（人工确认值，5类）
  comment?: string;                     // 人工备注（纯备注，不混入错误信息）
  confirmedAt?: string;                 // 确认入库时间戳

  // --- P2-5 相似题检测 ---
  isDuplicate?: boolean;                // 是否为相似题
  duplicateGroupId?: string;            // 相似题组ID
  duplicateCheckedAt?: string;          // 相似度检测时间

  // --- 系统字段 ---
  version?: number;                     // 版本号（用于乐观锁）
}

// ==================== 题型配置（按学段+学科分） ====================

// 题型值定义（数字）
export const QUESTION_TYPE_VALUES = {
  SINGLE_CHOICE: 1,      // 选择题
  FILL_BLANK: 2,         // 填空题
  MULTIPLE_CHOICE: 3,    // 多选题
  TRUE_FALSE: 4,         // 判断题
  SHORT_ANSWER: 9,       // 解答题
} as const;

// 题型值 -> 中文映射
export const QUESTION_TYPE_LABELS: Record<number, string> = {
  1: '选择题',
  2: '填空题',
  3: '多选题',
  4: '判断题',
  9: '解答题',
};

// 题型选项列表（用于下拉选择）
export const QUESTION_TYPE_OPTIONS = [
  { value: 1, label: '选择题' },
  { value: 2, label: '填空题' },
  { value: 3, label: '多选题' },
  { value: 4, label: '判断题' },
  { value: 9, label: '解答题' },
];

// 题型配置（按学段+学科分，值为数字）
export const QUESTION_TYPES: Record<EducationLevel, Record<string, number[]>> = {
  '初中': {
    '数学': [1, 3, 2, 9, 4],           // 选择题、多选题、填空题、解答题、判断题
    '语文': [1, 2, 3, 4, 9],           // 待完善
    '英语': [1, 2, 3, 4, 9],           // 待完善
    '物理': [1, 3, 2, 4, 9],           // 待完善
    '化学': [1, 3, 2, 4, 9],           // 待完善
    '生物': [1, 3, 2, 4, 9],           // 待完善
    '历史': [1, 2, 3, 4, 9],           // 待完善
    '地理': [1, 3, 4, 2, 9],           // 待完善
    '政治': [1, 2, 3, 4, 9],           // 待完善
  },
  '高中': {
    '数学': [1, 3, 2, 9, 4],           // 选择题、多选题、填空题、解答题、判断题
    '语文': [1, 3, 2, 9, 4],           // 待完善
    '英语': [1, 2, 3, 4, 9],           // 待完善
    '物理': [1, 3, 2, 4, 9],           // 待完善
    '化学': [1, 2, 3, 4, 9],           // 待完善
    '生物': [1, 2, 3, 4, 9],           // 待完善
    '历史': [1, 2, 3, 4, 9],           // 待完善
    '地理': [1, 2, 3, 4, 9],           // 待完善
    '政治': [1, 2, 3, 4, 9],           // 待完善
  },
};

// 题类选项列表
export const CATEGORY_OPTIONS: QuestionCategory[] = ['常考题', '易错题', '好题', '压轴题', '优选题'];

// ==================== 题型工具函数 ====================

/**
 * 获取题型中文名称
 * @param typeValue 题型数字值
 * @returns 中文名称
 */
export function getTypeLabel(typeValue: number | string | undefined): string {
  if (typeValue === undefined || typeValue === null) return '未知';
  return QUESTION_TYPE_LABELS[Number(typeValue)] || '未知';
}

/**
 * 根据学科和学段获取题型选项列表
 * @param subject 学科名称
 * @param level 学段
 * @returns 题型选项列表
 */
export function getTypeOptions(subject: string, level: EducationLevel = '初中'): { value: number; label: string }[] {
  const typeValues = QUESTION_TYPES[level]?.[subject] || [];
  return typeValues.map(value => ({
    value,
    label: QUESTION_TYPE_LABELS[value] || '未知'
  }));
}

// ==================== 辅助类型 ====================

// 题目筛选条件
export interface QuestionFilters {
  subject?: Subject;                    // 科目筛选
  grade?: number;                       // 年级筛选
  educationLevel?: EducationLevel;      // 学段筛选
  type?: string;                        // 类型筛选
  difficulty?: Difficulty;              // 难度筛选
  category?: QuestionCategory;          // 题类筛选
  status?: QuestionStatus;              // 状态筛选
  keyword?: string;                     // 关键词搜索
  hasAnalysis?: boolean;                // 是否有解析
  hasImages?: boolean;                  // 是否有图片
  hasTopics?: boolean;                  // 是否有知识点
  isAiOptimized?: boolean;              // 是否经过AI优化
  isDuplicate?: boolean;                // 是否为相似题筛选
  skip?: number;                        // 分页偏移
  limit?: number;                       // 分页数量
}

// 数据统计
export interface StatisticsData {
  total: number;                        // 总题数
  withAnalysis: number;                 // 有解析的题目数
  withImages: number;                   // 有图片的题目数
  withTopics: number;                   // 有知识点的题目数
  byType: Record<string, number>;       // 按题型统计
  byStatus: Record<string, number>;     // 按状态统计
  byDifficulty: Record<string, number>; // 按难度统计
  aiOptimized: number;                  // AI 已处理数
}

// 显示配置
export interface DisplayConfig {
  showAnswer: boolean;                  // 是否显示答案
  showAnalysis: boolean;                // 是否显示解析
  compactMode: boolean;                 // 是否紧凑模式
}

// 上传响应接口
export interface UploadResponse {
  success: boolean;
  folderName: string;
  subject: string;
  grade: number;
  educationLevel: string;
  questionCount: number;
  importedCount: number;
  failedCount: number;
  imageCount: number;
  storagePath: string;
  failedQuestions?: Array<{
    questionNumber: number;
    error: string;
  }>;
}

// API 响应包装器
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// ==================== 常量与工具函数 ====================

// 年级标签映射
export const gradeLabels: Record<number, string> = {
  7: '初一',
  8: '初二',
  9: '初三',
  10: '高一',
  11: '高二',
  12: '高三',
};

// 科目列表（按学段区分）
export const subjects: Record<EducationLevel, string[]> = {
  '初中': ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治'],
  '高中': ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治'],
};

// 根据学段获取年级列表
export function getGradesByLevel(level: EducationLevel): number[] {
  return level === '初中' ? [7, 8, 9] : [10, 11, 12];
}

// 根据学段+学科获取可用题型列表（返回数字值）
export function getTypesBySubject(subject: string, level: EducationLevel = '初中'): number[] {
  return QUESTION_TYPES[level]?.[subject] || [];
}

// 根据学段获取该学段的学科列表
export function getSubjectsByLevel(level: EducationLevel): string[] {
  return Object.keys(QUESTION_TYPES[level] || {});
}

// ==================== 题型映射工具函数 ====================

/**
 * 获取题型标签（已弃用，请使用 getTypeLabel）
 * @deprecated 使用 getTypeLabel 代替
 */
export function getEnglishTypeName(chineseType: string): string | undefined {
  console.warn('getEnglishTypeName is deprecated, type values are now numbers');
  return undefined;
}

/**
 * 获取题型中文名称（已弃用，请使用 getTypeLabel）
 * @deprecated 使用 getTypeLabel 代替
 */
export function getChineseTypeName(englishType: string): string | undefined {
  console.warn('getChineseTypeName is deprecated, use getTypeLabel instead');
  return getTypeLabel(englishType);
}

/**
 * 根据学科和学段获取题型列表（已弃用，请使用 getTypeOptions）
 * @deprecated 使用 getTypeOptions 代替
 */
export function getTypesBySubjectEnglish(subject: string, level: EducationLevel = '初中'): number[] {
  return QUESTION_TYPES[level]?.[subject] || [];
}


// ==================== 知识点筛选相关类型 ====================

/**
 * 知识点标签项
 * 用于知识点筛选器展示
 */
export interface KnowledgeTag {
  name: string;           // 知识点名称
  count: number;          // 关联题目数量
  selected?: boolean;     // 是否选中（可选，用于UI状态）
}

/**
 * 知识点筛选条件
 * 扩展 QuestionFilters 支持知识点筛选
 */
export interface KnowledgeFilter {
  topics: string[];       // 选中的知识点列表
}

/**
 * 知识点统计
 * 用于展示知识点分布情况
 */
export interface KnowledgeStats {
  total: number;          // 知识点总数
  withTopics: number;     // 有知识点的题目数
  withoutTopics: number;  // 无知识点的题目数
  distribution: KnowledgeTag[];  // 知识点分布列表
}
