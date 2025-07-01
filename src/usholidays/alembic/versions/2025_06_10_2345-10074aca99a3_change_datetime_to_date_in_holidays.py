"""Change datetime to date in holidays

Revision ID: 10074aca99a3
Revises: 226b977c1746
Create Date: 2025-06-10 23:45:22.318406

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "10074aca99a3"
down_revision: Union[str, None] = "226b977c1746"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("holidays", "datetime", new_column_name="date", nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("holidays", "date", new_column_name="datetime", nullable=False)
    # ### end Alembic commands ###
