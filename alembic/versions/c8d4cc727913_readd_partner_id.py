"""readd partner id

Revision ID: c8d4cc727913
Revises: 38f9d6c319e5
Create Date: 2024-02-28 17:26:14.543724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'c8d4cc727913'
down_revision: Union[str, None] = '38f9d6c319e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('partner_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order', 'partner', ['partner_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'partner_id')
    # ### end Alembic commands ###