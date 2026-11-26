from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.packages.domains.domain_ownership import DomainOwnership


class TestDomainOwnership:
    BASE: ClassVar[Dict[str, str]] = {
        "backend/swarm-service/src/swarm_service/fleet/a.py": "",
        "backend/swarm-service/src/swarm_service/shared/a.py": "",
        "backend/swarm-storage/src/swarm_storage/fleet/a.py": "",
        "backend/swarm-storage/src/swarm_storage/shared/a.py": "",
        "backend/swarm-clients/src/swarm_clients/missions/a.py": "",
        "backend/swarm-service/src/swarm_service/missions/a.py": "",
        "backend/apps/fleet/pyproject.toml": '[tool.swarm]\ndomains = ["fleet"]\n',
        "backend/apps/fleet/src/swarm_fleet/main.py": "",
        "backend/apps/missions/pyproject.toml": '[tool.swarm]\ndomains = ["missions"]\n',
        "backend/apps/missions/src/swarm_missions/main.py": "",
    }

    def violations_of(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path, self.BASE)
        write_files(tmp_path, files)
        return DomainOwnership().violations(tmp_path)

    def test_the_rule_has_its_name(self) -> None:
        assert DomainOwnership.NAME == "domain_ownership"

    def test_a_consistent_layout_is_accepted(self, tmp_path: Path) -> None:
        files = {
            "backend/swarm-service/src/swarm_service/fleet/b.py": (
                "from swarm_storage.fleet.x import Y\nfrom swarm_storage.shared.x import Z\n"
            ),
            "backend/apps/fleet/src/swarm_fleet/main.py": "from swarm_service.fleet.x import Y\nimport swarm_api.v1.fleet\n",
        }
        assert self.violations_of(tmp_path, files) == []

    def test_a_service_using_another_domains_storage_is_reported(self, tmp_path: Path) -> None:
        files = {"backend/swarm-service/src/swarm_service/fleet/b.py": "from swarm_storage.missions.x import Y\n"}
        found = self.violations_of(tmp_path, files)
        assert len(found) == 1
        assert "fleet domain must not import swarm_storage.missions.x.Y" in found[0]

    def test_a_service_using_another_domains_clients_is_reported(self, tmp_path: Path) -> None:
        files = {"backend/swarm-service/src/swarm_service/fleet/b.py": "from swarm_clients.missions import x\n"}
        assert len(self.violations_of(tmp_path, files)) == 1

    def test_an_app_wiring_a_domain_it_does_not_list_is_reported(self, tmp_path: Path) -> None:
        files = {"backend/apps/fleet/src/swarm_fleet/main.py": "from swarm_service.missions.x import Y\n"}
        found = self.violations_of(tmp_path, files)
        assert len(found) == 1
        assert "does not list the domain missions" in found[0]

    def test_an_app_wiring_an_unlisted_router_is_reported(self, tmp_path: Path) -> None:
        files = {"backend/apps/fleet/src/swarm_fleet/main.py": "from swarm_api.v1.missions.router import R\n"}
        assert len(self.violations_of(tmp_path, files)) == 1

    def test_the_live_router_and_the_shared_folders_are_free(self, tmp_path: Path) -> None:
        source = "from swarm_api.v1.live.x import R\nfrom swarm_service.shared.x import S\n"
        assert self.violations_of(tmp_path, {"backend/apps/fleet/src/swarm_fleet/main.py": source}) == []

    def test_a_domain_listed_by_two_apps_is_reported(self, tmp_path: Path) -> None:
        files = {"backend/apps/missions/pyproject.toml": '[tool.swarm]\ndomains = ["missions", "fleet"]\n'}
        found = self.violations_of(tmp_path, files)
        assert len(found) == 1
        assert "fleet must be listed by exactly one app, not 2" in found[0]

    def test_a_domain_listed_by_no_app_is_reported(self, tmp_path: Path) -> None:
        files = {"backend/swarm-service/src/swarm_service/orphan/a.py": ""}
        found = self.violations_of(tmp_path, files)
        assert len(found) == 1
        assert "orphan must be listed by exactly one app, not 0" in found[0]
