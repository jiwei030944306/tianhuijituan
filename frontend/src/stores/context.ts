import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// 学科名称映射（英文代码 -> 中文名）
// 初中代码和高中代码(带2)映射到同一中文名
const SUBJECT_NAMES: Record<string, string> = {
  chinese: '语文', chinese2: '语文',
  math: '数学', math2: '数学',
  english: '英语', english2: '英语',
  physics: '物理', physics2: '物理',
  chemistry: '化学', chemistry2: '化学',
  bio: '生物', bio2: '生物',
  geo: '地理', geo2: '地理',
  history: '历史', history2: '历史',
  politics: '政治', politics2: '政治',
};

// 反向映射：中文名 -> 初中英文代码（默认）
const SUBJECT_CODES: Record<string, string> = {
  '语文': 'chinese',
  '数学': 'math',
  '英语': 'english',
  '物理': 'physics',
  '化学': 'chemistry',
  '生物': 'bio',
  '地理': 'geo',
  '历史': 'history',
  '政治': 'politics',
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

    // 转换中文科目名为英文基础代码（如果传入的是中文）
    const baseCode = SUBJECT_CODES[newSubject] || newSubject;

    // 根据学段生成完整代码：高中加2，初中不加
    const subjectCode = newGrade === 'senior' ? `${baseCode}2` : baseCode;
    subject.value = subjectCode;

    // folderCode 直接使用学科代码
    folderCode.value = subjectCode;

    // 持久化(保存完整代码)
    localStorage.setItem('zy_context', JSON.stringify({
      grade: newGrade,
      subject: subjectCode,
      folderCode: folderCode.value,
      teacherName: teacherName.value
    }));
  }

  function loadFromStorage() {
    const saved = localStorage.getItem('zy_context');
    if (saved) {
      const parsed = JSON.parse(saved);
      grade.value = parsed.grade;

      // 兼容旧数据格式转换
      let subjectCode = parsed.subject;

      // 旧格式映射：biology -> bio, geography -> geo
      const legacyMapping: Record<string, string> = {
        'biology': 'bio', 'biology2': 'bio2',
        'geography': 'geo', 'geography2': 'geo2',
      };
      if (legacyMapping[subjectCode]) {
        subjectCode = legacyMapping[subjectCode];
      }

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
