from __future__ import annotations

# Standard library imports
import sys

# First-party imports
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_models.config.app_config import AppConfig
from swarm_scripts.swarm_apps import SwarmApps
from swarm_service.shared.migrations.factories.schema_migration_factory import SchemaMigrationFactory
from swarm_web.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory


def main() -> int:
    """Upgrade the PostgreSQL schema of every app, or of the one ``SWARM_APP`` names, to its latest revision.

    Returns:
        int: 0 when every schema is upgraded, 1 when a migration failed, 2 when ``SWARM_APP`` names no app.

    Notes:
        - The DSN of each app is read from the environment entry its ``postgres.dsn_key`` names,
          ``SWARM_<APP>_POSTGRES_DSN``, and is never printed.
        - In an image, the migration runs as a job with ``SWARM_APP`` and ``SWARM_APP_ROOT`` set.
    """
    LoggingConfigurator(LoggingConfig()).configure()
    apps = SwarmApps()
    selected = apps.selected()
    if not selected:
        print(f"{SwarmApps.APP_KEY} names no app: {apps.requested()!r}.", file=sys.stderr)
        return 2
    code = 0
    for app in selected:
        config = apps.config(app)
        folder = apps.folder(app) / AppConfig.MIGRATIONS_FOLDER
        migration = SchemaMigrationFactory(config.postgres, config.schema_name, folder).create()
        AsyncRunnableRunnerFactory(migration).create().execute()
        if migration.exit_code != 0:
            print(f"The migration of the {app.value} schema failed.", file=sys.stderr)
            code = 1
        else:
            print(f"Migrated the {app.value} schema.")
    return code
