"""Initial migration: create reactions table."""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "001_initial_reactions"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create reaction_record table."""
    op.create_table(
        "reaction_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reaction_type", sa.Enum("like", "dislike", name="reactiontype"), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_ip", sa.String(45), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reaction_record_reaction_type"), "reaction_record", ["reaction_type"], unique=False)
    op.create_index(op.f("ix_reaction_record_source_ip"), "reaction_record", ["source_ip"], unique=False)


def downgrade() -> None:
    """Drop reaction_record table."""
    op.drop_index(op.f("ix_reaction_record_source_ip"), table_name="reaction_record")
    op.drop_index(op.f("ix_reaction_record_reaction_type"), table_name="reaction_record")
    op.drop_table("reaction_record")
