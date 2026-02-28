# 智研题库云系统 - 页面视图 (Views) 知识库

**生成时间**: 2026-02-05
**位置**: `frontend/src/views`

## OVERVIEW
本目录包含智研题库云系统的所有页面级 Vue 组件，负责业务逻辑流转、全局状态绑定与复杂组件组合。

## STRUCTURE

### 核心页面组件 (4个)
| 组件 | 路由 | 中心 | 说明 |
|------|------|------|------|
| `Landing.vue` | `/landing` | - | 登录页/学段学科选择入口 |
| `Home.vue` | `/home` | - | 核心工作台，6大核心中心导航入口 |
| `UploadManagement.vue` | `/upload` | **P0** | 上传管理中心核心入口，实现大规模试题上传任务的监控与管理 |
| `QuestionCheckNew.vue` | `/check` | **P1** | 试题自检与同步中心核心入口，通过高度组件化的方式组织试题筛选与处理流程 |
| `SymbolLab.vue` | `/lab` | - | LaTeX公式渲染测试工具（开发工具） |

### 页面子组件目录
- **`upload-management/`**: P0-上传管理中心专用的局部业务组件，支持实时终端监控与历史记录
- **`QuestionCheckNew/`**: P1-试题自检与同步中心及其专属子组件（过滤器、统计卡片、巡检器、表格）
- **`dev-tools/`**: 开发工具组件（符号实验室等）

### 6大核心中心

| 中心 | 名称 | 路由 | 组件 | 状态 | 功能概述 |
|------|------|------|------|------|----------|
| **P0** | 上传管理中心 | `/upload` | `UploadManagement.vue` | ✅ 已上线 | ZIP/JSON批量上传、冲突检测、历史记录、实时日志 |
| **P1** | 试题自检与同步中心 | `/check` | `QuestionCheckNew.vue` | ✅ 已上线 | 批次管理、题目检视、内容校验、同步处理 |
| **P2** | 标化教研中心 | `/standardize` | - | 🚧 规划中 | 知识点打标、AI解析编写、人工审核 |
| **P3** | 成果总览与导出站 | `/export` | - | 🚧 规划中 | 精品题库浏览、试卷导出、教研心得 |
| **P4** | 全局监控看板 | `/monitor` | - | 📅 待规划 | 流转效率监控、错误分布、学科覆盖率统计 |
| **P5** | 日志与反馈中心 | `/logs` | - | 📅 待规划 | 错误日志聚合、Prompt修正、AI能力闭环训练 |

## P0-上传管理中心详细说明

**核心功能：**
- ✅ 文件夹/ZIP批量上传（JSON + 图片）
- ✅ 科目/学段/年级联动选择
- ✅ 实时上传进度显示
- ✅ 冲突检测与重复文件提示
- ✅ 上传历史记录管理（分页、删除）
- ✅ IDE风格实时终端日志
- ✅ 日志持久化（localStorage）
- ✅ 日志上报服务器

**页面子组件** (`upload-management/`):
- `UploadSidebar.vue` - 左侧边栏（环境信息、上传区、日志摘要）
- `StatsHeader.vue` - 统计面板（批次/题目/图片数量）
- `HistoryTable.vue` - 历史记录表格
- `LiveTerminal.vue` - 实时日志终端
- `BatchDetailDialog.vue` - 批次详情弹窗
- `ConflictDialog.vue` - 冲突处理弹窗
- `UploadDebugger.vue` - 完整日志调试器（Drawer）

## P1-试题自检与同步中心详细说明

**核心功能：**
- ✅ 试题批次列表展示
- ✅ 多维度筛选（科目/学段/年级/题型/难度）
- ✅ 题目详情检视（题干、选项、答案、解析）
- ✅ LaTeX公式渲染
- ✅ 图片预览与错误处理
- ✅ 批量操作与同步

**页面子组件** (`QuestionCheckNew/`):
- `QuestionFilters.vue` - 筛选器面板
- `QuestionTable.vue` - 题目表格
- `QuestionPagination.vue` - 分页组件
- `StatsCards.vue` - 统计卡片
- `BatchList.vue` - 批次列表
- `QuestionInspector/` - 题目巡检器
  - `index.vue` - 巡检器主组件
  - `PreviewTab.vue` - 预览标签页
  - `JsonTab.vue` - JSON数据标签页

## WHERE TO LOOK
- `Landing.vue`: 系统登录后的主导航页与门户入口（环境选择：学段/学科）。
- `Home.vue`: 核心工作台，6大核心中心入口导航与状态监控。
- `QuestionCheckNew.vue`: P1中心核心入口，通过高度组件化的方式组织试题筛选与处理流程。
- `UploadManagement.vue`: P0中心核心入口，实现大规模试题上传任务的监控与管理。
- `SymbolLab.vue`: LaTeX公式渲染测试工具（开发工具）。

## CONVENTIONS
- **逻辑分层**: 视图层仅负责组件拼装，复杂的业务计算应封装在 `stores/` 或 `composables/` 中。
- **状态管理**: 强制使用 Pinia 进行跨组件通信，页面初始化数据应由 Store 的 action 触发。
- **数据获取**: 必须通过 `src/api/` 模块进行 API 调用，严禁在视图层内直接硬编码 API 地址。
- **命名规范**: 页面根组件采用 PascalCase (如 `QuestionCheckNew.vue`)，辅助文件夹采用 kebab-case (如 `upload-management/`)。

## ANTI-PATTERNS
- ❌ **超长视图**: 单个 Vue 文件代码逻辑（除模板外）超过 300 行时必须进行组件拆分。
- ❌ **内联样式**: 严禁在页面组件中使用大量的 `<style>`，应优先使用全局 UI 变量或 UnoCSS/Tailwind。
- ❌ **硬编码路由**: 严禁硬编码 URL 跳转，必须使用 `vue-router` 的 `name` 属性进行编程导航。
- ❌ **忽略类型**: 严禁对 API 返回的数据使用 `any` 类型，必须在 `types/` 下定义或引用接口类型。
- ❌ **遗留备份**: 禁止保留 `-backup.vue` 文件，应直接提交至版本控制系统。
