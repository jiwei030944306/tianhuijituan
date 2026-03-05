#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智研题库云系统 - JSON试题数据导入脚本
文件名: import_questions.py
版本: v1.0
日期: 2025-01-30
"""

import json
import psycopg2
from psycopg2 import sql, errors
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
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": os.environ.get("DB_PORT", "5432")
}

# JSON文件路径
JSON_FILE_PATH = r"D:\newAI\天卉题云智研\测试数据\1\__主题__：文茂天卉中学_2023_-_2024_学年第一学期阶段二学情反馈试题中关于有理数、整式、方程等的单项选择题解析及答案.json"

# 表结构SQL文件路径
SCHEMA_FILE_PATH = r"D:\newAI\天卉题云智研\backend\scripts\schema.sql"

# ========================================
# 数据库操作部分
# ========================================

def create_connection():
    """
    创建数据库连接

    Returns:
        psycopg2.extensions.connection: 数据库连接对象

    Raises:
        Exception: 连接失败时抛出异常
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        print("✅ 数据库连接成功")
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        raise


def create_table_if_not_exists(conn):
    """
    创建表结构（如果不存在）

    Args:
        conn: 数据库连接对象
    """
    try:
        schema_path = Path(SCHEMA_FILE_PATH)
        if not schema_path.exists():
            print(f"⚠️  表结构SQL文件不存在: {SCHEMA_FILE_PATH}")
            print("尝试使用内置SQL创建表...")

            # 使用内置SQL创建表
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS questions (
                        id VARCHAR(100) PRIMARY KEY,
                        question_number INTEGER NOT NULL,
                        type VARCHAR(20) NOT NULL,
                        difficulty VARCHAR(10) NOT NULL,
                        stem TEXT NOT NULL,
                        options JSONB,
                        stem_images JSONB,
                        topics JSONB,
                        specialties JSONB,
                        answer TEXT NOT NULL,
                        analysis TEXT,
                        comment TEXT,
                        status VARCHAR(20) DEFAULT 'draft',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE,
                        CONSTRAINT chk_questions_type CHECK (type IN (
                            'single_choice', 'multiple_choice', 'fill_blank',
                            'calculation', 'application'
                        )),
                        CONSTRAINT chk_questions_difficulty CHECK (difficulty IN (
                            'easy', 'medium_easy', 'medium', 'medium_hard', 'hard'
                        )),
                        CONSTRAINT chk_questions_status CHECK (status IN (
                            'draft', 'validated', 'tagged', 'published'
                        )),
                        CONSTRAINT chk_questions_question_number CHECK (question_number > 0)
                    )
                """)
                conn.commit()
        else:
            # 读取并执行SQL文件
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
                conn.commit()

        print("✅ 表结构创建成功")
    except Exception as e:
        print(f"❌ 表结构创建失败: {e}")
        conn.rollback()
        raise


def create_indexes(conn):
    """
    创建索引（如果不存在）

    Args:
        conn: 数据库连接对象
    """
    try:
        with conn.cursor() as cursor:
            # 普通索引
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(type)",
                "CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty)",
                "CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status)",
                "CREATE INDEX IF NOT EXISTS idx_questions_question_number ON questions(question_number)",
                "CREATE INDEX IF NOT EXISTS idx_questions_type_difficulty ON questions(type, difficulty)",
                "CREATE INDEX IF NOT EXISTS idx_questions_type_status ON questions(type, status)",
                # GIN索引
                "CREATE INDEX IF NOT EXISTS idx_questions_topics ON questions USING GIN(topics)",
                "CREATE INDEX IF NOT EXISTS idx_questions_specialties ON questions USING GIN(specialties)",
                "CREATE INDEX IF NOT EXISTS idx_questions_options ON questions USING GIN(options)",
                # 全文搜索索引
                "CREATE INDEX IF NOT EXISTS idx_questions_stem_fts ON questions USING GIN(to_tsvector('chinese', stem))",
                "CREATE INDEX IF NOT EXISTS idx_questions_analysis_fts ON questions USING GIN(to_tsvector('chinese', analysis))"
            ]

            for index_sql in indexes:
                cursor.execute(index_sql)

            conn.commit()
        print("✅ 索引创建成功")
    except Exception as e:
        print(f"❌ 索引创建失败: {e}")
        conn.rollback()
        raise


def clear_existing_data(conn):
    """
    清空现有数据（可选，用于重新导入）

    Args:
        conn: 数据库连接对象
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM questions")
            conn.commit()
        print("✅ 现有数据已清空")
    except Exception as e:
        print(f"❌ 清空数据失败: {e}")
        conn.rollback()
        raise


def import_questions(conn, questions: List[Dict[str, Any]]):
    """
    导入题目数据

    Args:
        conn: 数据库连接对象
        questions: 题目数据列表

    Returns:
        tuple: (成功数量, 失败数量)
    """
    success_count = 0
    failed_count = 0
    failed_ids = []

    try:
        with conn.cursor() as cursor:
            # 准备INSERT语句（使用ON CONFLICT实现UPSERT）
            insert_sql = """
                INSERT INTO questions (
                    id, question_number, type, difficulty, stem, options,
                    stem_images, topics, specialties, answer, analysis,
                    comment, status, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    question_number = EXCLUDED.question_number,
                    type = EXCLUDED.type,
                    difficulty = EXCLUDED.difficulty,
                    stem = EXCLUDED.stem,
                    options = EXCLUDED.options,
                    stem_images = EXCLUDED.stem_images,
                    topics = EXCLUDED.topics,
                    specialties = EXCLUDED.specialties,
                    answer = EXCLUDED.answer,
                    analysis = EXCLUDED.analysis,
                    comment = EXCLUDED.comment,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """

            for i, question in enumerate(questions, 1):
                try:
                    # 映射JSON字段到数据库字段
                    mapped_data = (
                        question.get('id'),
                        question.get('questionNumber'),
                        question.get('type'),
                        question.get('difficulty'),
                        question.get('stem'),
                        json.dumps(question.get('options')) if question.get('options') else None,
                        json.dumps(question.get('stemImages')) if question.get('stemImages') else None,
                        json.dumps(question.get('topics')) if question.get('topics') else None,
                        json.dumps(question.get('specialties')) if question.get('specialties') else None,
                        question.get('answer'),
                        question.get('analysis'),
                        question.get('comment'),
                        question.get('status', 'draft'),
                        datetime.now(),
                        datetime.now()
                    )

                    cursor.execute(insert_sql, mapped_data)
                    success_count += 1

                    # 每10条提交一次
                    if i % 10 == 0:
                        conn.commit()
                        print(f"  已导入 {i}/{len(questions)} 条数据")

                except Exception as e:
                    failed_count += 1
                    failed_ids.append(question.get('id', f'unknown_{i}'))
                    print(f"  ⚠️  导入失败（第{i}题）: {e}")
                    conn.rollback()  # 回滚当前事务
                    continue

            # 提交剩余的数据
            conn.commit()

        print(f"\n✅ 数据导入完成")
        print(f"  成功: {success_count} 条")
        print(f"  失败: {failed_count} 条")

        if failed_ids:
            print(f"\n失败的题目ID: {', '.join(failed_ids)}")

        return success_count, failed_count

    except Exception as e:
        print(f"❌ 数据导入失败: {e}")
        conn.rollback()
        raise


# ========================================
# 数据验证部分
# ========================================

def validate_question(question: Dict[str, Any]) -> tuple[bool, str]:
    """
    验证单个题目的数据完整性

    Args:
        question: 题目数据字典

    Returns:
        tuple: (是否有效, 错误信息)
    """
    # 必填字段检查
    required_fields = ["id", "questionNumber", "type", "difficulty", "stem", "answer"]
    for field in required_fields:
        if field not in question or question[field] is None or question[field] == "":
            return False, f"缺少必填字段: {field}"

    # 题型枚举值验证
    valid_types = ["single_choice", "multiple_choice", "fill_blank", "calculation", "application"]
    if question.get("type") not in valid_types:
        return False, f"无效的题型: {question.get('type')}"

    # 难度枚举值验证（5级：easy, medium_easy, medium, medium_hard, hard）
    valid_difficulties = ["easy", "medium_easy", "medium", "medium_hard", "hard"]
    if question.get("difficulty") not in valid_difficulties:
        return False, f"无效的难度: {question.get('difficulty')}"

    # 题号必须大于0
    if question.get("questionNumber", 0) <= 0:
        return False, f"题号必须大于0: {question.get('questionNumber')}"

    return True, ""


def validate_all_questions(questions: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
    """
    批量验证所有题目

    Args:
        questions: 题目数据列表

    Returns:
        tuple: (是否全部有效, 错误信息列表)
    """
    all_valid = True
    errors = []

    for i, question in enumerate(questions, 1):
        is_valid, error_msg = validate_question(question)
        if not is_valid:
            all_valid = False
            errors.append(f"题目{i}（ID: {question.get('id', 'unknown')}）: {error_msg}")

    return all_valid, errors


# ========================================
# 主程序
# ========================================

def main():
    """主函数"""
    print("=" * 60)
    print("智研题库云系统 - JSON试题数据导入")
    print("=" * 60)

    # 1. 读取JSON文件
    print("\n[1/5] 读取JSON文件...")
    json_path = Path(JSON_FILE_PATH)
    if not json_path.exists():
        print(f"❌ JSON文件不存在: {JSON_FILE_PATH}")
        sys.exit(1)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        print(f"✅ 成功读取 {len(questions)} 道题目")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        sys.exit(1)

    # 2. 验证数据
    print("\n[2/5] 验证数据...")
    all_valid, errors = validate_all_questions(questions)
    if not all_valid:
        print("❌ 数据验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("✅ 数据验证通过")

    # 3. 连接数据库
    print("\n[3/5] 连接数据库...")
    try:
        conn = create_connection()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n请检查:")
        print("  1. PostgreSQL服务是否运行")
        print("  2. 数据库配置是否正确")
        print("  3. 数据库是否已创建: CREATE DATABASE question_bank;")
        sys.exit(1)

    # 4. 创建表结构
    print("\n[4/5] 创建表结构...")
    try:
        create_table_if_not_exists(conn)
        create_indexes(conn)
    except Exception as e:
        print(f"❌ 表结构创建失败: {e}")
        conn.close()
        sys.exit(1)

    # 5. 导入数据
    print("\n[5/5] 导入数据...")
    try:
        success_count, failed_count = import_questions(conn, questions)
    except Exception as e:
        print(f"❌ 数据导入失败: {e}")
        conn.close()
        sys.exit(1)
    finally:
        conn.close()

    # 完成
    print("\n" + "=" * 60)
    print("导入完成!")
    print("=" * 60)
    print(f"总计: {len(questions)} 道题目")
    print(f"成功: {success_count} 道")
    print(f"失败: {failed_count} 道")

    if failed_count == 0:
        print("\n✅ 所有题目导入成功!")
    else:
        print(f"\n⚠️  有 {failed_count} 道题目导入失败，请检查日志")


if __name__ == "__main__":
    main()