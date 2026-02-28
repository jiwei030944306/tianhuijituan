/**
 * AI服务API
 * 用于调用AI接口优化试题标签
 * 支持多模态（文本 + 图片）
 */

import axios from 'axios';
import type { Question } from '@/types/question';
import { getKnowledgeTree } from '@/config/knowledgePoints';
import type { KnowledgeNode } from '@/components/common/KnowledgePointSelector.vue';

// AI服务配置
// 安全修复：API Key 从环境变量读取，不再硬编码
const AI_CONFIG = {
  baseURL: import.meta.env.VITE_AI_BASE_URL || 'https://moyuapi.top/v1',
  apiKey: import.meta.env.VITE_AI_API_KEY || '', // 必须通过环境变量配置
  model: import.meta.env.VITE_AI_MODEL || 'gemini-3-pro-preview'
};

// 验证 API Key 是否已配置
if (!AI_CONFIG.apiKey) {
  console.warn('[AI] VITE_AI_API_KEY 未配置，AI 功能将不可用。请在 .env.local 文件中配置。');
}

// 静态资源基础路径
const STATIC_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

// 创建AI专用axios实例
const aiClient = axios.create({
  baseURL: AI_CONFIG.baseURL,
  timeout: 120000, // 多模态请求可能更慢
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${AI_CONFIG.apiKey}`
  }
});

// AI优化结果接口
export interface AIOptimizeResult {
  grade?: string;           // 建议年级
  difficulty?: string;      // 建议难度（5级中文）
  topics?: string[];        // 建议知识点
  category?: string;        // 建议题类
  analysis?: string;        // 生成的解析
  reasoning?: string;       // AI推理过程（用于调试）
  debug?: {                 // 调试信息
    prompt: ChatMessage[];
    rawResponse: unknown;
  };
}

// 图片信息接口
interface ImageInfo {
  url: string;              // 图片URL或base64
  location: 'stem' | 'option';  // 图片位置：题干或选项
  optionKey?: string;       // 如果在选项中，选项标识
}

// 多模态消息内容
type MessageContent = string | MessageContentPart[];

interface MessageContentPart {
  type: 'text' | 'image_url';
  text?: string;
  image_url?: {
    url: string;  // 支持 URL 或 data:image/xxx;base64,xxx
  };
}

// AI请求消息格式（支持多模态）
interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: MessageContent;
}

// AI响应格式
interface ChatResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: {
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }[];
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

/**
 * 从知识点树中提取所有叶子节点名称
 */
function extractLeafKnowledgePoints(nodes: KnowledgeNode[]): string[] {
  const leaves: string[] = [];

  const traverse = (nodeList: KnowledgeNode[]) => {
    for (const node of nodeList) {
      if (node.children && node.children.length > 0) {
        traverse(node.children);
      } else {
        leaves.push(node.name);
      }
    }
  };

  traverse(nodes);
  return leaves;
}

/**
 * 格式化知识点树为层级文本
 */
function formatKnowledgeTreeForPrompt(nodes: KnowledgeNode[]): string {
  const lines: string[] = [];

  const traverse = (nodeList: KnowledgeNode[], depth: number = 0) => {
    for (const node of nodeList) {
      const indent = '  '.repeat(depth);
      if (node.children && node.children.length > 0) {
        lines.push(`${indent}【${node.name}】`);
        traverse(node.children, depth + 1);
      } else {
        lines.push(`${indent}- ${node.name}`);
      }
    }
  };

  traverse(nodes);
  return lines.join('\n');
}

/**
 * 将图片URL转换为完整路径
 */
function getFullImageUrl(path: string): string {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  if (path.startsWith('data:')) return path;  // 已经是base64

  // 如果是 static 或 api 开头的路径，使用相对路径以利用 Vite 代理 (避免CORS问题)
  if (path.startsWith('static/') || path.startsWith('/static/')) {
    return path.startsWith('/') ? path : `/${path}`;
  }
  if (path.startsWith('/api/')) {
    return path;
  }

  return `${STATIC_BASE_URL}/${path}`;
}

/**
 * 获取图片的base64编码
 * @param imageUrl 图片URL
 * @returns base64字符串或null
 */
async function fetchImageAsBase64(imageUrl: string): Promise<string | null> {
  try {
    const fullUrl = getFullImageUrl(imageUrl);
    console.log(`[AI] 正在获取图片: ${fullUrl}`);

    const response = await axios.get(fullUrl, {
      responseType: 'arraybuffer',
      timeout: 10000
    });

    const contentType = response.headers['content-type'] || 'image/png';

    // 使用更高效的方式转换 Buffer 为 Base64 (避免大图片导致栈溢出)
    const buffer = new Uint8Array(response.data);
    let binary = '';
    const len = buffer.byteLength;

    // 分块处理以防内存问题
    const CHUNK_SIZE = 8192;
    for (let i = 0; i < len; i += CHUNK_SIZE) {
      const chunk = buffer.subarray(i, Math.min(i + CHUNK_SIZE, len));
      // String.fromCharCode 接受多个参数，但不能太多
      binary += String.fromCharCode(...Array.from(chunk));
    }

    const base64 = btoa(binary);

    return `data:${contentType};base64,${base64}`;
  } catch (error) {
    console.error('图片加载失败:', imageUrl, error);
    return null;
  }
}

/**
 * 收集试题中的所有图片信息
 */
function collectQuestionImages(question: Question): ImageInfo[] {
  const images: ImageInfo[] = [];

  // 收集题干图片
  if (question.stemImages && question.stemImages.length > 0) {
    for (const img of question.stemImages) {
      if (img.src) {
        images.push({
          url: img.src,
          location: 'stem'
        });
      }
    }
  }

  // 收集选项图片
  if (question.options && question.options.length > 0) {
    for (const opt of question.options) {
      if (opt.image) {
        images.push({
          url: opt.image,
          location: 'option',
          optionKey: opt.key || opt.label
        });
      }
    }
  }

  return images;
}

/**
 * 构建试题文本提示词
 */
function buildTextPrompt(question: Question, imageInfos: ImageInfo[]): string {
  // 构建选项文本，标注哪些选项有图片
  let optionsText = '无';
  if (question.options && question.options.length > 0) {
    const optionLines = question.options.map(o => {
      const key = o.key || o.label;
      if (o.image) {
        return `${key}. [见选项${key}图片]`;
      }
      return `${key}. ${o.content}`;
    });
    optionsText = optionLines.join('\n');
  }

  // 标注题干图片
  let stemNote = '';
  const stemImageCount = imageInfos.filter(i => i.location === 'stem').length;
  if (stemImageCount > 0) {
    stemNote = `\n【题干图片】共${stemImageCount}张，请结合图片分析`;
  }

  // 标注选项图片
  const optionImages = imageInfos.filter(i => i.location === 'option');
  let optionNote = '';
  if (optionImages.length > 0) {
    const optionKeys = optionImages.map(i => i.optionKey).join('、');
    optionNote = `\n【选项图片】选项 ${optionKeys} 包含图片`;
  }

  return `
【学科】${question.subject || '未知'}
【学段】${question.educationLevel || '未知'}
【题型】${question.type || '未知'}
【题干】${question.stem || ''}${stemNote}
【选项】
${optionsText}${optionNote}
【答案】${question.answer || '未知'}
【原始解析】${question.analysis || '未知'}
【来源】${question.source || '未知'}
`.trim();
}

/**
 * 获取系统提示词
 */
function getSystemPrompt(educationLevel: string, subject: string, hasImages: boolean): string {

  // 获取对应学科学段的知识点树
  const knowledgeTree = getKnowledgeTree(subject, educationLevel);
  const knowledgePointsList = extractLeafKnowledgePoints(knowledgeTree);
  const knowledgeTreeText = formatKnowledgeTreeForPrompt(knowledgeTree);

  // 知识点说明部分
  let knowledgeSection = '';
  if (knowledgePointsList.length > 0) {
    knowledgeSection = `
## 标准知识点体系
以下是${educationLevel}${subject}的标准知识点分类，请从中选择最匹配的知识点（必须使用下列名称）：

${knowledgeTreeText}

**可选知识点列表**（共${knowledgePointsList.length}个）：
${knowledgePointsList.join('、')}
`;
  }

  // 图片说明
  const imageNote = hasImages
    ? '\n**注意**：本题包含图片，请仔细观察图片内容，结合题干进行分析。'
    : '';

  return `你是一位专业的${educationLevel}${subject}教研专家。请分析以下试题，返回优化标签信息。${imageNote}

## 任务要求
1. 判断试题适用的**年级**（初中返回7/8/9，高中返回10/11/12）
2. 判断试题的**难度等级**（必须返回：易/较易/中档/较难/难）
3. 识别试题涉及的**知识点**（最多3个，必须从标准知识点列表中选择）
4. 判断试题**题类**（必须返回：常考题/易错题/好题/压轴题/优选题）
5. 生成**详细解析**（包含解题思路和关键步骤，支持LaTeX公式如 $x^2$）
${knowledgeSection}
## 难度定义
- 易: 基本概念直接应用
- 较易: 简单推理或公式应用
- 中档: 需要2-3步推理
- 较难: 综合分析，多知识点
- 难: 创新思维或竞赛级别

## 输出格式
请严格按照以下JSON格式输出，不要添加任何其他内容：
{
  "grade": "7|8|9|10|11|12",
  "difficulty": "易|较易|中档|较难|难",
  "topics": ["知识点1", "知识点2", "知识点3"],
  "category": "常考题|易错题|好题|压轴题|优选题",
  "analysis": "详细解析内容（支持LaTeX）",
  "reasoning": "你的推理过程（说明为什么选择这些标签）"
}`;
}

/**
 * 构建多模态消息内容
 */
async function buildMultimodalContent(
  textPrompt: string,
  imageInfos: ImageInfo[]
): Promise<MessageContentPart[]> {
  const parts: MessageContentPart[] = [];

  // 添加文本部分
  parts.push({
    type: 'text',
    text: textPrompt
  });

  // 添加题干图片
  const stemImages = imageInfos.filter(i => i.location === 'stem');
  for (let i = 0; i < stemImages.length; i++) {
    const base64 = await fetchImageAsBase64(stemImages[i].url);
    if (base64) {
      parts.push({
        type: 'text',
        text: `[题干图片${i + 1}]:`
      });
      parts.push({
        type: 'image_url',
        image_url: { url: base64 }
      });
    }
  }

  // 添加选项图片
  const optionImages = imageInfos.filter(i => i.location === 'option');
  for (const optImg of optionImages) {
    const base64 = await fetchImageAsBase64(optImg.url);
    if (base64) {
      parts.push({
        type: 'text',
        text: `[选项${optImg.optionKey}图片]:`
      });
      parts.push({
        type: 'image_url',
        image_url: { url: base64 }
      });
    }
  }

  return parts;
}

/**
 * 调用AI优化单道试题（支持多模态）
 */
export async function optimizeQuestion(question: Question): Promise<AIOptimizeResult> {
  // 收集图片信息
  const imageInfos = collectQuestionImages(question);
  const hasImages = imageInfos.length > 0;

  // 构建系统提示词
  const systemPrompt = getSystemPrompt(
    question.educationLevel || '初中',
    question.subject || '数学',
    hasImages
  );

  // 构建用户消息
  const textPrompt = buildTextPrompt(question, imageInfos);

  let userContent: MessageContent;

  if (hasImages) {
    // 多模态消息
    userContent = await buildMultimodalContent(textPrompt, imageInfos);
  } else {
    // 纯文本消息
    userContent = textPrompt;
  }

  const messages: ChatMessage[] = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: userContent }
  ];

  try {
    const response = await aiClient.post<ChatResponse>('/chat/completions', {
      model: AI_CONFIG.model,
      messages,
      temperature: 0.3,
      max_tokens: 2000
    });

    const content = response.data.choices[0]?.message?.content || '';
    const result = parseAIResponse(content);

    // 添加调试信息
    result.debug = {
      prompt: messages,
      rawResponse: response.data
    };

    if (hasImages) {
      result.reasoning = `[包含${imageInfos.length}张图片] ` + (result.reasoning || '');
    }

    return result;
  } catch (error) {
    console.error('AI优化请求失败:', error);
    throw error;
  }
}

/**
 * 解析AI响应内容
 */
function parseAIResponse(content: string): AIOptimizeResult {
  try {
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return {
        grade: parsed.grade,
        difficulty: parsed.difficulty,
        topics: Array.isArray(parsed.topics) ? parsed.topics.slice(0, 3) : [],
        category: parsed.category,
        analysis: parsed.analysis,
        reasoning: parsed.reasoning
      };
    }
  } catch (e) {
    console.warn('AI响应解析失败，返回原始内容:', content);
  }

  return {
    reasoning: content
  };
}

/**
 * 批量优化试题
 */
export async function batchOptimizeQuestions(
  questions: Question[],
  onProgress?: (current: number, total: number, result?: AIOptimizeResult) => void
): Promise<{ question: Question; result: AIOptimizeResult; error?: string }[]> {
  const results: { question: Question; result: AIOptimizeResult; error?: string }[] = [];

  for (let i = 0; i < questions.length; i++) {
    const question = questions[i];

    try {
      const result = await optimizeQuestion(question);
      results.push({ question, result });
      onProgress?.(i + 1, questions.length, result);
    } catch (error: unknown) {
      const errorMsg = error instanceof Error ? error.message : '未知错误';
      results.push({ question, result: {}, error: errorMsg });
      onProgress?.(i + 1, questions.length);
    }

    // 请求间隔，避免频率限制
    if (i < questions.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  return results;
}

/**
 * 测试AI连接
 */
export async function testAIConnection(): Promise<{ success: boolean; message: string; latency?: number }> {
  const startTime = Date.now();

  try {
    const response = await aiClient.post<ChatResponse>('/chat/completions', {
      model: AI_CONFIG.model,
      messages: [
        { role: 'user', content: '你好，请回复"连接成功"' }
      ],
      max_tokens: 50
    });

    const latency = Date.now() - startTime;
    const content = response.data.choices[0]?.message?.content || '';

    return {
      success: true,
      message: content,
      latency
    };
  } catch (error: unknown) {
    const errorMsg = error instanceof Error ? error.message : '连接失败';
    return {
      success: false,
      message: errorMsg
    };
  }
}

// 导出配置（用于调试）
export const aiConfig = {
  model: AI_CONFIG.model,
  baseURL: AI_CONFIG.baseURL
};

// ==================== 异步任务管理 ====================

// 任务状态
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

// 异步任务接口
export interface AsyncTask {
  id: string;                    // 任务ID
  status: TaskStatus;            // 任务状态
  totalCount: number;            // 总题目数
  completedCount: number;        // 已完成数
  failedCount: number;           // 失败数
  currentQuestion?: string;      // 当前处理的题目ID
  results: TaskResult[];         // 已完成的结果
  startTime: number;             // 开始时间
  endTime?: number;              // 结束时间
  error?: string;                // 错误信息
}

// 单个结果
export interface TaskResult {
  questionId: string;
  questionNumber: number;
  result: AIOptimizeResult;
  error?: string;
  timestamp: number;
}

// 任务存储（内存中）
const taskStore = new Map<string, AsyncTask>();

// 任务控制器（用于取消）
const taskControllers = new Map<string, AbortController>();

/**
 * 生成任务ID
 */
function generateTaskId(): string {
  return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 创建异步优化任务
 * @param questions 试题列表
 * @returns 任务ID
 */
export function createAsyncOptimizeTask(questions: Question[]): string {
  const taskId = generateTaskId();
  const controller = new AbortController();

  // 初始化任务
  const task: AsyncTask = {
    id: taskId,
    status: 'pending',
    totalCount: questions.length,
    completedCount: 0,
    failedCount: 0,
    results: [],
    startTime: Date.now()
  };

  taskStore.set(taskId, task);
  taskControllers.set(taskId, controller);

  // 异步执行（不阻塞）
  executeAsyncTask(taskId, questions, controller.signal);

  return taskId;
}

/**
 * 执行异步任务
 */
async function executeAsyncTask(
  taskId: string,
  questions: Question[],
  signal: AbortSignal
): Promise<void> {
  const task = taskStore.get(taskId);
  if (!task) return;

  task.status = 'running';

  for (let i = 0; i < questions.length; i++) {
    // 检查是否被取消
    if (signal.aborted) {
      task.status = 'cancelled';
      task.endTime = Date.now();
      return;
    }

    const question = questions[i];
    task.currentQuestion = question.id;

    try {
      const result = await optimizeQuestion(question);

      task.results.push({
        questionId: question.id,
        questionNumber: question.questionNumber,
        result,
        timestamp: Date.now()
      });
      task.completedCount++;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '未知错误';

      task.results.push({
        questionId: question.id,
        questionNumber: question.questionNumber,
        result: {},
        error: errorMsg,
        timestamp: Date.now()
      });
      task.failedCount++;
    }

    // 请求间隔
    if (i < questions.length - 1 && !signal.aborted) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  task.status = 'completed';
  task.currentQuestion = undefined;
  task.endTime = Date.now();
}

/**
 * 查询任务状态
 * @param taskId 任务ID
 * @returns 任务信息或null
 */
export function getTaskStatus(taskId: string): AsyncTask | null {
  return taskStore.get(taskId) || null;
}

/**
 * 查询任务进度
 * @param taskId 任务ID
 * @returns 进度信息
 */
export function getTaskProgress(taskId: string): {
  status: TaskStatus;
  progress: number;
  completed: number;
  failed: number;
  total: number;
  currentQuestion?: string;
  elapsedTime: number;
} | null {
  const task = taskStore.get(taskId);
  if (!task) return null;

  const progress = task.totalCount > 0
    ? Math.round((task.completedCount / task.totalCount) * 100)
    : 0;

  const elapsedTime = (task.endTime || Date.now()) - task.startTime;

  return {
    status: task.status,
    progress,
    completed: task.completedCount,
    failed: task.failedCount,
    total: task.totalCount,
    currentQuestion: task.currentQuestion,
    elapsedTime
  };
}

/**
 * 获取任务结果
 * @param taskId 任务ID
 * @param fromIndex 从第几个结果开始（用于增量获取）
 * @returns 结果列表
 */
export function getTaskResults(taskId: string, fromIndex: number = 0): TaskResult[] {
  const task = taskStore.get(taskId);
  if (!task) return [];

  return task.results.slice(fromIndex);
}

/**
 * 取消任务
 * @param taskId 任务ID
 * @returns 是否成功
 */
export function cancelTask(taskId: string): boolean {
  const controller = taskControllers.get(taskId);
  if (!controller) return false;

  controller.abort();
  return true;
}

/**
 * 删除任务（清理内存）
 * @param taskId 任务ID
 */
export function deleteTask(taskId: string): void {
  taskStore.delete(taskId);
  taskControllers.delete(taskId);
}

/**
 * 获取所有任务列表
 */
export function getAllTasks(): AsyncTask[] {
  return Array.from(taskStore.values());
}

/**
 * 清理已完成的任务（保留最近N个）
 * @param keepCount 保留数量
 */
export function cleanupCompletedTasks(keepCount: number = 5): void {
  const tasks = Array.from(taskStore.entries())
    .filter(([_, task]) => task.status === 'completed' || task.status === 'cancelled' || task.status === 'failed')
    .sort((a, b) => (b[1].endTime || 0) - (a[1].endTime || 0));

  // 删除超出保留数量的任务
  tasks.slice(keepCount).forEach(([id]) => {
    deleteTask(id);
  });
}

/**
 * 轮询任务状态（返回Promise，直到任务完成）
 * @param taskId 任务ID
 * @param onProgress 进度回调
 * @param pollInterval 轮询间隔（毫秒）
 */
export function pollTaskUntilComplete(
  taskId: string,
  onProgress?: (progress: ReturnType<typeof getTaskProgress>) => void,
  pollInterval: number = 1000
): Promise<AsyncTask | null> {
  return new Promise((resolve) => {
    const poll = () => {
      const task = getTaskStatus(taskId);

      if (!task) {
        resolve(null);
        return;
      }

      const progress = getTaskProgress(taskId);
      if (progress) {
        onProgress?.(progress);
      }

      if (task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled') {
        resolve(task);
        return;
      }

      setTimeout(poll, pollInterval);
    };

    poll();
  });
}
