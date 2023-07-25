"""added bio and pfp to users column

Revision ID: 07a6c8c94bf1
Revises: b1ee6832f1e2
Create Date: 2023-07-22 23:35:26.846466

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07a6c8c94bf1'
down_revision = 'b1ee6832f1e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('biography', sa.String(), nullable=True))
    op.add_column('users', sa.Column('profile_photo', sa.String(), nullable=True, server_default=sa.text("'https://firebasestorage.googleapis.com/v0/b/connectx-22806.appspot.com/o/images%2FDefaultpfp4.jpeg?alt=media&token=0ec8e6d7-9967-45f7-a8a0-401f4ec50ad4'")))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_photo')
    op.drop_column('users', 'biography')
    # ### end Alembic commands ###

