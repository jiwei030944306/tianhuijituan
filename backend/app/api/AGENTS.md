# Backend API 知识库 (backend/app/api)

**生成时间**: 2026-02-05 20:38
**模块范围**: 系统核心 RESTful API 路由定义

## OVERVIEW
智研题库云系统后端 API 核心层，负责处理 HTTP 请求路由、输入验证与响应格式化。

## WHERE TO LOOK
| 文件 | 描述 | 状态 |
|------|------|------|
| `questions.py` | 试题中心核心 API (592行)，包含 CRUD、批量同步、复杂筛选 | **核心/复杂** |
| `logs.py` | 审计日志与系统反馈 API，支持操作追踪与性能监控 | 活跃 |
| `__init__.py` | API 版本控制与路由挂载中心 | 静态 |

## CONVENTIONS
- **模块化路由**: 必须使用 `APIRouter` 组织代码，并由 `main.py` 统一包含。
- **强类型契约**: 所有 Endpoint 必须声明 `response_model`，并使用 Pydantic Schemas 进行数据验证。
- **逻辑分层**: 路由函数仅负责“解析-分发-返回”。禁止直接操作数据库，必须通过 `crud` 模块进行数据交互。
- **标准异常**: 业务错误应统一抛出 `fastapi.HTTPException`，并携带符合前端解析规范的 `detail` 信息。
- **依赖注入**: 数据库会话 (`get_db`) 和用户认证 (`get_current_user`) 必须通过 `Depends` 注入。

## ANTI-PATTERNS
- ❌ **胖路由 (Fat Routes)**: 在路由函数中编写复杂的业务逻辑或原始 SQL 查询。
- ❌ **动态类型**: 使用 `dict` 或 `Any` 接收/返回数据，导致 API 文档 (Swagger) 缺失类型定义。
- ❌ **忽略状态码**: 不声明 `status_code` 或统一返回 200 (即使发生业务逻辑错误)。
- ❌ **长函数**: `questions.py` 中的函数如果超过 50 行，必须考虑拆分或逻辑下沉。
- ❌ **敏感信息泄露**: 在错误日志或 `detail` 中直接返回原始数据库错误信息。
