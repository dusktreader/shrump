"""Initial migration

Revision ID: 2dc0dc8ec2ae
Revises:
Create Date: 2024-10-03 22:47:41.198274

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2dc0dc8ec2ae"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "identities",
        sa.Column("uuid", sa.Uuid(), nullable=False),
        sa.Column("owner", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_identities_owner"), "identities", ["owner"], unique=False)
    op.create_index(op.f("ix_identities_uuid"), "identities", ["uuid"], unique=False)
    op.create_table(
        "events",
        sa.Column("identity_id", sa.Integer(), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["identity_id"],
            ["identities.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("events")
    op.drop_index(op.f("ix_identities_uuid"), table_name="identities")
    op.drop_index(op.f("ix_identities_owner"), table_name="identities")
    op.drop_table("identities")
    # ### end Alembic commands ###
