# 智研题库云系统 - 后端核心 (app)

**OVERVIEW**: 基于 FastAPI 的后端核心模块，负责业务逻辑处理、API 路由分发及数据库交互。

## STRUCTURE

- `api/`: RESTful 路由定义，使用 `APIRouter` 进行模块化拆分
- `crud/`: 封装数据库增删改查（CRUD）逻辑，解耦业务与路由
- `models/`: SQLAlchemy ORM 模型定义，映射数据库表结构
- `schemas/`: Pydantic 数据验证模型，负责请求输入验证与响应输出过滤
- `core/`: 全局核心配置、数据库引擎初始化及认证逻辑
- `utils/`: 跨模块通用的辅助工具函数（如文件处理、时间格式化）

## WHERE TO LOOK

- `main.py`: FastAPI 应用入口，挂载路由与中间件
- `api/questions.py`: 试题核心 API (592行)，包含搜索、自检及同步逻辑
- `crud/question.py`: 试题相关的数据库操作封装
- `models/question.py`: 试题 ORM 模型定义
- `core/database.py`: 数据库 Session 管理与依赖项

## CONVENTIONS

- **职责分离**: 路由 (`api/`) 只负责参数接收与结果返回，业务逻辑下沉到 `crud/`
- **命名规范**: 变量与函数统一使用 `snake_case`
- **类型提示**: 所有函数必须标注 Python Type Hints
- **依赖注入**: 数据库连接 (`db: Session`) 统一通过 FastAPI `Depends` 注入
- **模型同步**: 保持 `models/` 与 `schemas/` 字段同步，利用 `from_attributes=True` 进行转换

## ANTI-PATTERNS

- ❌ 在 `api/` 路由函数中直接编写复杂的 SQLAlchemy 查询语句
- ❌ 在 API 响应中直接返回 ORM 对象（应使用 `schemas/` 进行序列化）
- ❌ 模块间循环引用（通常是 `crud` 与 `schemas` 之间的耦合）
- ❌ 忽略异常处理，导致数据库 Session 未能正确关闭
