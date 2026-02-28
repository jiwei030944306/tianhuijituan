import type { Question, Difficulty, QuestionStatus, Subject, EducationLevel, Option, StemImage } from '@/types/question';

/**
 * 转换图片路径为可访问的 API URL
 * @param src 原始图片路径（如 ./xxx.jpg 或 images/xxx.jpg）
 * @param batchId 批次 ID
 * @returns 转换后的图片 URL
 */
function convertImageSrc(src: string, batchId?: string): string {
  if (!src || !batchId) return src;

  // 提取文件名：处理 ./xxx.jpg 或 images/xxx.jpg 格式
  const filename = src.replace(/^\.\//, '').replace(/^images\//, '');

  // 转换为 API URL
  return `/api/questions/batch/${batchId}/image/${filename}`;
}

/**
 * 转换后端或上传的原始 JSON 数据为前端统一的 Question 类型
 * @param jsonData 原始 JSON 数据数组
 * @param batchId 批次 ID（用于转换图片路径）
 * @returns 转换后的 Question 对象数组
 */
// Raw question item shape from backend/upload JSON
type RawQuestionItem = {
  id?: string;
  questionNumber?: number;
  stem?: string;
  options?: Option[];
  stemImages?: StemImage[];
  answer?: string;
  analysis?: string;
  topics?: string[];
  subject?: Subject;
  educationLevel?: EducationLevel;
  type?: string;
  difficulty?: Difficulty;
  [key: string]: any;
};

export function convertJsonToQuestions(jsonData: RawQuestionItem[], batchId?: string): Question[] {
  return jsonData.map(item => {
    // 处理选项：将 label 映射为 key 以适配 QuestionCard 组件
    const options: Option[] | undefined = item.options?.map((opt: Option) => ({
      ...opt,
      key: opt.label, // QuestionCard 使用 key 字段
      label: opt.label,
      content: opt.content,
      isCorrect: opt.isCorrect
    }));

    // 处理题干图片：转换相对路径为 API URL
    const stemImages: StemImage[] = (item.stemImages || []).map((img: StemImage) => ({
      ...img,
      src: convertImageSrc(img.src, batchId)
    }));

    // 构建 Question 对象
    return {
      id: item.id || `q-${Math.random().toString(36).substr(2, 9)}`,
      questionNumber: item.questionNumber,
      type: item.type || '选择题',
      difficulty: item.difficulty as Difficulty | undefined,
      status: 'active' as QuestionStatus,
      stem: item.stem || '',
      options,
      stemImages,
      topics: item.topics || [],
      answer: item.answer || '',
      analysis: item.analysis || '',
      // 分类信息（从 contextStore 注入或原始数据）
      subject: item.subject as Subject | undefined,
      educationLevel: item.educationLevel as EducationLevel | undefined,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
  });
}
