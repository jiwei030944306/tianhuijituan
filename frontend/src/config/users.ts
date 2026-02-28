/**
 * 用户配置文件
 * 在此文件中管理所有用户账号、权限和角色
 */

// 用户权限类型
export type UserRole = 'admin' | 'teacher' | 'student';

// 用户权限定义
export const PERMISSIONS = {
  // 管理员权限
  admin: ['all', 'upload', 'edit', 'delete', 'view', 'manage'],
  // 教师权限
  teacher: ['upload', 'edit', 'view'],
  // 学生权限
  student: ['view']
} as const;

// 用户权限类型（从 PERMISSIONS 推断）
export type Permission = typeof PERMISSIONS.admin[number] | typeof PERMISSIONS.teacher[number] | typeof PERMISSIONS.student[number];

// 用户接口
export interface UserConfig {
  id: string;
  username: string;
  password?: string;  // 可选，生产环境应该从后端验证
  name: string;
  role: UserRole;
  permissions: Permission[];
  enabled: boolean;   // 是否启用
  remark?: string;    // 备注
  level?: 'junior' | 'senior' | null;  // 学段：初中/高中，null表示不预选
  subject?: string | null;               // 学科代码，null表示不预选
}

// 用户配置列表（12个用户）
export const USERS: UserConfig[] = [
  // 1. admin（不预选学科学段）
  {
    id: 'user-001',
    username: 'jiwei',
    password: 'test123',
    name: '籍伟',
    role: 'admin',
    permissions: PERMISSIONS.admin,
    enabled: true,
    remark: '系统管理员',
    level: null,
    subject: null
  },
  // 2-4. 高中教师（语文、数学、英语）
  {
    id: 'user-002',
    username: 'gaozhong-yuwen',
    password: 'test123',
    name: '高中-语文老师',
    role: 'teacher',
    permissions: PERMISSIONS.teacher,
    enabled: true,
    remark: '高中语文教师',
    level: 'senior',
    subject: 'chinese'
  },
  {
    id: 'user-003',
    username: 'gaozhong-shuxue',
    password: 'test123',
    name: '高中-数学老师',
    role: 'teacher',
    permissions: PERMISSIONS.teacher,
    enabled: true,
    remark: '高中数学教师',
    level: 'senior',
    subject: 'math'
  },
  {
    id: 'user-004',
    username: 'gaozhong-yingyu',
    password: 'test123',
    name: '高中-英语老师',
    role: 'teacher',
    permissions: PERMISSIONS.teacher,
    enabled: true,
    remark: '高中英语教师',
    level: 'senior',
    subject: 'english'
  },
  // 5-7. 初中教师（语文、数学、英语）
  {
    id: 'user-005',
    username: 'chuzhong-yuwen',
    password: 'test123',
    name: '初中-语文老师',
    role: 'teacher',
    permissions: PERMISSIONS.teacher,
    enabled: true,
    remark: '初中语文教师',
    level: 'junior',
    subject: 'chinese'
  },
  {
    id: 'user-006',
    username: 'chuzhong-shuxue',
    password: 'test123',
    name: '初中-数学老师',
    role: 'teacher',
    permissions: PERMISSIONS.teacher,
    enabled: true,
    remark: '初中数学教师',
    level: 'junior',
    subject: 'math'
  },
  {
    id: 'user-007',
    username: 'chuzhong-yingyu',
    password: 'test123',
    name: '初中-英语老师',
    role: 'teacher',
    permissions: PERMISSIONS.teacher,
    enabled: true,
    remark: '初中英语教师',
    level: 'junior',
    subject: 'english'
  },
  // 8-9. 学生（只区分学段，学科用占位符）
  {
    id: 'user-008',
    username: 'gaozhong-student',
    password: 'test123',
    name: '高中-学生',
    role: 'student',
    permissions: PERMISSIONS.student,
    enabled: true,
    remark: '高中学生代表',
    level: 'senior',
    subject: 'placeholder'
  },
  {
    id: 'user-009',
    username: 'chuzhong-student',
    password: 'test123',
    name: '初中-学生',
    role: 'student',
    permissions: PERMISSIONS.student,
    enabled: true,
    remark: '初中学生代表',
    level: 'junior',
    subject: 'placeholder'
  },
  // 10-12. 保留原有用户（更新配置）
  {
    id: 'user-010',
    username: 'zhangsan',
    password: 'test123',
    name: '张三',
    role: 'teacher',
    permissions: PERMISSIONS.teacher,
    enabled: true,
    remark: '数学教师',
    level: 'senior',
    subject: 'math'
  },
  {
    id: 'user-011',
    username: 'lisi',
    password: 'test123',
    name: '李四',
    role: 'teacher',
    permissions: PERMISSIONS.teacher,
    enabled: true,
    remark: '语文教师',
    level: 'junior',
    subject: 'chinese'
  },
  {
    id: 'user-012',
    username: 'wangwu',
    password: 'test123',
    name: '王五',
    role: 'student',
    permissions: PERMISSIONS.student,
    enabled: true,
    remark: '学生代表',
    level: 'junior',
    subject: 'math'
  }
];

// 工具函数：根据用户名查找用户
export function findUserByUsername(username: string): UserConfig | undefined {
  return USERS.find(user => user.username === username);
}

// 工具函数：验证用户登录
export function validateUser(username: string, password: string): UserConfig | null {
  const user = findUserByUsername(username);
  if (!user) return null;
  if (!user.enabled) return null;
  if (user.password && user.password !== password) return null;
  return user;
}

// 工具函数：获取用户默认权限
export function getDefaultPermissions(role: UserRole): Permission[] {
  return [...PERMISSIONS[role]];
}

// 角色显示映射（权限→角色显示名称）
export const ROLE_DISPLAY_MAP: Record<UserRole, string> = {
  'admin': '系统管理员',
  'teacher': '教研员',
  'student': '学员'
};

// 工具函数：获取角色显示名称
export function getRoleDisplayName(role: UserRole): string {
  return ROLE_DISPLAY_MAP[role] || role;
}
