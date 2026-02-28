# Frontend Components - AGENTS.md

**OVERVIEW**: Vue 3 + TypeScript 驱动的可复用业务组件库。

## STRUCTURE

- **common/**: 全局通用 UI 组件 (如 `GlobalNavbar`, `HelpGuide`)
- **upload/**: 上传业务专用组件 (如 `UploadStep1`, `UploadHistory`)

## WHERE TO LOOK

- **核心业务组件**:
  - `FolderUploader.vue`: 处理文件夹上传逻辑与统计
  - `QuestionList.vue`: 题目列表展示、筛选与分页
  - `upload/UploadStep1/2/3.vue`: 分步上传流程拆解
- **数学公式渲染**:
  - `MathText.vue`: 基于 KaTeX 的文本与公式混排渲染
  - `LatexCard.vue`: LaTeX 内容的卡片式展示
- **UI 基础设施**:
  - `QuestionTable.vue`: 题目表格视图
  - `StatisticsPanel.vue`: 业务数据统计面板

## CONVENTIONS

- **开发模式**: 必须使用 `<script setup>` 和 Composition API。
- **类型定义**: Props 和 Emits 必须使用 TypeScript 接口定义。
  ```ts
  const props = defineProps<{
    data: Question[];
    loading?: boolean;
  }>();
  ```
- **UI 框架**: 优先使用 Element Plus 组件，保持视觉一致性。
- **公式处理**: 涉及 LaTeX 内容必须通过 `MathText` 组件渲染。
- **图片处理**: 使用 `getImageUrl` 处理后端静态资源路径。

## ANTI-PATTERNS

- ❌ **样式硬编码**: 禁止在组件内写大量行内样式，优先使用原子化 CSS 或 Scoped CSS。
- ❌ **直接操纵 DOM**: 禁止使用原生 DOM API (应使用 Vue `ref`)。
- ❌ **过度封装**: 避免将不相关的逻辑强行塞入单个组件 (应拆分为子组件)。
- ❌ **忽略容错**: 禁止在渲染题目内容时不处理 `null` 或 `undefined`。
