# 智研题库云 - 前端状态管理中心 (Stores)

**生成时间**: 2026-02-05
**作用**: 集中式响应式状态管理，驱动全局业务逻辑与 UI 同步。

## OVERVIEW
基于 Pinia 的应用状态中心，管理用户鉴权信息及系统运行时的全局上下文。

## WHERE TO LOOK

| 领域 | 文件 | 核心职责 |
|------|------|----------|
| **用户中心** | `user.ts` | 登录/登出、Token 校验、权限菜单、用户信息持久化 |
| **全局上下文** | `context.ts` | 页面标题、侧边栏状态、全局 Loading、公共配置数据 |

## CONVENTIONS (Pinia Setup Mode)

### 1. 结构规范
所有 Store 必须使用 **Setup 模式** (返回 `ref`, `computed`, `function`)：
- **State**: 使用 `ref()` 定义。
- **Getters**: 使用 `computed()` 派生。
- **Actions**: 普通函数（支持 `async`），负责 API 调用及状态修改。

### 2. 响应式安全
- 组件中解构 State 必须使用 `storeToRefs(store)`，防止丢失响应式。
- Actions 可直接解构调用。

### 3. 持久化策略
- **敏感数据 (Token)**: 必须结合 `localStorage` 且需进行校验。
- **UI 状态**: 根据用户体验决定是否持久化（如侧边栏折叠状态）。

## ANTI-PATTERNS (Store 避雷)

- ❌ **直接修改他人的 State**: 禁止 `storeA.count++`，必须通过 Store A 定义的 Action 修改。
- ❌ **解构陷阱**: 直接 `const { name } = useUserStore()` 会导致 UI 不更新。
- ❌ **逻辑膨胀**: 禁止在 Store 中处理复杂的 DOM 操作或组件级交互逻辑（Store 只管数据）。
- ❌ **冗余存储**: 能通过 Computed 计算得出的状态，严禁在 State 中重复定义。
- ❌ **大型对象堆积**: 避免在 State 中存储未处理的原始大 JSON，应根据 `types/` 下的 Schema 存储。