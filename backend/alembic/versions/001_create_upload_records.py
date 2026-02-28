"""
创建upload_records表的迁移脚本

Revision ID: 001_create_upload_records
Revises: 
Create Date: 2026-02-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_create_upload_records'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建upload_records表
    op.create_table(
        'upload_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('folder_code', sa.String(10), nullable=False, comment='学科学段短代码，如：h7s9m2'),
        sa.Column('education_level', sa.String(20), nullable=False, comment='学段中文，如：高中'),
        sa.Column('subject', sa.String(20), nullable=False, comment='学科中文，如：数学'),
        sa.Column('batch_id', sa.String(30), nullable=False, comment='批次ID：YYYYMMDD-HHMMSS-XXXXXX'),
        sa.Column('record_date', sa.Date(), nullable=False, comment='记录日期'),
        sa.Column('full_path', sa.String(500), nullable=False, comment='完整存储路径'),
        sa.Column('teacher_id', sa.Integer(), nullable=True, comment='老师ID（预留）'),
        sa.Column('teacher_name', sa.String(50), nullable=True, comment='老师姓名，如：张老师'),
        sa.Column('display_name', sa.String(255), nullable=False, comment='显示名称，如：期中考试'),
        sa.Column('original_filename', sa.String(255), nullable=False, comment='原始文件名，如：期中考试.zip'),
        sa.Column('file_size', sa.BigInteger(), nullable=True, comment='文件大小（字节）'),
        sa.Column('file_count', sa.Integer(), nullable=True, comment='题目数量'),
        sa.Column('image_count', sa.Integer(), nullable=True, comment='图片数量'),
        sa.Column('status', sa.String(20), nullable=False, server_default='completed', comment='状态：pending/processing/completed/error'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='扩展信息（JSON格式）'),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='上传时间'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='完成时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('folder_code', 'record_date', 'batch_id', name='uix_upload_folder_date_batch')
    )
    
    # 创建索引
    op.create_index('idx_upload_folder', 'upload_records', ['folder_code'])
    op.create_index('idx_upload_date', 'upload_records', ['record_date'])
    op.create_index('idx_upload_teacher', 'upload_records', ['teacher_name', 'record_date'])
    op.create_index('idx_upload_status', 'upload_records', ['status'])
    op.create_index('idx_upload_filename', 'upload_records', ['folder_code', 'teacher_name', 'record_date', 'original_filename'])


def downgrade():
    # 删除索引
    op.drop_index('idx_upload_filename', table_name='upload_records')
    op.drop_index('idx_upload_status', table_name='upload_records')
    op.drop_index('idx_upload_teacher', table_name='upload_records')
    op.drop_index('idx_upload_date', table_name='upload_records')
    op.drop_index('idx_upload_folder', table_name='upload_records')
    
    # 删除表
    op.drop_table('upload_records')
