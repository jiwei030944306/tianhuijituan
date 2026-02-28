# 智研题库云系统 - CRUD 知识库

**生成时间**: 2026-02-05 20:55
**作用**: 数据库持久层，封装所有数据库操作逻辑

## OVERVIEW
本目录包含 CRUD（Create, Read, Update, Delete）操作函数，作为 API 路由与数据库模型之间的桥梁。

## WHERE TO LOOK

| 模块 | 文件 | 核心职责 |
|------|------|----------|
| `question` | `question.py` (168行) | 试题的增删改查、批量查询、统计计算、冲突检测 |
| `upload` | `upload.py` (122行) | 上传记录的创建、状态更新、历史查询 |

## CONVENTIONS

### 1. 函数签名
- **命名**: `动词_名词` 格式（如 `get_question`, `create_question`, `update_question`）。
- **参数**: 第一个参数始终为 `db: Session`，后续为业务参数。
- **返回值**: 必须返回 Pydantic Schema 对象，严禁直接返回 ORM 模型。

### 2. 查询模式
- **单条查询**: 使用 `db.query(Model).filter(...).first()`，未找到返回 `None`。
- **列表查询**: 使用 `db.query(Model).filter(...).all()`，返回列表。
- **分页查询**: 使用 `.offset(skip).limit(limit)` 实现。
- **复杂查询**: 使用 `.join()`、`.options()` 进行关联查询和性能优化。

### 3. 事务处理
- **写操作**: 必须在 `try...except` 块中执行，异常时 `db.rollback()`，成功时 `db.commit()`。
- **批量操作**: 使用 `db.bulk_save_objects()` 或 `db.bulk_insert_mappings()` 提升性能。

## ANTI-PATTERNS

- ❌ **直接返回 ORM**: 禁止函数返回 SQLAlchemy 模型对象，必须转换为 Schema。
- ❌ **硬编码 SQL**: 禁止使用 `db.execute(text("..."))`，应优先使用 ORM 查询。
- ❌ **Session 泄漏**: 禁止在异常情况下未关闭或回滚 Session。
- ❌ **N+1 查询**: 禁止在循环中执行查询，应使用 `eager loading`（`joinedload`, `selectinload`）。
- ❌ **忽略权限**: 禁止在 CRUD 层忽略用户权限验证（应在 API 层或独立 Service 层处理）。