import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { UserConfig, UserRole, Permission } from '@/config/users';
import { 
  USERS, 
  validateUser, 
  PERMISSIONS 
} from '@/config/users';

// 用户接口（从 UserConfig 转换，去掉密码等敏感信息）
export interface User {
  id: string;
  username: string;
  name: string;
  role: UserRole;
  permissions: Permission[];
  level?: 'junior' | 'senior' | null;  // 学段
  subject?: string | null;               // 学科
}

// 从 UserConfig 创建 User 对象（去掉密码，保留level和subject）
function createUserFromConfig(config: UserConfig): User {
  return {
    id: config.id,
    username: config.username,
    name: config.name,
    role: config.role,
    permissions: config.permissions,
    level: config.level,      // 新增：学段
    subject: config.subject   // 新增：学科
  };
}

export const useUserStore = defineStore('user', () => {
  // State
  const currentUser = ref<User | null>(null);
  const isLoggedIn = ref(false);

  // Computed
  const userName = computed(() => currentUser.value?.name || '');

  const hasPermission = computed(() => (permission: string): boolean => {
    if (!currentUser.value) return false;
    // admin 拥有所有权限
    if (currentUser.value.role === 'admin') return true;
    return currentUser.value.permissions.includes(permission as Permission);
  });

  // Actions
  function login(username: string, password: string): Promise<boolean> {
    return new Promise((resolve) => {
      // 模拟登录请求（实际项目中应调用后端API）
      setTimeout(() => {
        // 验证用户
        const userConfig = validateUser(username, password);
        
        if (userConfig) {
          // 登录成功
          currentUser.value = createUserFromConfig(userConfig);
          isLoggedIn.value = true;

          // 持久化（不保存密码，保留level和subject）
          localStorage.setItem('zy_user', JSON.stringify({
            username: userConfig.username,
            name: userConfig.name,
            role: userConfig.role,
            permissions: userConfig.permissions,
            level: userConfig.level,      // 新增
            subject: userConfig.subject   // 新增
          }));

          resolve(true);
        } else {
          // 登录失败
          resolve(false);
        }
      }, 500);
    });
  }

  function logout() {
    currentUser.value = null;
    isLoggedIn.value = false;
    localStorage.removeItem('zy_user');
  }

  function loadFromStorage() {
    const saved = localStorage.getItem('zy_user');
    if (saved) {
      const parsed = JSON.parse(saved);
      currentUser.value = {
        id: `user-${parsed.username}`,
        username: parsed.username,
        name: parsed.name,
        role: parsed.role,
        permissions: parsed.permissions,
        level: parsed.level,        // 新增
        subject: parsed.subject     // 新增
      };
      isLoggedIn.value = true;
    }
  }

  // Auto-load on init
  loadFromStorage();

  return {
    // State
    currentUser,
    isLoggedIn,
    userName,
    // Computed
    hasPermission,
    // Actions
    login,
    logout,
    loadFromStorage
  };
});

// 导出权限常量，供外部使用
export { PERMISSIONS };
