"""Add birth_date column to user_data

Revision ID: 9b1bba4bcbbd
Revises:
Create Date: 2025-06-08 23:18:35.849704

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b1bba4bcbbd"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "matchmaking", sa.Column("languages", sa.ARRAY(sa.String()), nullable=True)
    )
    op.add_column(
        "matchmaking", sa.Column("practice_frequency", sa.String(), nullable=True)
    )
    op.drop_column("matchmaking", "age")
    op.add_column("user_data", sa.Column("birth_date", sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user_data", "birth_date")
    op.add_column(
        "matchmaking",
        sa.Column("age", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.drop_column("matchmaking", "practice_frequency")
    op.drop_column("matchmaking", "languages")
    # ### end Alembic commands ###
