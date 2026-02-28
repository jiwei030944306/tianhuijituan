-- ========================================
-- 智研题库云系统 - 数据库表结构
-- 文件名: schema.sql
-- 版本: v1.0
-- 日期: 2025-01-30
-- ========================================

-- 开始事务
BEGIN;

-- ========================================
-- 创建questions表（试题表）
-- ========================================
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
        'single_choice',
        'multiple_choice',
        'fill_blank',
        'calculation',
        'application'
    )),
    CONSTRAINT chk_questions_difficulty CHECK (difficulty IN (
        'easy',
        'medium',
        'hard'
    )),
    CONSTRAINT chk_questions_status CHECK (status IN (
        'draft',
        'validated',
        'tagged',
        'published'
    )),
    CONSTRAINT chk_questions_question_number CHECK (question_number > 0)
);

-- ========================================
-- 创建索引
-- ========================================

-- 普通索引
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(type);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status);
CREATE INDEX IF NOT EXISTS idx_questions_question_number ON questions(question_number);

-- 复合索引
CREATE INDEX IF NOT EXISTS idx_questions_type_difficulty ON questions(type, difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_type_status ON questions(type, status);

-- GIN索引（用于JSONB字段）
CREATE INDEX IF NOT EXISTS idx_questions_topics ON questions USING GIN(topics);
CREATE INDEX IF NOT EXISTS idx_questions_specialties ON questions USING GIN(specialties);
CREATE INDEX IF NOT EXISTS idx_questions_options ON questions USING GIN(options);

-- 全文搜索索引
CREATE INDEX IF NOT EXISTS idx_questions_stem_fts ON questions USING GIN(to_tsvector('chinese', stem));
CREATE INDEX IF NOT EXISTS idx_questions_analysis_fts ON questions USING GIN(to_tsvector('chinese', analysis));

-- ========================================
-- 添加表和字段注释
-- ========================================

COMMENT ON TABLE questions IS '试题表 - 存储所有试题数据';
COMMENT ON COLUMN questions.id IS '试题唯一ID';
COMMENT ON COLUMN questions.question_number IS '题目序号';
COMMENT ON COLUMN questions.type IS '题型：single_choice(单选), multiple_choice(多选), fill_blank(填空), calculation(计算), application(应用)';
COMMENT ON COLUMN questions.difficulty IS '难度：easy(简单), medium(中等), hard(困难)';
COMMENT ON COLUMN questions.stem IS '题干内容（支持LaTeX公式）';
COMMENT ON COLUMN questions.options IS '选项（JSON数组，单选题和多选题专用）';
COMMENT ON COLUMN questions.stem_images IS '题干图片（JSON数组）';
COMMENT ON COLUMN questions.topics IS '知识点（JSON数组）';
COMMENT ON COLUMN questions.specialties IS '能力维度（JSON数组）';
COMMENT ON COLUMN questions.answer IS '答案';
COMMENT ON COLUMN questions.analysis IS '解析（支持LaTeX公式）';
COMMENT ON COLUMN questions.comment IS '备注';
COMMENT ON COLUMN questions.status IS '状态：draft(草稿), validated(已校验), tagged(已标化), published(已发布)';
COMMENT ON COLUMN questions.created_at IS '创建时间';
COMMENT ON COLUMN questions.updated_at IS '更新时间';

-- ========================================
-- 创建更新时间触发器函数
-- ========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 为questions表创建触发器
-- ========================================
DROP TRIGGER IF EXISTS trigger_questions_updated_at ON questions;
CREATE TRIGGER trigger_questions_updated_at
    BEFORE UPDATE ON questions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 提交事务
COMMIT;

-- ========================================
-- 验证脚本
-- ========================================

-- 查看表结构
\d questions

-- 查看索引
SELECT indexname, tablename, indexdef
FROM pg_indexes
WHERE tablename = 'questions'
ORDER BY indexname;

-- 查看约束
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'questions'::regclass;

-- 查看触发器
SELECT trigger_name, event_manipulation, event_object_table
FROM information_schema.triggers
WHERE event_object_table = 'questions';