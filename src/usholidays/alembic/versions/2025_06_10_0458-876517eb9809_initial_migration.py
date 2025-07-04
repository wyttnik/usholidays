"""Initial migration

Revision ID: 876517eb9809
Revises:
Create Date: 2025-06-10 04:58:38.665505

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "876517eb9809"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "holidays",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("datetime", sa.Date(), nullable=False),
        sa.Column("custom", sa.Boolean(), server_default="False", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "holidays_states",
        sa.Column("holiday_id", sa.Integer(), nullable=False),
        sa.Column("state_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["holiday_id"],
            ["holidays.id"],
        ),
        sa.ForeignKeyConstraint(
            ["state_id"],
            ["states.id"],
        ),
        sa.PrimaryKeyConstraint("holiday_id", "state_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("holidays_states")
    op.drop_table("states")
    op.drop_table("holidays")
    # ### end Alembic commands ###
