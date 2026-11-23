from __future__ import annotations

# Standard library imports
import subprocess
from pathlib import Path

# First-party imports
from tests.postgres.helpers import POSTGRES_APP_ROLE


class TestPostgresFixture:
    def query(self, bin_dir: Path, dsn: str, sql: str) -> str:
        completed = subprocess.run(
            [str(bin_dir / "psql"), "-X", "-q", "-At", "-v", "ON_ERROR_STOP=1", "-c", sql, dsn],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )
        return completed.stdout.strip()

    def test_the_connection_is_made_by_the_application_role(self, postgres_bin_dir: Path, postgres_dsn: str) -> None:
        assert self.query(postgres_bin_dir, postgres_dsn, "SELECT current_user") == POSTGRES_APP_ROLE

    def test_the_application_role_is_neither_superuser_nor_bypassing_row_level_security(
        self, postgres_bin_dir: Path, postgres_dsn: str
    ) -> None:
        sql = "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user"
        assert self.query(postgres_bin_dir, postgres_dsn, sql) == "f|f"

    def test_the_database_is_a_throwaway_one(self, postgres_bin_dir: Path, postgres_dsn: str) -> None:
        assert self.query(postgres_bin_dir, postgres_dsn, "SELECT current_database()").startswith("swarm_test_")

    def test_the_database_starts_without_any_table(self, postgres_bin_dir: Path, postgres_dsn: str) -> None:
        sql = (
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema NOT IN ('pg_catalog', 'information_schema')"
        )
        assert self.query(postgres_bin_dir, postgres_dsn, sql) == "0"

    def test_the_owner_can_create_a_schema(self, postgres_bin_dir: Path, postgres_dsn: str) -> None:
        self.query(postgres_bin_dir, postgres_dsn, "CREATE SCHEMA probe")
        sql = "SELECT count(*) FROM pg_namespace WHERE nspname = 'probe'"
        assert self.query(postgres_bin_dir, postgres_dsn, sql) == "1"
