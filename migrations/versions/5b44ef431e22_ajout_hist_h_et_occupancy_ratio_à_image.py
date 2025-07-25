"""Ajout hist_h et occupancy_ratio à Image

Revision ID: 5b44ef431e22
Revises: 9a8be40736b0
Create Date: 2025-06-23 17:56:08.300065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b44ef431e22'
down_revision = '9a8be40736b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hist_h', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('occupancy_ratio', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.drop_column('occupancy_ratio')
        batch_op.drop_column('hist_h')

    # ### end Alembic commands ###
