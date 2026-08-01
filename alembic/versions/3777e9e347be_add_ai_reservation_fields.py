"""add ai reservation fields

Revision ID: 3777e9e347be
Revises: 3549b8e779f3
Create Date: 2026-07-30 21:44:40.478107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3777e9e347be'
down_revision: Union[str, Sequence[str], None] = '3549b8e779f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    ai_request_state = sa.Enum(
        "PENDING",
        "COMPLETED",
        "FAILED",
        name="airequeststate"
    )

    # Create the PostgreSQL enum type first
    ai_request_state.create(op.get_bind(), checkfirst=True)

    # Now use it
    op.add_column(
        "ai_usage_tracker",
        sa.Column(
            "state",
            ai_request_state,
            nullable=False,
            server_default="COMPLETED"
        )
    )

    op.add_column(
        "ai_usage_tracker",
        sa.Column(
            "current_request_id",
            sa.String(),
            nullable=True
        )
    )

    # Optional: remove the default after existing rows are populated
    op.alter_column(
        "ai_usage_tracker",
        "state",
        server_default=None
    )

def downgrade() -> None:
    op.drop_column("ai_usage_tracker", "current_request_id")
    op.drop_column("ai_usage_tracker", "state")

    ai_request_state = sa.Enum(
        "PENDING",
        "COMPLETED",
        "FAILED",
        name="airequeststate"
    )

    ai_request_state.drop(op.get_bind(), checkfirst=True)
