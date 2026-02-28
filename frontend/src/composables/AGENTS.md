# 智研题库云 - 前端 Composables 规范

## OVERVIEW
封装复杂业务逻辑与副作用，为组件提供响应式状态与原子化操作的 Composition API 集合。

## WHERE TO LOOK
| 功能模块 | 关键文件 | 核心职责 |
| :--- | :--- | :--- |
| **上传核心** | `upload-management/useUploadOperation.ts` | 驱动 ZIP 上传流、分片进度控制及上传状态机转换 |
| **记录管理** | `upload-management/useUploadHistory.ts` | 维护上传历史列表的响应式分页、筛选及删除操作 |
| **实时日志** | `upload-management/useUploadLogs.ts` | 监听后端日志流，管理日志缓冲区及前端展示格式化 |

## CONVENTIONS
- **返回结构**: 统一返回**普通对象**。状态变量保持为 `Ref` 以支持安全解构，禁止返回 `toRefs(reactive)`。
- **状态管理**:
  - 内部状态使用 `ref` 定义；对外暴露时，关键状态建议使用 `readonly()` 包裹，强制通过提供的函数修改。
  - 对于强关联的数据结构（如分页信息）可使用 `reactive`。
- **副作用清理**: 必须在 `onUnmounted` 或 `onDeactivated` 中显式清理计时器、SSE 连接、DOM 监听或取消未完成的请求。
- **依赖处理**:
  - 传入参数若需支持响应式，应使用 `MaybeRefOrGetter` 类型并配合 `toValue` 使用。
  - Composable 之间可以相互调用，但应避免循环依赖。
- **逻辑分离**: 保持 Composable 纯粹性。它只负责**数据逻辑**和**副作用**，不应感知具体的 UI 结构或样式。

## ANTI-PATTERNS
- ❌ **内部修改 Props**: 绝不应在 Composable 内部尝试修改组件传入的 `props`。
- ❌ **隐式依赖**: 避免依赖未在参数中声明的全局变量（Pinia Store 除外，但应优先作为参数传入）。
- ❌ **包含静态配置**: 巨大的常量配置应移至 `src/utils/constants.ts` 而非留在 Composable 内部。
- ❌ **逻辑臃肿**: 单个文件行数超过 300 行（如 `useUploadOperation.ts`）时，需考虑将"状态定义"、"API 调用"与"格式化工具"进一步拆分。