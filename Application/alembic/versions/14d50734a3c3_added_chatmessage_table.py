"""added ChatMessage table

Revision ID: 14d50734a3c3
Revises: 389cabc131d1
Create Date: 2025-06-10 07:22:06.563703

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "14d50734a3c3"
down_revision: Union[str, None] = "389cabc131d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###
