"""weight discrepancy

Revision ID: a2902370f1cb
Revises: aeb1fde6ef99
Create Date: 2024-01-23 16:48:13.959173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'a2902370f1cb'
down_revision: Union[str, None] = 'aeb1fde6ef99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('weight_discrepancy_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('weight_discrepancy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.Column('charged_weight', sa.Float(), nullable=True),
    sa.Column('excess_weight', sa.Float(), nullable=True),
    sa.Column('excess_rate', sa.Float(), nullable=True),
    sa.Column('courier_image', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('modified_by', sa.Integer(), nullable=True),
    sa.Column('generation_date', sa.DateTime(), nullable=True),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['modified_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['weight_discrepancy_status.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('weight_discrepancy')
    op.drop_table('weight_discrepancy_status')
    # ### end Alembic commands ###
