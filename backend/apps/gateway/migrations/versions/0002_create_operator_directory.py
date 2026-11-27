from __future__ import annotations

from alembic import context, op

from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from swarm_storage.shared.postgres.migrations.alembic_migrator import AlembicMigrator

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    schema = context.config.attributes[AlembicMigrator.SCHEMA_ATTRIBUTE]
    for statement in OperatorDirectoryTables().create(schema):
        op.execute(statement)


def downgrade() -> None:
    schema = context.config.attributes[AlembicMigrator.SCHEMA_ATTRIBUTE]
    for statement in OperatorDirectoryTables().drop(schema):
        op.execute(statement)
