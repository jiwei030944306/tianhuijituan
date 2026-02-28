import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// 学科名称映射（英文代码 -> 中文名）
const SUBJECT_NAMES: Record<string, string> = {
  chinese: '语文',
  math: '数学',
  english: '英语',
  physics: '物理',
  chemistry: '化学',
  biology: '生物',
  geography: '地理',
  politics: '道德与法治',
  technology: '通用技术',
};

// 反向映射：中文名 -> 英文代码
const SUBJECT_CODES: Record<string, string> = {
  '语文': 'chinese',
  '数学': 'math',
  '英语': 'english',
  '物理': 'physics',
  '化学': 'chemistry',
  '生物': 'biology',
  '地理': 'geography',
  '道德与法治': 'politics',
  '通用技术': 'technology',
};

// 学科学段短代码映射表
const FOLDER_CODE_MAP: Record<string, string> = {
  // 高中
  '高中-chinese': 'h8c3n4',
  '高中-math': 'h7s9m2',
  '高中-english': 'h9e5n1',
  '高中-physics': 'h1p8h2',
  '高中-chemistry': 'h2c7h3',
  '高中-biology': 'h3b6h4',
  '高中-geography': 'h5g4h6',
  '高中-technology': 'h6t3h7',
  // 初中
  '初中-chinese': 'm8c3n4',
  '初中-math': 'm7s9m2',
  '初中-english': 'm9e5n1',
  '初中-physics': 'm1p8h2',
  '初中-chemistry': 'm2c7h3',
  '初中-biology': 'm3b6h4',
  '初中-geography': 'm5g4h6',
  '初中-politics': 'm6p3h7',
};

export const useContextStore = defineStore('context', () => {
  // State
  const grade = ref<'junior' | 'senior' | null>(null);
  const subject = ref<string | null>(null);  // 英文代码
  const folderCode = ref<string | null>(null);
  const teacherName = ref<string>('张老师');  // 后期从用户信息获取

  // Computed
  const subjectName = computed(() => {
    return subject.value ? SUBJECT_NAMES[subject.value] || subject.value : '';
  });

  const levelName = computed(() => {
    if (!grade.value) return '';
    return grade.value === 'senior' ? '高中' : '初中';
  });

  const contextLabel = computed(() => {
    if (!levelName.value || !subjectName.value) return '';
    return `${levelName.value}${subjectName.value}`;
  });

  // Actions
  function setContext(newGrade: 'junior' | 'senior', newSubject: string) {
    grade.value = newGrade;
    
    // 转换中文科目名为英文代码（如果传入的是中文）
    const subjectCode = SUBJECT_CODES[newSubject] || newSubject;
    subject.value = subjectCode;
    
    // 生成folder_code（必须使用英文代码查找）
    const level = newGrade === 'senior' ? '高中' : '初中';
    const key = `${level}-${subjectCode}`;
    folderCode.value = FOLDER_CODE_MAP[key] || generateRandomCode(6);
    
    // 持久化(保存英文代码)
    localStorage.setItem('zy_context', JSON.stringify({
      grade: newGrade,
      subject: subjectCode,  // 保存英文代码而不是原始参数
      folderCode: folderCode.value,
      teacherName: teacherName.value
    }));
  }

  function loadFromStorage() {
    const saved = localStorage.getItem('zy_context');
    if (saved) {
      const parsed = JSON.parse(saved);
      grade.value = parsed.grade;

      // 转换中文科目名为英文代码(兼容旧数据)
      const subjectCode = SUBJECT_CODES[parsed.subject] || parsed.subject;
      subject.value = subjectCode;

      folderCode.value = parsed.folderCode;
      if (parsed.teacherName) {
        teacherName.value = parsed.teacherName;
      }
    }
  }

  function setTeacherName(name: string) {
    teacherName.value = name;
    const saved = localStorage.getItem('zy_context');
    if (saved) {
      const parsed = JSON.parse(saved);
      parsed.teacherName = name;
      localStorage.setItem('zy_context', JSON.stringify(parsed));
    }
  }

  function clearContext() {
    grade.value = null;
    subject.value = null;
    folderCode.value = null;
    localStorage.removeItem('zy_context');
  }

  // 辅助函数：生成6位随机码
  function generateRandomCode(length: number = 6): string {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  // Auto-load on init
  loadFromStorage();

  return {
    // State
    grade,
    subject,
    subjectName,
    folderCode,
    teacherName,
    // Computed
    levelName,
    contextLabel,
    // Actions
    setContext,
    setTeacherName,
    loadFromStorage,
    clearContext
  };
});
