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
export type Subject = '数学' | '语文' | '英语' | '物理' | '化学' | '生物' | '历史' | '地理' | '道德与法治' | '政治';

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

  // --- 系统字段 ---
  version?: number;                     // 版本号（用于乐观锁）
}

// ==================== 题型配置（按学段+学科分） ====================

export const QUESTION_TYPES: Record<EducationLevel, Record<string, string[]>> = {
  '初中': {
    '数学': ['选择题', '多选题', '填空题', '解答题', '判断题'],
    '语文': ['选择题', '填空题', '多选题', '汉字书写', '解答题', '翻译', '基础知识', '默写', '语言运用', '综合读写', '名著阅读', '现代文阅读', '古诗词赏析', '文言文阅读', '作文', '综合性学习'],
    '英语': ['听力题', '选择题', '填空题', '完形填空', '阅读理解', '信息匹配', '选词填空', '短文填空', '语法填空', '其他阅读题型', '对话填空', '单词拼写', '词性转换', '句型转换', '句子改错', '完成句子', '翻译题', '短文改错', '书面表达', '词汇应用', '解答题'],
    '物理': ['选择题', '多选题', '填空题', '选择说明题', '判断题', '作图题', '简答题', '实验探究题', '解答题', '计算题', '综合能力题', '科普阅读题'],
    '化学': ['选择题', '多选题', '选择填充题', '判断题', '填空题', '实验题', '推断题', '工艺流程题', '科普阅读题', '科学探究题', '综合应用题', '解答题', '计算题'],
    '生物': ['选择题', '多选题', '判断题', '填空题', '实验探究题', '解答题', '材料分析题'],
    '历史': ['选择题', '填空题', '多选题', '辨析题', '材料题', '解答题', '判断题', '论述题'],
    '地理': ['选择题', '多选题', '判断题', '填空题', '连线题', '解答题'],
    '道德与法治': ['选择题', '填空题', '多选题', '判断题', '简答题', '辨析题', '评析题', '阐述见解题', '材料分析题', '判断说理题', '情境探究题', '分析说明题', '综合探究题'],
  },
  '高中': {
    '语文': ['选择题', '多选题', '填空题', '解答题', '判断题'],
    '数学': ['选择题', '多选题', '填空题', '解答题', '判断题'],
    '英语': ['听力题', '选择题', '填空题', '完形填空', '阅读理解', '信息匹配', '选词填空', '短文填空', '语法填空', '其他阅读题型', '对话填空', '单词拼写', '词性转换', '句型转换', '句子改错', '完成句子', '翻译题', '短文改错', '书面表达', '词汇应用', '解答题'],
    '物理': ['选择题', '多选题', '填空题', '判断题', '作图题', '实验题', '解答题'],
    '化学': ['选择题', '填空题', '多选题', '判断题', '实验题', '计算题', '推断题', '解答题', '工艺流程题'],
    '生物': ['选择题', '填空题', '多选题', '材料题', '判断题', '解答题', '论述题'],
    '历史': ['选择题', '填空题', '多选题', '材料题', '判断题', '解答题', '论述题'],
    '地理': ['选择题', '填空题', '多选题', '判断题', '解答题'],
    '政治': ['选择题', '填空题', '多选题', '辨析评析题', '判断题', '材料题', '解答题', '论述题', '图表题', '探究类试题', '简答题'],
  },
};

// 题类选项列表
export const CATEGORY_OPTIONS: QuestionCategory[] = ['常考题', '易错题', '好题', '压轴题', '优选题'];

// ==================== 题型英文映射（AI返回标准）====================

// 中文题型 -> 英文标识符（AI 返回此值）
export const QUESTION_TYPE_TO_ENGLISH: Record<string, string> = {
  // 通用题型
  '选择题': 'single_choice',
  '多选题': 'multiple_choice',
  '填空题': 'basic_fill',  // 统一使用名词 + _fill 风格，与其他填空类题型保持一致
  '解答题': 'subjective',
  '判断题': 'true_false',
  '解答题': 'subjective',
  '判断题': 'true_false',

  // 语文特有
  '汉字书写': 'character_writing',
  '翻译': 'translation',
  '基础知识': 'basic_knowledge',
  '默写': 'dictation',
  '语言运用': 'language_usage',
  '综合读写': 'reading_writing',
  '名著阅读': 'classic_reading',
  '现代文阅读': 'modern_reading',
  '古诗词赏析': 'poetry_appreciation',
  '文言文阅读': 'classical_chinese',
  '作文': 'composition',
  '综合性学习': 'integrated_learning',

  // 数学特有
  '计算题': 'calculation',

  // 英语特有
  '听力题': 'listening',
  '完形填空': 'cloze',
  '阅读理解': 'reading_comprehension',
  '信息匹配': 'information_matching',
  '选词填空': 'word_selection',
  '短文填空': 'passage_fill',
  '语法填空': 'grammar_fill',
  '其他阅读题型': 'other_reading',
  '对话填空': 'dialogue_fill',
  '单词拼写': 'spelling',
  '词性转换': 'word_formation',
  '句型转换': 'sentence_transformation',
  '句子改错': 'error_correction',
  '完成句子': 'sentence_completion',
  '短文改错': 'passage_correction',
  '书面表达': 'writing',
  '词汇应用': 'vocabulary_usage',

  // 物理特有
  '选择说明题': 'choice_explanation',
  '作图题': 'drawing',
  '简答题': 'short_answer',
  '实验探究题': 'experiment_inquiry',
  '综合能力题': 'comprehensive',
  '科普阅读题': 'science_reading',

  // 化学特有
  '选择填充题': 'choice_fill',
  '实验题': 'experiment',
  '推断题': 'deduction',
  '工艺流程题': 'process_flow',
  '科学探究题': 'science_inquiry',
  '综合应用题': 'comprehensive_application',

  // 生物特有
  '材料分析题': 'material_analysis',

  // 历史特有
  '辨析题': 'analysis',
  '材料题': 'material',
  '论述题': 'essay',

  // 地理特有
  '连线题': 'matching',

  // 政治/道德与法治特有
  '评析题': 'evaluation',
  '阐述见解题': 'opinion',
  '判断说理题': 'reasoning',
  '情境探究题': 'scenario_inquiry',
  '分析说明题': 'explanation',
  '综合探究题': 'comprehensive_inquiry',
  '辨析评析题': 'analysis_evaluation',
  '图表题': 'chart',
  '探究类试题': 'inquiry',
};

// 英文标识符 -> 中文显示（前端显示用）
export const QUESTION_TYPE_TO_CHINESE: Record<string, string> = Object.fromEntries(
  Object.entries(QUESTION_TYPE_TO_ENGLISH).map(([cn, en]) => [en, cn])
);

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
  '初中': ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '道德与法治'],
  '高中': ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治'],
};

// 根据学段获取年级列表
export function getGradesByLevel(level: EducationLevel): number[] {
  return level === '初中' ? [7, 8, 9] : [10, 11, 12];
}

// 根据学段+学科获取可用题型列表
export function getTypesBySubject(subject: string, level: EducationLevel = '初中'): string[] {
  return QUESTION_TYPES[level]?.[subject] || [];
}

// 根据学段获取该学段的学科列表
export function getSubjectsByLevel(level: EducationLevel): string[] {
  return Object.keys(QUESTION_TYPES[level] || {});
}

// ==================== 题型映射工具函数 ====================

/**
 * 中文题型转英文
 * @param chineseType 中文题型名称
 * @returns 英文标识符
 */
export function getEnglishTypeName(chineseType: string): string | undefined {
  return QUESTION_TYPE_TO_ENGLISH[chineseType];
}

/**
 * 英文题型转中文
 * @param englishType 英文标识符
 * @returns 中文题型名称
 */
export function getChineseTypeName(englishType: string): string | undefined {
  return QUESTION_TYPE_TO_CHINESE[englishType];
}

/**
 * 根据学科和学段获取英文题型列表
 * @param subject 学科名称（中文）
 * @param level 学段
 * @returns 英文题型标识符列表
 */
export function getTypesBySubjectEnglish(subject: string, level: EducationLevel = '初中'): string[] {
  const chineseTypes = QUESTION_TYPES[level]?.[subject] || [];
  return chineseTypes.map(cn => QUESTION_TYPE_TO_ENGLISH[cn] || cn);
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
