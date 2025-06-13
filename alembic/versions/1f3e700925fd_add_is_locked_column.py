"""add_is_locked_column

Revision ID: 1f3e700925fd
Revises: 6827f01ea5b8
Create Date: 2025-06-13 04:58:02.802084

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f3e700925fd"
down_revision: Union[str, None] = "6827f01ea5b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # op.add_column(
    #     "user_data",
    #     sa.Column("is_locked", sa.Boolean(), nullable=True, server_default="false"),
    # )
    pass


def downgrade():
    op.drop_column("user_data", "is_locked")
