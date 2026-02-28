/**
 * Vitest 测试环境配置
 * 全局注册 Element Plus 和 Pinia
 */
import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 创建 Pinia 实例
const pinia = createPinia()

// 全局注册 Element Plus 和 Pinia
config.global.plugins = [ElementPlus, pinia]

// 全局注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  config.global.components[key] = component
}

// 全局 mocks
config.global.mocks = {
  $t: (msg: string) => msg,
  $router: {
    push: () => Promise.resolve(),
    replace: () => Promise.resolve()
  },
  $route: {
    path: '/',
    params: {},
    query: {}
  }
}

console.log('✅ Vitest setup: Element Plus + Pinia registered globally')
