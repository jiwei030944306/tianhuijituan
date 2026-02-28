#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智研题库云系统 - JSON导入PostgreSQL自动化测试脚本
文件名: test_import.py
版本: v1.0
日期: 2025-01-30
"""

import json
import psycopg2
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import sys

# ========================================
# 配置部分
# ========================================

# 数据库配置
# 安全修复：从环境变量读取敏感信息
import os

DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "question_bank"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),  # 必须通过环境变量配置
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

# JSON文件路径
JSON_FILE_PATH = r"D:\newAI\天卉题云智研\测试数据\1\__主题__：文茂天卉中学_2023_-_2024_学年第一学期阶段二学情反馈试题中关于有理数、整式、方程等的单项选择题解析及答案.json"

# ========================================
# 全局变量
# ========================================

conn = None
questions = None
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

# ========================================
# 数据库连接
# ========================================

def connect_db():
    """连接数据库"""
    global conn
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return True
    except Exception as e:
        return False


def close_db():
    """关闭数据库连接"""
    global conn
    if conn:
        conn.close()


# ========================================
# 测试函数
# ========================================

def test_db_connection():
    """测试1: 数据库连接"""
    try:
        if connect_db():
            print("✅ 测试1: 数据库连接成功")
            close_db()
            return True
        else:
            raise Exception("数据库连接失败")
    except Exception as e:
        print(f"❌ 测试1: 数据库连接失败 - {e}")
        return False


def test_json_file_exists():
    """测试2: JSON文件是否存在"""
    try:
        json_path = Path(JSON_FILE_PATH)
        assert json_path.exists(), f"JSON文件不存在: {JSON_FILE_PATH}"
        print("✅ 测试2: JSON文件存在")
        return True
    except Exception as e:
        print(f"❌ 测试2: JSON文件不存在 - {e}")
        return False


def test_json_format():
    """测试3: JSON格式验证"""
    global questions
    try:
        json_path = Path(JSON_FILE_PATH)
        with open(json_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)

        assert isinstance(questions, list), "JSON应该是数组"
        assert len(questions) > 0, "JSON数组不能为空"
        print(f"✅ 测试3: JSON格式正确，包含 {len(questions)} 道题目")
        return True
    except Exception as e:
        print(f"❌ 测试3: JSON格式错误 - {e}")
        return False


def test_required_fields():
    """测试4: 必填字段完整性检查"""
    try:
        required_fields = ["id", "questionNumber", "type", "difficulty", "stem", "answer"]
        missing_fields = []

        for i, q in enumerate(questions):
            for field in required_fields:
                if field not in q or q[field] is None or q[field] == "":
                    missing_fields.append(f"题目{i+1}（ID: {q.get('id', 'unknown')}）缺少字段: {field}")

        assert len(missing_fields) == 0, f"发现缺失字段: {', '.join(missing_fields[:5])}..."
        print("✅ 测试4: 所有必填字段完整")
        return True
    except Exception as e:
        print(f"❌ 测试4: 必填字段检查失败 - {e}")
        return False


def test_valid_types():
    """测试5: 题型枚举值验证"""
    try:
        valid_types = ["single_choice", "multiple_choice", "fill_blank", "calculation", "application"]
        invalid_types = []

        for i, q in enumerate(questions):
            if q.get("type") not in valid_types:
                invalid_types.append(f"题目{i+1}（ID: {q.get('id', 'unknown')}）: {q.get('type')}")

        assert len(invalid_types) == 0, f"发现无效题型: {', '.join(invalid_types[:5])}..."
        print("✅ 测试5: 所有题型有效")
        return True
    except Exception as e:
        print(f"❌ 测试5: 题型验证失败 - {e}")
        return False


def test_valid_difficulties():
    """测试6: 难度枚举值验证"""
    try:
        valid_difficulties = ["easy", "medium_easy", "medium", "medium_hard", "hard"]
        invalid_difficulties = []

        for i, q in enumerate(questions):
            if q.get("difficulty") not in valid_difficulties:
                invalid_difficulties.append(f"题目{i+1}（ID: {q.get('id', 'unknown')}）: {q.get('difficulty')}")

        assert len(invalid_difficulties) == 0, f"发现无效难度: {', '.join(invalid_difficulties[:5])}..."
        print("✅ 测试6: 所有难度有效")
        return True
    except Exception as e:
        print(f"❌ 测试6: 难度验证失败 - {e}")
        return False


def test_import_count():
    """测试7: 导入数量验证"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM questions")
            count = cursor.fetchone()[0]

        assert count == len(questions), f"导入数量不匹配: 预期 {len(questions)}，实际 {count}"
        print(f"✅ 测试7: 导入数量正确 ({count} 道)")
        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试7: 导入数量验证失败 - {e}")
        close_db()
        return False


def test_id_uniqueness():
    """测试8: ID唯一性验证"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, COUNT(*) as count
                FROM questions
                GROUP BY id
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()

        assert len(duplicates) == 0, f"发现重复ID: {[d[0] for d in duplicates]}"
        print("✅ 测试8: 所有ID唯一")
        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试8: ID唯一性验证失败 - {e}")
        close_db()
        return False


def test_type_distribution():
    """测试9: 题型分布验证"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT type, COUNT(*) as count
                FROM questions
                GROUP BY type
                ORDER BY type
            """)
            distribution = cursor.fetchall()

        print(f"✅ 测试9: 题型分布:")
        for type_name, count in distribution:
            print(f"    {type_name}: {count} 道")

        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试9: 题型分布验证失败 - {e}")
        close_db()
        return False


def test_difficulty_distribution():
    """测试10: 难度分布验证"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT difficulty, COUNT(*) as count
                FROM questions
                GROUP BY difficulty
                ORDER BY difficulty
            """)
            distribution = cursor.fetchall()

        print(f"✅ 测试10: 难度分布:")
        for difficulty, count in distribution:
            print(f"    {difficulty}: {count} 道")

        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试10: 难度分布验证失败 - {e}")
        close_db()
        return False


def test_jsonb_fields():
    """测试11: JSONB字段验证"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, question_number, options
                FROM questions
                WHERE type = 'single_choice'
                LIMIT 1
            """)
            result = cursor.fetchone()

        assert result is not None, "没有找到单选题"
        assert result[2] is not None, "单选题的options字段不能为空"

        # 验证options是有效的JSON
        options = json.loads(result[2])
        assert isinstance(options, list), "options应该是数组"

        print(f"✅ 测试11: JSONB字段验证通过")
        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试11: JSONB字段验证失败 - {e}")
        close_db()
        return False


def test_index_creation():
    """测试12: 索引创建验证"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT indexname, tablename
                FROM pg_indexes
                WHERE tablename = 'questions'
                ORDER BY indexname
            """)
            indexes = cursor.fetchall()

        expected_indexes = [
            'idx_questions_type',
            'idx_questions_difficulty',
            'idx_questions_status',
            'idx_questions_question_number',
            'idx_questions_type_difficulty',
            'idx_questions_type_status',
            'idx_questions_topics',
            'idx_questions_specialties',
            'idx_questions_options',
            'idx_questions_stem_fts',
            'idx_questions_analysis_fts'
        ]

        actual_indexes = [idx[0] for idx in indexes]
        missing_indexes = set(expected_indexes) - set(actual_indexes)

        assert len(missing_indexes) == 0, f"缺少索引: {', '.join(missing_indexes)}"

        print(f"✅ 测试12: 索引创建成功 ({len(indexes)} 个索引)")
        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试12: 索引创建验证失败 - {e}")
        close_db()
        return False


def test_query_by_type():
    """测试13: 按题型查询"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, question_number, stem, answer
                FROM questions
                WHERE type = 'single_choice'
                LIMIT 5
            """)
            results = cursor.fetchall()

        assert len(results) > 0, "没有查询到单选题"
        print(f"✅ 测试13: 按题型查询成功 (返回 {len(results)} 条)")
        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试13: 按题型查询失败 - {e}")
        close_db()
        return False


def test_query_by_difficulty():
    """测试14: 按难度查询"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, question_number, stem, difficulty
                FROM questions
                WHERE difficulty = 'medium'
            """)
            results = cursor.fetchall()

        assert len(results) > 0, "没有查询到中等难度题目"
        print(f"✅ 测试14: 按难度查询成功 (返回 {len(results)} 条)")
        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试14: 按难度查询失败 - {e}")
        close_db()
        return False


def test_json_query():
    """测试15: JSONB查询（按知识点）"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            # 查询包含特定知识点的题目
            cursor.execute("""
                SELECT id, question_number, topics
                FROM questions
                WHERE topics IS NOT NULL
                LIMIT 1
            """)
            result = cursor.fetchone()

        if result and result[2]:
            topics = result[2]
            if isinstance(topics, list) and len(topics) > 0:
                topic = topics[0]
                cursor.execute("""
                    SELECT id, question_number, topics
                    FROM questions
                    WHERE topics @> %s::jsonb
                    LIMIT 5
                """, (json.dumps([topic]),))
                results = cursor.fetchall()

                print(f"✅ 测试15: JSONB查询成功 (按知识点 '{topic}' 查询到 {len(results)} 条)")
            else:
                print("✅ 测试15: JSONB查询成功 (没有知识点数据)")
        else:
            print("✅ 测试15: JSONB查询成功 (没有知识点数据)")

        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试15: JSONB查询失败 - {e}")
        close_db()
        return False


def test_fulltext_search():
    """测试16: 全文搜索测试"""
    try:
        connect_db()
        with conn.cursor() as cursor:
            # 搜索题干中包含"函数"的题目
            cursor.execute("""
                SELECT id, question_number, stem
                FROM questions
                WHERE to_tsvector('chinese', stem) @@ to_tsquery('chinese', '函数')
                LIMIT 5
            """)
            results = cursor.fetchall()

        print(f"✅ 测试16: 全文搜索成功 (搜索'函数'，返回 {len(results)} 条)")
        close_db()
        return True
    except Exception as e:
        print(f"❌ 测试16: 全文搜索失败 - {e}")
        close_db()
        return False


# ========================================
# 主程序
# ========================================

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("智研题库云系统 - JSON导入自动化测试")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 定义测试组
    test_groups = [
        ("前置条件测试", [
            test_db_connection,
            test_json_file_exists,
            test_json_format,
            test_required_fields,
            test_valid_types,
            test_valid_difficulties
        ]),
        ("导入后验证测试", [
            test_import_count,
            test_id_uniqueness,
            test_type_distribution,
            test_difficulty_distribution,
            test_jsonb_fields,
            test_index_creation,
            test_query_by_type,
            test_query_by_difficulty,
            test_json_query,
            test_fulltext_search
        ])
    ]

    # 运行所有测试
    for group_name, test_funcs in test_groups:
        print(f"\n{group_name}")
        print("-" * 60)
        for test_func in test_funcs:
            test_results["total"] += 1
            try:
                if test_func():
                    test_results["passed"] += 1
                else:
                    test_results["failed"] += 1
                    test_results["errors"].append(f"{test_func.__name__}")
            except Exception as e:
                test_results["failed"] += 1
                test_results["errors"].append(f"{test_func.__name__}: {str(e)}")
                print(f"❌ {test_func.__name__}: {e}")

    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {test_results['total']}")
    print(f"通过: {test_results['passed']}")
    print(f"失败: {test_results['failed']}")
    print(f"通过率: {test_results['passed'] / test_results['total'] * 100:.1f}%")

    if test_results["failed"] > 0:
        print(f"\n失败的测试:")
        for error in test_results["errors"]:
            print(f"  - {error}")

    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 返回测试结果
    return test_results["failed"] == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)