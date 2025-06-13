"""Add proficiency_level to matchmaking

Revision ID: 9669a6de3d37
Revises: 14d50734a3c3
Create Date: 2025-06-12 03:17:51.103654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9669a6de3d37'
down_revision: Union[str, None] = '14d50734a3c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First create the enum type if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'proficiencylevel') THEN
                CREATE TYPE proficiencylevel AS ENUM ('BEGINNER', 'INTERMEDIATE', 'FLUENT');
            END IF;
        END
        $$;
    """)
    
    # Then alter the existing column to use the enum type
    op.alter_column('matchmaking', 'proficiency_level',
               type_=sa.Enum('BEGINNER', 'INTERMEDIATE', 'FLUENT', name='proficiencylevel'),
               postgresql_using='proficiency_level::text::proficiencylevel')

def downgrade() -> None:
    op.alter_column('matchmaking', 'proficiency_level',
               type_=sa.VARCHAR(),
               postgresql_using='proficiency_level::text')
    op.execute("DROP TYPE IF EXISTS proficiencylevel")