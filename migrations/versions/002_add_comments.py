"""Add comments table migration."""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002_add_comments"
down_revision = "001_initial_reactions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create comment_record table."""
    op.create_table(
        "comment_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_ip", sa.String(45), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comment_record_source_ip"), "comment_record", ["source_ip"], unique=False)


def downgrade() -> None:
    """Drop comment_record table."""
    op.drop_index(op.f("ix_comment_record_source_ip"), table_name="comment_record")
    op.drop_table("comment_record")
