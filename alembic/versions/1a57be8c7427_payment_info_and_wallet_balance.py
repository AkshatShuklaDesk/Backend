"""payment info and wallet balance

Revision ID: 1a57be8c7427
Revises: cf93d96ba6bc
Create Date: 2024-02-19 23:18:22.762010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '1a57be8c7427'
down_revision: Union[str, None] = 'cf93d96ba6bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment_status_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('payment_order_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('users', sa.Column('wallet_balance', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'wallet_balance')
    op.drop_table('payment_status_details')
    # ### end Alembic commands ###