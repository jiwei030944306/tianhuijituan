# 智研题库云系统 - Schemas 知识库

**OVERVIEW**: 基于 Pydantic 的数据验证与序列化层，负责 API 的输入校验与响应格式化。

## WHERE TO LOOK

- `question.py`: 核心试题模型 (103行)，包含试题的创建、更新、统计及冲突检测 Schema。
- `upload.py`: 上传记录模型 (约55行)，定义上传任务的状态跟踪与响应结构。

## CONVENTIONS

- **分层继承**:
  - `Base`: 定义通用字段与类型。
  - `Create`: 继承 `Base`，通常不包含 `id` 和时间戳字段。
  - `Update`: 独立定义，所有字段设为 `Optional` 以支持部分更新。
  - `Response`: 继承 `Base`，包含 `id`、时间戳，并配置 `from_attributes = True`。
- **字段规范**:
  - 必须使用 `Field(..., description="...")` 标注所有字段含义。
  - 严格使用 `typing` 模块的类型提示（如 `List`, `Optional`, `Dict`）。
  - 对 JSONB 等复杂字段，在 `Response` 模型中使用 `@field_validator(mode='before')` 自动解析字符串。
- **序列化**:
  - 时间戳统一使用 `@field_serializer` 转换为 ISO 8601 格式字符串。
  - 使用 `from_attributes = True` 实现 SQLAlchemy ORM 对象的自动转换。

## ANTI-PATTERNS

- ❌ **泄漏敏感信息**: 在 `Response` 模型中包含内部 ID、原始路径或调试信息。
- ❌ **逻辑堆砌**: 在 Schema 中编写复杂的业务逻辑（应保留在 `crud/` 或 `api/`）。
- ❌ **直接返回 ORM**: API 路由未指定 `response_model`，导致数据库模型直接暴露。
- ❌ **忽略可选性**: 在 `Update` 模型中将字段设为必填，导致前端无法进行增量更新。
- ❌ **类型不一致**: Schema 字段类型与数据库 `models/` 字段类型不匹配，导致转换失败。
