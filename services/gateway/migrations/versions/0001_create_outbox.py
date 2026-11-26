from __future__ import annotations

from alembic import context, op

from swarm_storage.shared.postgres.ddl.outbox_table import OutboxTable
from swarm_storage.shared.postgres.migrations.alembic_migrator import AlembicMigrator

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    schema = context.config.attributes[AlembicMigrator.SCHEMA_ATTRIBUTE]
    for statement in OutboxTable().create(schema):
        op.execute(statement)


def downgrade() -> None:
    schema = context.config.attributes[AlembicMigrator.SCHEMA_ATTRIBUTE]
    for statement in OutboxTable().drop(schema):
        op.execute(statement)
