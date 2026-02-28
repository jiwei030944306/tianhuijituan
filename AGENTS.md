# 智研题库云系统 - 项目知识库

**生成时间**: 2026-02-20
**提交**: 331351e feat: optimize P1 check page UI and implement metadata auto-repair persistence
**分支**: feature/filter-single-row-compact

## OVERVIEW
AI驱动的试题数字化生产线，基于 FastAPI + Vue 3 + SQLite 构建的全栈应用。

### 技术栈
- **前端**: Vue 3 + TypeScript + Pinia + Element Plus + KaTeX
- **后端**: Python + FastAPI + Pydantic + SQLAlchemy (async)
- **数据库**: SQLite (aiosqlite)

## STRUCTURE
```
天卉题云智研/
├── backend/               # FastAPI 后端核心
│   ├── app/              # 应用主目录
│   │   ├── api/          # RESTful API 路由
│   │   ├── crud/         # 数据库操作层
│   │   ├── models/       # SQLAlchemy ORM 模型
│   │   ├── schemas/      # Pydantic 数据验证
│   │   ├── services/     # 业务逻辑服务层
│   │   ├── core/         # 核心配置与依赖
│   │   └── utils/        # 工具函数
│   ├── alembic/          # 数据库迁移
│   └── scripts/          # 后端脚本
├── frontend/             # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── api/          # API 服务层
│   │   ├── components/   # 可复用组件
│   │   │   ├── common/   # 公共组件
│   │   │   └── QuestionInspector/  # 试题检查组件
│   │   ├── composables/  # Vue Composition Hooks
│   │   ├── stores/       # Pinia 状态管理
│   │   ├── views/        # 页面级组件
│   │   │   ├── QuestionCheckNew/   # 试题审核（新）
│   │   │   ├── QuestionRefine/     # 试题精修
│   │   │   └── upload-management/  # 上传管理
│   │   ├── router/       # 路由配置
│   │   ├── types/        # TypeScript 类型
│   │   ├── config/       # 配置（知识点、用户等）
│   │   └── utils/        # 前端工具
│   └── tests/            # 前端测试
├── 执行手册/              # 任务计划与执行文档
├── docs/                  # 技术文档
├── scripts/               # 全局启动脚本
├── data/                  # 数据存储（上传文件、测试数据）
└── logs/                  # 应用日志
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| **启动后端** | `backend/run_server.py` 或 `backend/start.py` | Uvicorn 服务器 |
| **启动前端** | `frontend/package.json` → `npm run dev` | Vite 开发服务器 |
| **API 文档** | http://localhost:8000/docs | Swagger UI |
| **主入口** | `backend/app/main.py` | FastAPI 应用初始化 |
| **前端入口** | `frontend/src/main.ts` | Vue 应用初始化 |

## CONVENTIONS

### 后端 (Python)
- **框架**: FastAPI + SQLAlchemy + Pydantic
- **命名**: `snake_case` (变量/函数), `PascalCase` (类)
- **类型提示**: 所有函数必须标注 Type Hints
- **依赖注入**: 使用 FastAPI `Depends` 注入数据库会话
- **分层架构**: API → CRUD → Models (禁止跨层调用)

### 前端 (TypeScript/Vue)
- **框架**: Vue 3 + TypeScript + Pinia + Element Plus
- **开发模式**: 必须使用 `<script setup>` 和 Composition API
- **命名**: 组件 `PascalCase`, 变量 `camelCase`, 目录 `kebab-case`
- **类型安全**: 严格 TypeScript, 禁止 `any`
- **状态管理**: 多组件共享数据必须使用 Pinia

### 文档
- **命名规范**: `[时间]-[功能名称][类型].md`
- **三阶段**: 设计 → 测试 → 总结 (不可缺失或倒置)
- **语言**: 中文优先，技术术语保留英文

## ANTI-PATTERNS (THIS PROJECT)

### 后端
- ❌ 在 `api/` 路由中直接编写 SQLAlchemy 查询
- ❌ 在 API 响应中直接返回 ORM 对象
- ❌ 模块间循环引用 (crud ↔ schemas)
- ❌ 忽略异常处理导致 Session 泄漏

### 前端
- ❌ 在 `views` 组件中堆砌复杂业务逻辑 (应提取至 composables)
- ❌ 直接操作 DOM (应使用 Vue ref)
- ❌ 忽略 API 返回值类型定义
- ❌ 父组件直接修改子组件内部状态



## COMMANDS

```bash
# 后端
python backend/run_server.py
# 或
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm run dev

# 清理数据库（慎用，会清空所有数据）
python scripts/clear_database.py
```

## NOTES

- **数据库**: SQLite (通过 SQLAlchemy ORM + aiosqlite)
- **数据库路径**: `backend/data/question_bank.db`
- **API 文档**: http://localhost:8000/docs (Swagger UI)
- **健康检查**: `GET /health`
- **前端端口**: 5173 (开发), 3000 (备用)
- **后端端口**: 8000

