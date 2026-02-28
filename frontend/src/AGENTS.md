# Frontend Source - AGENTS.md

**OVERVIEW**: Vue 3 + TypeScript 驱动的智研题库云前端核心源码。

## STRUCTURE

- **api/**: Axios 封装与后端接口定义 (如 `question.ts`)
- **components/**: 全局通用 UI 组件与布局原子组件
- **composables/**: 业务逻辑复用 Hooks (Vue Composition API)
- **config/**: 全局配置、常量定义与环境变量
- **router/**: Vue Router 路由配置、中间件与导航守卫
- **stores/**: Pinia 状态管理 (用户信息、全局上下文、业务状态)
- **types/**: 全局 TypeScript 接口 (Interfaces) 与类型声明
- **utils/**: 辅助工具函数 (数据格式化、校验、加密等)
- **views/**: 页面级组件与业务模块入口 (P1-P5 核心视图)

## WHERE TO LOOK

- **入口文件**: `main.ts` (应用初始化、插件注册、样式引入)
- **根容器**: `App.vue` (顶级布局骨架)
- **API 定义**: `api/` (各模块接口对接点)
- **路由核心**: `router/index.ts` (单页应用路由映射)
- **全局状态**: `stores/user.ts` (鉴权), `stores/context.ts` (全局状态)
- **核心页面**: `views/UploadManagement.vue`, `views/QuestionCheckNew.vue`

## CONVENTIONS

- **开发模式**: 必须使用 `<script setup>` 和 Composition API
- **命名规范**: 组件名 PascalCase，变量名 camelCase，目录名 kebab-case
- **类型安全**: 严格 TypeScript 模式，禁止使用 `any`，接口需在 `types/` 定义
- **状态管理**: 涉及多组件共享的数据必须通过 Pinia store 管理
- **样式规范**: 优先使用 Scoped CSS，确保组件样式隔离

## ANTI-PATTERNS

- ❌ **逻辑堆砌**: 禁止在 `views` 组件中直接编写复杂的 API 调用或计算逻辑 (应提取至 `composables`)
- ❌ **DOM 操作**: 禁止直接使用 `document.querySelector` (应使用 `ref` 或 Vue 指令)
- ❌ **隐式类型**: 禁止忽略 API 返回值的类型定义
- ❌ **深度耦合**: 禁止父组件直接修改子组件内部状态 (应使用 props/emits 或 store)
