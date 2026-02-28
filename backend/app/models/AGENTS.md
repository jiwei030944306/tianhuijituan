# 数据库模型规范 (backend/app/models)

**生成时间**: 2026-02-05 20:55
**状态**: 核心模型定义层

## OVERVIEW
本目录定义 SQLAlchemy ORM 模型，作为 Python 对象与 PostgreSQL 数据库表之间的映射核心。

## WHERE TO LOOK

| 模型名称 | 文件路径 | 说明 |
|----------|----------|------|
| `Question` | `question.py` | 核心试题模型，包含题干、选项（JSONB）、知识点（ARRAY） |
| `UploadRecord` | `upload_record.py` | 记录上传历史、文件路径及处理状态 |
| `Base` | `base.py` | 所有模型的基类（通常包含 `id` 和时间戳等通用字段） |

## CONVENTIONS

### 1. 字段定义
- **命名**: 使用 `snake_case`（如 `is_active`）。布尔值必须带 `is_` 前缀。
- **类型**:
  - 主键 ID 统一使用 `String(100)` 以支持 UUID 或自定义业务 ID。
  - 复杂结构（如试题选项、元数据）必须使用 `JSONB` 类型以利用 Postgres 索引。
  - 时间戳：所有模型必须包含 `created_at` 和 `updated_at`，并使用带时区的 `DateTime(timezone=True)`。

### 2. 索引与约束
- **索引**: 凡是用于 `WHERE` 或 `ORDER BY` 的字段（如 `type`, `difficulty`）必须显式定义索引。
- **约束**:
  - 状态枚举值需配合 `CheckConstraint` 确保数据库层的数据完整性。
  - 唯一索引统一使用 `uk_表名_字段名` 格式命名。

### 3. 关系定义
- **双向关系**: 必须使用 `relationship` 配合 `back_populates`（而非 `backref`）以增强类型提示。
- **级联删除**: 在定义 `ForeignKey` 时必须明确 `ondelete="CASCADE"` 并在 `relationship` 中声明 `cascade="all, delete-orphan"`。

## ANTI-PATTERNS

- ❌ **在模型中编写业务逻辑**: 禁止在模型类中定义复杂的计算函数，相关逻辑应下沉至 `crud/` 层。
- ❌ **循环引用**: 禁止在模型文件头交叉导入其他模型。应使用字符串形式定义关系（如 `relationship("Question", ...)`）。
- ❌ **缺少 Index**: 禁止忽略外键字段的索引定义，这会导致大规模 JOIN 查询性能崩溃。
- ❌ **裸返回**: 禁止将 ORM 模型对象直接暴露给前端，必须经过 `schemas/` 进行数据脱敏与验证。