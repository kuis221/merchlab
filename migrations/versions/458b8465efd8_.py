"""empty message

Revision ID: 458b8465efd8
Revises: 3b51eb05f42e
Create Date: 2018-02-15 21:25:43.208727

"""

# revision identifiers, used by Alembic.
revision = '458b8465efd8'
down_revision = '3b51eb05f42e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('asin_metadata', sa.Column('last_indexed_date', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('asin_metadata', 'last_indexed_date')
    ### end Alembic commands ###
