"""empty message

Revision ID: 00bb44b8e07b
Revises: e12ccf3dbb2e
Create Date: 2017-11-16 18:11:56.863840

"""

# revision identifiers, used by Alembic.
revision = '00bb44b8e07b'
down_revision = 'e12ccf3dbb2e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('asin_analytics', sa.Column('last_trademark_indexed_date', sa.String(), nullable=True))
    op.drop_column('asin_metadata', 'last_trademark_indexed_date')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('asin_metadata', sa.Column('last_trademark_indexed_date', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('asin_analytics', 'last_trademark_indexed_date')
    ### end Alembic commands ###
