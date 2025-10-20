"""Remove CLOSED status from SprintStatus enum

Revision ID: sfnpwf_dmptf
Revises: 3947a09bbc8a
Create Date: 2025-10-20 22:46:43.247444

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'sfnpwf_dmptf'
down_revision = '3947a09bbc8a'
branch_labels = None
depends_on = None


def upgrade():
    # First update any existing CLOSED sprints to ACTIVE
    op.execute("UPDATE sprints SET status = 'ACTIVE' WHERE status = 'CLOSED'")
    
    # Drop the old enum
    op.execute("DROP TYPE IF EXISTS sprintstatus")
    
    # Create new enum without CLOSED
    op.execute("CREATE TYPE sprintstatus AS ENUM ('DRAFT', 'ACTIVE')")
    
    # The column should automatically use the new enum


def downgrade():
    # Recreate the old enum with CLOSED
    op.execute("DROP TYPE IF EXISTS sprintstatus")
    op.execute("CREATE TYPE sprintstatus AS ENUM ('DRAFT', 'ACTIVE', 'CLOSED')")
