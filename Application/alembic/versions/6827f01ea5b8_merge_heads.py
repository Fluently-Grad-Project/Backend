"""merge_heads

Revision ID: 6827f01ea5b8
Revises: 4d2861e1153a, 9669a6de3d37
Create Date: 2025-06-13 04:51:06.724039

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "6827f01ea5b8"
down_revision: Union[str, None] = ("4d2861e1153a", "9669a6de3d37")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
