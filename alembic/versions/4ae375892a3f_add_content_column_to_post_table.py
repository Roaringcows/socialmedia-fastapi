"""add content column to post table

Revision ID: 4ae375892a3f
Revises: 6850bda97592
Create Date: 2022-11-19 08:43:26.896314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ae375892a3f'
down_revision = '6850bda97592'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
