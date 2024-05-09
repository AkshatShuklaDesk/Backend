"""waybill col add

Revision ID: 1b89baf13e2f
Revises: 47c42ec18b39
Create Date: 2023-12-30 00:41:17.398793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '1b89baf13e2f'
down_revision: Union[str, None] = '47c42ec18b39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('waybill_no', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'waybill_no')
    # ### end Alembic commands ###
