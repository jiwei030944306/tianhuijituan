<template>
  <div class="user-auth-widget">
    <!-- 登录按钮 -->
    <template v-if="!userStore.isLoggedIn">
      <button
        @click="showLoginModal = true"
        class="login-trigger-btn group"
      >
        <div class="user-avatar">
          <User :size="16" />
        </div>
        <span>登录</span>
      </button>
    </template>

    <!-- 已登录状态 -->
    <template v-else>
      <el-dropdown @command="handleCommand" trigger="click">
        <div class="user-info">
          <User :size="18" class="text-slate-600" />
          <span class="text-sm font-medium text-slate-700">{{ userStore.userName }}</span>
          <ChevronDown :size="16" class="text-slate-400" />
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <div class="flex items-center gap-2">
                <User :size="16" />
                <span>个人信息</span>
              </div>
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <div class="flex items-center gap-2">
                <Settings :size="16" />
                <span>设置</span>
              </div>
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <div class="flex items-center gap-2 text-red-600">
                <LogOut :size="16" />
                <span>退出登录</span>
              </div>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </template>

    <!-- 登录对话框 -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showLoginModal" class="login-modal-overlay" @click.self="showLoginModal = false">
          <Transition name="scale">
            <div v-if="showLoginModal" class="login-modal-container">
              <!-- 关闭按钮 -->
              <button
                @click="showLoginModal = false"
                class="close-btn"
              >
                <X :size="18" />
              </button>

              <!-- Logo和标题 -->
              <div class="login-header">
                <div class="logo">
                  <Zap :size="32" class="fill-white" />
                </div>
                <h2 class="login-title">欢迎回来</h2>
                <p class="login-subtitle">ZyCloud 智研题库协作云</p>
              </div>

              <!-- 登录表单 -->
              <form @submit.prevent="handleLogin" class="login-form">
                <!-- 用户名输入 -->
                <div class="form-group">
                  <label class="form-label">账号 / Email</label>
                  <div class="input-wrapper">
                    <User class="input-icon" :size="18" />
                    <input
                      v-model="loginForm.username"
                      type="text"
                      class="form-input"
                      placeholder="请输入用户名"
                      required
                    />
                  </div>
                </div>

                <!-- 密码输入 -->
                <div class="form-group">
                  <label class="form-label">密码 / Password</label>
                  <div class="input-wrapper">
                    <Lock class="input-icon" :size="18" />
                    <input
                      v-model="loginForm.password"
                      type="password"
                      class="form-input"
                      placeholder="请输入密码"
                      required
                    />
                  </div>
                </div>

                <!-- 记住我和忘记密码 -->
                <div class="form-options">
                  <label class="remember-me">
                    <input
                      v-model="loginForm.rememberMe"
                      type="checkbox"
                      class="checkbox"
                    />
                    <span>记住我 (30天)</span>
                  </label>
                  <a href="#" class="forgot-password" @click.prevent="handleForgotPassword">
                    忘记密码?
                  </a>
                </div>

                <!-- 登录按钮 -->
                <button
                  type="submit"
                  :disabled="loginLoading"
                  class="submit-btn"
                >
                  <template v-if="loginLoading">
                    <Loader2 class="animate-spin" :size="20" />
                    <span>验证身份中...</span>
                  </template>
                  <template v-else>
                    <span>立即登录</span>
                    <ArrowRight :size="18" />
                  </template>
                </button>
              </form>

              <!-- 底部提示 -->
              <div class="login-footer">
                <p class="footer-text">
                  还没有账号？
                  <a href="#" class="trial-link" @click.prevent="handleApplyTrial">
                    申请企业试用
                  </a>
                </p>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import {
  User, Lock, ChevronDown, Settings, LogOut, Zap, X, ArrowRight, Loader2
} from 'lucide-vue-next';

// Store
const userStore = useUserStore();

// State
const showLoginModal = ref(false);
const loginLoading = ref(false);
const loginForm = ref({
  username: '',
  password: '',
  rememberMe: false
});

// 页面加载时检查localStorage中的记住我状态
onMounted(() => {
  const rememberedUser = localStorage.getItem('zy_remembered_username');
  if (rememberedUser) {
    loginForm.value.username = rememberedUser;
    loginForm.value.rememberMe = true;
  }
});

// 登录处理
const handleLogin = async () => {
  if (!loginForm.value.username) {
    alert('请输入用户名');
    return;
  }

  loginLoading.value = true;
  try {
    const success = await userStore.login(loginForm.value.username, loginForm.value.password);
    if (success) {
      // 处理记住我
      if (loginForm.value.rememberMe) {
        localStorage.setItem('zy_remembered_username', loginForm.value.username);
      } else {
        localStorage.removeItem('zy_remembered_username');
      }

      showLoginModal.value = false;
      loginForm.value.password = '';
    } else {
      alert('登录失败，请检查用户名和密码');
    }
  } catch (error: unknown) {
    console.error('登录错误:', error);
    alert(`登录失败: ${error instanceof Error ? error.message : '请稍后重试'}`);
  } finally {
    loginLoading.value = false;
  }
};

// 忘记密码处理
const handleForgotPassword = () => {
  alert('请联系管理员重置密码\n邮箱: admin@zycloud.com');
};

// 申请试用处理
const handleApplyTrial = () => {
  alert('请联系管理员 admin@zycloud.com 开通试用账号。');
};

// 下拉菜单命令处理
const handleCommand = (command: string) => {
  if (command === 'logout') {
    if (confirm('确定要退出登录吗？')) {
      userStore.logout();
    }
  } else if (command === 'profile') {
    alert('个人信息功能开发中...');
  } else if (command === 'settings') {
    alert('设置功能开发中...');
  }
};
</script>

<style scoped>
.user-auth-widget {
  display: flex;
  align-items: center;
  z-index: 100;
}

/* 登录按钮样式 - 毛玻璃效果 */
.login-trigger-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 9999px;
  color: #475569;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.login-trigger-btn:hover {
  background: rgba(255, 255, 255, 1);
  color: #4f46e5;
  box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.2);
  transform: translateY(-1px);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.login-trigger-btn:hover .user-avatar {
  background: #eef2ff;
  color: #4f46e5;
}

/* 已登录用户样式 */
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f1f5f9;
}

/* 登录对话框遮罩 */
.login-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  padding: 16px;
}

/* 登录对话框容器 */
.login-modal-container {
  position: relative;
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  padding: 48px 32px 32px;
  border: 1px solid #f1f5f9;
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f8fafc;
  color: #94a3b8;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #64748b;
}

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 32px;
  margin-top: 8px;
}

.logo {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #6366f1 0%, #9333ea 100%);
  color: white;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.3);
}

.login-title {
  font-size: 24px;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: -0.025em;
  margin-bottom: 8px;
}

.login-subtitle {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

/* 登录表单 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-left: 4px;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: 14px 16px 14px 44px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #334155;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s;
  outline: none;
}

.form-input::placeholder {
  color: #94a3b8;
}

.form-input:hover {
  background: #f1f5f9;
}

.form-input:focus {
  background: white;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* 表单选项（记住我 + 忘记密码） */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  padding: 0 4px;
  margin-top: 4px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  cursor: pointer;
  transition: color 0.2s;
}

.remember-me:hover {
  color: #334155;
}

.checkbox {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid #cbd5e1;
  accent-color: #6366f1;
  cursor: pointer;
}

.forgot-password {
  color: #4f46e5;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s;
}

.forgot-password:hover {
  text-decoration: underline;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  padding: 14px;
  margin-top: 8px;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.3);
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #4338ca;
  transform: scale(1.02);
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 动画 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 底部提示 */
.login-footer {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
  text-align: center;
}

.footer-text {
  font-size: 12px;
  color: #94a3b8;
}

.trial-link {
  color: #4f46e5;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s;
}

.trial-link:hover {
  text-decoration: underline;
}

/* 过渡动画 - 淡入淡出 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 过渡动画 - 缩放 */
.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* 响应式适配 */
@media (max-width: 480px) {
  .login-modal-container {
    padding: 40px 24px 24px;
  }

  .login-title {
    font-size: 20px;
  }

  .logo {
    width: 56px;
    height: 56px;
  }
}
</style>