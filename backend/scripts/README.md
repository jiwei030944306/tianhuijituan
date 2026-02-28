# 第1步：JSON数据导入PostgreSQL - 使用说明

## 概述

本步骤将JSON格式的试题数据导入PostgreSQL数据库，建立智研题库云系统的基础数据层。

## 前置条件

### 1. 安装PostgreSQL

**Windows**:
- 下载并安装PostgreSQL 15+: https://www.postgresql.org/download/windows/
- 安装时记住设置的密码（默认用户：postgres）

**验证安装**:
```bash
psql --version
```

### 2. 创建数据库

```bash
# 使用psql连接到PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE question_bank;

# 退出
\q
```

### 3. 安装Python依赖

```bash
pip install psycopg2-binary
```

### 4. 配置数据库连接

编辑 `backend/scripts/import_questions.py` 和 `backend/scripts/test_import.py`，修改数据库配置：

```python
DB_CONFIG = {
    "dbname": "question_bank",
    "user": "postgres",
    "password": "你的密码",  # 修改这里
    "host": "localhost",
    "port": "5432"
}
```

## 执行步骤

### 步骤1：创建表结构

```bash
# 方式1：使用psql执行SQL文件
psql -U postgres -d question_bank -f backend/scripts/schema.sql

# 方式2：让导入脚本自动创建（推荐）
# 导入脚本会自动创建表结构
```

### 步骤2：导入数据

```bash
cd backend/scripts
python import_questions.py
```

**预期输出**:
```
============================================================
智研题库云系统 - JSON试题数据导入
============================================================

[1/5] 读取JSON文件...
✅ 成功读取 26 道题目

[2/5] 验证数据...
✅ 数据验证通过

[3/5] 连接数据库...
✅ 数据库连接成功

[4/5] 创建表结构...
✅ 表结构创建成功
✅ 索引创建成功

[5/5] 导入数据...
  已导入 10/26 条数据
  已导入 20/26 条数据
✅ 数据导入完成
  成功: 26 条
  失败: 0 条

============================================================
导入完成!
============================================================
总计: 26 道题目
成功: 26 道
失败: 0 道

✅ 所有题目导入成功!
```

### 步骤3：运行测试

```bash
python test_import.py
```

**预期输出**:
```
============================================================
智研题库云系统 - JSON导入自动化测试
============================================================
开始时间: 2025-01-30 23:45:00

前置条件测试
------------------------------------------------------------
✅ 测试1: 数据库连接成功
✅ 测试2: JSON文件存在
✅ 测试3: JSON格式正确，包含 26 道题目
✅ 测试4: 所有必填字段完整
✅ 测试5: 所有题型有效
✅ 测试6: 所有难度有效

导入后验证测试
------------------------------------------------------------
✅ 测试7: 导入数量正确 (26 道)
✅ 测试8: 所有ID唯一
✅ 测试9: 题型分布:
    single_choice: 16 道
    fill_blank: 3 道
    calculation: 5 道
    application: 2 道
✅ 测试10: 难度分布:
    easy: 12 道
    medium: 10 道
    hard: 4 道
✅ 测试11: JSONB字段验证通过
✅ 测试12: 索引创建成功 (11 个索引)
✅ 测试13: 按题型查询成功 (返回 5 条)
✅ 测试14: 按难度查询成功 (返回 10 条)
✅ 测试15: JSONB查询成功 (按知识点 '函数' 查询到 3 条)
✅ 测试16: 全文搜索成功 (搜索'函数'，返回 5 条)

============================================================
测试总结
============================================================
总测试数: 16
通过: 16
失败: 0
通过率: 100.0%

结束时间: 2025-01-30 23:45:05
```

## 手动验证

### 1. 查看表结构

```bash
psql -U postgres -d question_bank -c "\d questions"
```

### 2. 查看索引

```bash
psql -U postgres -d question_bank -c "SELECT indexname, tablename FROM pg_indexes WHERE tablename = 'questions' ORDER BY indexname;"
```

### 3. 查看数据

```bash
# 查看所有题目数量
psql -U postgres -d question_bank -c "SELECT COUNT(*) FROM questions;"

# 查看前5道题目
psql -U postgres -d question_bank -c "SELECT id, type, difficulty, stem FROM questions LIMIT 5;"

# 按题型统计
psql -U postgres -d question_bank -c "SELECT type, COUNT(*) FROM questions GROUP BY type;"

# 按难度统计
psql -U postgres -d question_bank -c "SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty;"
```

## 常见问题

### Q1: 提示"数据库连接失败"

**A**: 检查以下几点：
1. PostgreSQL服务是否运行
2. 用户名和密码是否正确
3. 数据库是否已创建：`CREATE DATABASE question_bank;`

### Q2: 提示"psycopg2安装失败"

**A**: 尝试以下方法：
```bash
pip install psycopg2-binary
```

如果仍然失败，可能需要安装C编译工具。

### Q3: JSON文件路径错误

**A**: 确认JSON文件路径是否正确，Windows路径使用原始字符串或双反斜杠：
```python
JSON_FILE_PATH = r"D:\newAI\天卉题云智研\测试数据\1\__主题__：..."
```

### Q4: 导入数据时提示"表已存在"

**A**: 这是正常的，脚本会使用UPSERT操作，不会产生重复数据。如果需要清空数据重新导入，可以在脚本中调用 `clear_existing_data()` 函数。

### Q5: 测试失败

**A**: 检查测试失败的详细信息：
1. 确认数据已成功导入
2. 确认表结构和索引已创建
3. 检查JSON文件格式是否正确

## 文件说明

| 文件 | 说明 |
|------|------|
| `schema.sql` | 数据库表结构和索引SQL |
| `import_questions.py` | 数据导入脚本 |
| `test_import.py` | 自动化测试脚本 |
| `README.md` | 本说明文档 |

## 下一步

数据导入成功后，可以继续：
- 第2步：搭建FastAPI基础框架
- 第3步：搭建Vue前端基础框架

## 技术支持

如遇到问题，请检查：
1. PostgreSQL日志
2. Python错误堆栈
3. JSON文件格式

---

**文档版本**: v1.0
**创建日期**: 2025-01-30
**作者**: AI Assistant