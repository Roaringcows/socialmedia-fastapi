"""add foreign-key to post table

Revision ID: 46237d8b6cf3
Revises: c35cad06effa
Create Date: 2022-11-19 08:56:10.976529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46237d8b6cf3'
down_revision = 'c35cad06effa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table="posts", referent_table="users", local_cols=[
                          'owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade() -> None:
    op.drop_constraint('post_user_fk', table_name='posts')
    op.drop_column('posts', 'owner_id')
    pass
