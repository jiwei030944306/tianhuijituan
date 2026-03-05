"""add duplicate fields to questions

Revision ID: 004_add_duplicate_fields
Revises: 003_create_monitor_logs_table
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_duplicate_fields'
down_revision = '003_create_monitor_logs_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加相似题检测相关字段
    op.add_column('questions', sa.Column('is_duplicate', sa.Boolean(), nullable=True, default=False, comment='是否为相似题'))
    op.add_column('questions', sa.Column('duplicate_group_id', sa.String(50), nullable=True, comment='相似题组ID'))
    op.add_column('questions', sa.Column('duplicate_checked_at', sa.DateTime(), nullable=True, comment='相似度检测时间'))

    # 添加索引以提高查询性能
    op.create_index('idx_questions_is_duplicate', 'questions', ['is_duplicate'])
    op.create_index('idx_questions_duplicate_group_id', 'questions', ['duplicate_group_id'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('idx_questions_duplicate_group_id', 'questions')
    op.drop_index('idx_questions_is_duplicate', 'questions')

    # 删除字段
    op.drop_column('questions', 'duplicate_checked_at')
    op.drop_column('questions', 'duplicate_group_id')
    op.drop_column('questions', 'is_duplicate')