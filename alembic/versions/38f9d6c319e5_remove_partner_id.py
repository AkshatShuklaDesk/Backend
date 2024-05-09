"""remove partner id

Revision ID: 38f9d6c319e5
Revises: 1a57be8c7427
Create Date: 2024-02-28 17:25:56.976158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '38f9d6c319e5'
down_revision: Union[str, None] = '1a57be8c7427'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('order_partner_id_fkey', 'order', type_='foreignkey')
    op.drop_column('order', 'partner_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('partner_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('order_partner_id_fkey', 'order', 'partner', ['partner_id'], ['id'])
    # ### end Alembic commands ###