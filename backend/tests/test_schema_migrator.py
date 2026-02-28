"""
测试SchemaMigrator类

测试Schema版本迁移工具类的核心功能
"""

import pytest
from datetime import datetime
from backend.app.utils.schema_migrator import SchemaMigrator, create_default_migrator


class TestSchemaMigrator:
    """测试SchemaMigrator类"""
    
    def test_register_migration(self):
        """测试注册迁移规则"""
        migrator = SchemaMigrator()
        
        # 注册v1.0到v2.0的迁移
        migrator.register_migration(
            from_version="1.0",
            to_version="2.0",
            rules={
                "difficulty": "difficulty",
                "topics": "topics"
            }
        )
        
        # 验证迁移规则已注册
        assert "1.0→2.0" in migrator.migration_rules
        assert migrator.migration_rules["1.0→2.0"]["from_version"] == "1.0"
        assert migrator.migration_rules["1.0→2.0"]["to_version"] == "2.0"
    
    def test_migrate_simple_mapping(self):
        """测试简单字段映射迁移"""
        migrator = SchemaMigrator()
        
        migrator.register_migration(
            from_version="1.0",
            to_version="2.0",
            rules={
                "difficulty": "difficulty",
                "topics": "topics",
                "grade": "grade"
            }
        )
        
        # 执行迁移
        old_data = {
            "difficulty": "中等",
            "topics": ["二次函数"],
            "grade": 9
        }
        
        new_data = migrator.migrate(old_data, "1.0", "2.0")
        
        # 验证迁移结果
        assert new_data["difficulty"] == "中等"
        assert new_data["topics"] == ["二次函数"]
        assert new_data["grade"] == 9
        assert "_migration_log" in new_data
        assert new_data["_migration_log"]["from_version"] == "1.0"
        assert new_data["_migration_log"]["to_version"] == "2.0"
    
    def test_migrate_with_default_value(self):
        """测试带默认值的迁移"""
        migrator = SchemaMigrator()
        
        migrator.register_migration(
            from_version="1.0",
            to_version="2.0",
            rules={
                "difficulty": "difficulty",
                "category": {
                    "from": None,
                    "default": "常考题"
                }
            }
        )
        
        old_data = {
            "difficulty": "中等"
            # 注意：没有category字段
        }
        
        new_data = migrator.migrate(old_data, "1.0", "2.0")
        
        assert new_data["difficulty"] == "中等"
        assert new_data["category"] == "常考题"  # 使用默认值
    
    def test_migrate_with_transform(self):
        """测试带转换函数的迁移"""
        migrator = SchemaMigrator()
        
        migrator.register_migration(
            from_version="1.0",
            to_version="2.0",
            rules={
                "difficulty": "difficulty",
                "score": {
                    "from": "points",
                    "transform": lambda x: x * 10 if x else 0
                }
            }
        )
        
        old_data = {
            "difficulty": "中等",
            "points": 5
        }
        
        new_data = migrator.migrate(old_data, "1.0", "2.0")
        
        assert new_data["difficulty"] == "中等"
        assert new_data["score"] == 50  # 5 * 10
    
    def test_migrate_with_transformer(self):
        """测试使用转换器的迁移"""
        migrator = SchemaMigrator()
        
        migrator.register_migration(
            from_version="1.0",
            to_version="2.0",
            rules={
                "difficulty": "difficulty"
            },
            transformers={
                "difficulty": lambda v: v.upper() if v else v
            }
        )
        
        old_data = {
            "difficulty": "medium"
        }
        
        new_data = migrator.migrate(old_data, "1.0", "2.0")
        
        assert new_data["difficulty"] == "MEDIUM"  # 转换为大写
    
    def test_get_migration_path(self):
        """测试获取迁移路径"""
        migrator = SchemaMigrator()
        
        migrator.register_migration("1.0", "2.0", {})
        migrator.register_migration("2.0", "3.0", {})
        migrator.register_migration("3.0", "4.0", {})
        
        path = migrator.get_migration_path("1.0", "4.0")
        
        assert len(path) == 3
        assert path[0] == "1.0→2.0"
        assert path[1] == "2.0→3.0"
        assert path[2] == "3.0→4.0"
    
    def test_get_migration_path_not_found(self):
        """测试获取不存在的迁移路径"""
        migrator = SchemaMigrator()
        
        with pytest.raises(ValueError) as exc_info:
            migrator.get_migration_path("1.0", "2.0")
        
        assert "无法找到从 1.0 到 2.0 的迁移路径" in str(exc_info.value)
    
    def test_migrate_version_not_found(self):
        """测试迁移到不存在的版本"""
        migrator = SchemaMigrator()
        
        with pytest.raises(ValueError) as exc_info:
            migrator.migrate({}, "1.0", "2.0")
        
        assert "未找到从 1.0 到 2.0 的迁移规则" in str(exc_info.value)


class TestDefaultMigrator:
    """测试默认迁移器"""
    
    def test_create_default_migrator(self):
        """测试创建默认迁移器"""
        migrator = create_default_migrator()
        
        # 验证预定义的迁移规则已注册
        assert "1.0→2.0" in migrator.migration_rules
        assert "2.0→3.0" in migrator.migration_rules
    
    def test_v1_to_v2_migration(self):
        """测试v1.0到v2.0的迁移"""
        migrator = create_default_migrator()
        
        old_data = {
            "difficulty": "简单",
            "topics": ["二次函数"],
            "grade": 9
        }
        
        new_data = migrator.migrate(old_data, "1.0", "2.0")
        
        # 验证旧字段已映射
        assert new_data["difficulty"] == "容易"  # v1的"简单"映射到v2的"容易"
        assert new_data["topics"] == ["二次函数"]
        assert new_data["grade"] == 9
        
        # 验证新增字段有默认值
        assert new_data["category"] == "常考题"
        assert new_data["core_competencies"] == ["数学抽象", "逻辑推理"]
    
    def test_v2_to_v3_migration(self):
        """测试v2.0到v3.0的迁移"""
        migrator = create_default_migrator()
        
        old_data = {
            "difficulty": "较难",
            "topics": ["导数"],
            "grade": 10,
            "category": "压轴题",
            "core_competencies": ["逻辑推理"]
        }
        
        new_data = migrator.migrate(old_data, "2.0", "3.0")
        
        # 验证旧字段已保留
        assert new_data["difficulty"] == "较难"
        assert new_data["topics"] == ["导数"]
        assert new_data["grade"] == 10
        assert new_data["category"] == "压轴题"
        assert new_data["core_competencies"] == ["逻辑推理"]
        
        # 验证新增字段有默认值
        assert new_data["cognitive_level"] == "理解"
        assert new_data["time_estimate"] == 5  # 分钟


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
