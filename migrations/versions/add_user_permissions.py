"""add user permissions

Revision ID: add_user_permissions
Revises: 1118ec1bd628
Create Date: 2024-05-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_permissions'
down_revision = '1118ec1bd628'
branch_labels = None
depends_on = None


def upgrade():
    # 添加新的用户权限字段
    op.add_column('user', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'))
    op.add_column('user', sa.Column('can_create_project', sa.Boolean(), nullable=True, server_default='1'))
    op.add_column('user', sa.Column('can_create_bug', sa.Boolean(), nullable=True, server_default='1'))
    op.add_column('user', sa.Column('can_reply_bug', sa.Boolean(), nullable=True, server_default='1'))
    
    # 更新现有用户的权限设置
    op.execute("UPDATE user SET is_active = 1, can_create_project = 1, can_create_bug = 1, can_reply_bug = 1")


def downgrade():
    # 删除添加的字段
    op.drop_column('user', 'is_active')
    op.drop_column('user', 'can_create_project')
    op.drop_column('user', 'can_create_bug')
    op.drop_column('user', 'can_reply_bug')