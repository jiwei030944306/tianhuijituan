# 数据库Schema演进方案

## 1. 方案概述

本方案解决数据库Schema演进的核心问题：
- 固定标签字段需要变更
- 支持书籍库升级
- 支持属性版本控制

## 2. 三层架构设计

### 2.1 核心稳定层（Core Layer）
- 表：`questions`
- 字段：题目的本质定义，永不改变
- 字段：id, stem, answer, type, created_at, options, stem_images

### 2.2 扩展属性层（Extension Layer）
- 表：`question_attributes`
- 功能：存储题目的扩展属性，支持版本控制
- 核心字段：
  - schema_version: 属性集版本
  - schema_name: 属性集名称（basic, advanced, ai_enhanced）
  - attribute_data: JSONB存储所有扩展属性
  - is_active: 是否生效
  - valid_from/valid_until: 有效期

### 2.3 外部系统层（External Layer）
- 表：`book_libraries`, `question_book_refs`
- 功能：书籍库独立版本管理
- 表：`knowledge_graphs`, `question_knowledge_nodes`
- 功能：知识图谱独立演进

## 3. 核心表结构

### 3.1 questions 表（改造后）
```sql
CREATE TABLE questions (
    id VARCHAR(100) PRIMARY KEY,
    -- 核心内容
    stem TEXT NOT NULL,
    answer TEXT NOT NULL,
    type VARCHAR(20) NOT NULL,
    options JSONB,  -- 选项JSON
    stem_images JSONB,  -- 图片JSON
    -- 状态
    status VARCHAR(20) DEFAULT 'draft',
    -- 版本控制
    version INTEGER DEFAULT 1,
    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- 软删除
    deleted_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

### 3.2 question_attributes 表（新增）
```sql
CREATE TABLE question_attributes (
    id SERIAL PRIMARY KEY,
    question_id VARCHAR(100) NOT NULL REFERENCES questions(id),
    -- 版本控制
    schema_version VARCHAR(10) NOT NULL,
    schema_name VARCHAR(50) NOT NULL,
    -- 属性数据（JSONB）
    attribute_data JSONB NOT NULL,
    -- 有效性控制
    is_active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,
    -- 迁移记录
    migration_notes TEXT,
    -- 创建信息
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),
    
    -- 约束
    UNIQUE(question_id, schema_version)
);

-- JSONB索引
CREATE INDEX idx_qa_attr_gin ON question_attributes USING GIN(attribute_data);
-- 常用字段索引
CREATE INDEX idx_qa_attr_difficulty ON question_attributes((attribute_data->>'difficulty'));
CREATE INDEX idx_qa_attr_grade ON question_attributes((attribute_data->>'grade'));
```

### 3.3 book_libraries 表（新增）
```sql
CREATE TABLE book_libraries (
    id SERIAL PRIMARY KEY,
    library_version VARCHAR(20) NOT NULL UNIQUE,
    library_name VARCHAR(100) NOT NULL,
    publisher VARCHAR(100),
    effective_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    -- 版本元数据
    schema_definition JSONB,
    migration_script TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.4 question_book_refs 表（新增）
```sql
CREATE TABLE question_book_refs (
    id SERIAL PRIMARY KEY,
    question_id VARCHAR(100) NOT NULL REFERENCES questions(id),
    book_library_version VARCHAR(20) NOT NULL,
    -- 具体引用信息
    book_name VARCHAR(100),
    grade INTEGER,
    semester VARCHAR(10),
    unit VARCHAR(50),
    page INTEGER,
    question_number INTEGER,
    -- 附加元数据
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(question_id, book_library_version)
);
```

## 4. 核心代码实现

### 4.1 扩展属性 CRUD
```python
# backend/app/crud/question_attribute.py
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.question_attribute import QuestionAttribute
from app.schemas.question_attribute import QuestionAttributeCreate, QuestionAttributeUpdate

class CRUDQuestionAttribute:
    async def create(
        self, 
        db: AsyncSession, 
        obj_in: QuestionAttributeCreate
    ) -> QuestionAttribute:
        """创建扩展属性记录"""
        db_obj = QuestionAttribute(
            question_id=obj_in.question_id,
            schema_version=obj_in.schema_version,
            schema_name=obj_in.schema_name,
            attribute_data=obj_in.attribute_data,
            is_active=obj_in.is_active,
            valid_from=obj_in.valid_from,
            valid_until=obj_in.valid_until,
            created_by=obj_in.created_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_question_and_version(
        self,
        db: AsyncSession,
        question_id: str,
        schema_version: str
    ) -> Optional[QuestionAttribute]:
        """获取指定题目的特定版本属性"""
        result = await db.execute(
            select(QuestionAttribute).where(
                and_(
                    QuestionAttribute.question_id == question_id,
                    QuestionAttribute.schema_version == schema_version
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_active_by_question(
        self,
        db: AsyncSession,
        question_id: str
    ) -> Optional[QuestionAttribute]:
        """获取指定题目的当前生效属性"""
        result = await db.execute(
            select(QuestionAttribute).where(
                and_(
                    QuestionAttribute.question_id == question_id,
                    QuestionAttribute.is_active == True
                )
            ).order_by(QuestionAttribute.schema_version.desc())
        )
        return result.scalar_one_or_none()
    
    async def get_all_by_question(
        self,
        db: AsyncSession,
        question_id: str
    ) -> List[QuestionAttribute]:
        """获取指定题目的所有版本属性"""
        result = await db.execute(
            select(QuestionAttribute).where(
                QuestionAttribute.question_id == question_id
            ).order_by(QuestionAttribute.schema_version.desc())
        )
        return result.scalars().all()
    
    async def update(
        self,
        db: AsyncSession,
        db_obj: QuestionAttribute,
        obj_in: QuestionAttributeUpdate
    ) -> QuestionAttribute:
        """更新扩展属性记录"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def deactivate(
        self,
        db: AsyncSession,
        db_obj: QuestionAttribute
    ) -> QuestionAttribute:
        """停用扩展属性记录"""
        db_obj.is_active = False
        db_obj.valid_until = datetime.now()
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

# 实例化 CRUD 对象
question_attribute = CRUDQuestionAttribute()
```

### 4.2 版本迁移工具类
```python
# backend/app/utils/schema_migrator.py
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime
import json

class SchemaMigrator:
    """
    Schema版本迁移工具类
    
    用于处理题目属性的版本迁移，支持：
    - 定义迁移规则
    - 执行版本转换
    - 记录迁移日志
    """
    
    def __init__(self):
        self.migration_rules: Dict[str, Dict[str, Any]] = {}
        self.transformers: Dict[str, Callable] = {}
    
    def register_migration(
        self,
        from_version: str,
        to_version: str,
        rules: Dict[str, Any],
        transformers: Optional[Dict[str, Callable]] = None
    ):
        """
        注册一个版本迁移规则
        
        Args:
            from_version: 起始版本
            to_version: 目标版本
            rules: 字段映射规则
            transformers: 转换函数字典
        """
        migration_key = f"{from_version}→{to_version}"
        self.migration_rules[migration_key] = {
            "from_version": from_version,
            "to_version": to_version,
            "rules": rules,
            "created_at": datetime.now().isoformat()
        }
        
        if transformers:
            for field_name, transformer in transformers.items():
                transformer_key = f"{migration_key}:{field_name}"
                self.transformers[transformer_key] = transformer
    
    def migrate(
        self,
        data: Dict[str, Any],
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """
        执行数据迁移
        
        Args:
            data: 原始数据
            from_version: 起始版本
            to_version: 目标版本
            
        Returns:
            迁移后的数据
        """
        migration_key = f"{from_version}→{to_version}"
        
        if migration_key not in self.migration_rules:
            raise ValueError(f"未找到从 {from_version} 到 {to_version} 的迁移规则")
        
        rules = self.migration_rules[migration_key]["rules"]
        new_data = {}
        
        for new_key, rule in rules.items():
            if isinstance(rule, str):
                # 直接映射
                new_data[new_key] = data.get(rule)
            elif callable(rule):
                # 自定义转换函数
                new_data[new_key] = rule(data)
            elif isinstance(rule, dict):
                # 带默认值的映射
                source_key = rule.get('from')
                default = rule.get('default')
                transform = rule.get('transform')
                
                value = data.get(source_key, default)
                if transform and callable(transform):
                    value = transform(value)
                new_data[new_key] = value
            
            # 检查是否有转换器
            transformer_key = f"{migration_key}:{new_key}"
            if transformer_key in self.transformers:
                new_data[new_key] = self.transformers[transformer_key](new_data[new_key])
        
        # 添加迁移日志
        new_data["_migration_log"] = {
            "from_version": from_version,
            "to_version": to_version,
            "migrated_at": datetime.now().isoformat(),
            "migration_key": migration_key
        }
        
        return new_data
    
    def get_migration_path(
        self,
        from_version: str,
        to_version: str
    ) -> List[str]:
        """
        获取从起始版本到目标版本的迁移路径
        
        Args:
            from_version: 起始版本
            to_version: 目标版本
            
        Returns:
            迁移路径列表
        """
        # 简化实现，实际应该使用图算法找最短路径
        path = []
        current = from_version
        
        while current != to_version:
            # 找到从当前版本出发的下一个版本
            next_version = None
            for key in self.migration_rules:
                rule = self.migration_rules[key]
                if rule["from_version"] == current:
                    next_version = rule["to_version"]
                    path.append(f"{current}→{next_version}")
                    break
            
            if next_version is None:
                raise ValueError(f"无法找到从 {current} 到 {to_version} 的迁移路径")
            
            current = next_version
        
        return path


# 预定义的迁移规则

def create_default_migrator() -> SchemaMigrator:
    """创建默认的迁移器，包含预定义的迁移规则"""
    migrator = SchemaMigrator()
    
    # 定义 v1.0 到 v2.0 的迁移
    migrator.register_migration(
        from_version="1.0",
        to_version="2.0",
        rules={
            # 直接映射
            "difficulty": "difficulty",
            "topics": "topics",
            "grade": "grade",
            # 新增字段（带默认值）
            "category": {
                "from": None,
                "default": "常考题"
            },
            # 新增字段（通过转换）
            "core_competencies": {
                "from": None,
                "transform": lambda x: ["数学抽象", "逻辑推理"]
            }
        },
        transformers={
            "difficulty": lambda v: convert_difficulty_v1_to_v2(v)
        }
    )
    
    # 定义 v2.0 到 v3.0 的迁移
    migrator.register_migration(
        from_version="2.0",
        to_version="3.0",
        rules={
            "difficulty": "difficulty",
            "topics": "topics",
            "grade": "grade",
            "category": "category",
            "core_competencies": "core_competencies",
            # 新增字段
            "cognitive_level": {
                "from": None,
                "default": "理解"
            },
            "time_estimate": {
                "from": None,
                "default": 5  # 分钟
            }
        }
    )
    
    return migrator


def convert_difficulty_v1_to_v2(difficulty: str) -> str:
    """将 v1.0 的难度等级映射到 v2.0"""
    mapping = {
        "简单": "容易",
        "中等": "较易",
        "困难": "较难",
        "极难": "难"
    }
    return mapping.get(difficulty, difficulty)
```
