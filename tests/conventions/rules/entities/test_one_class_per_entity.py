from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.entities.one_class_per_entity import OneClassPerEntity
from tests.conventions.rules.service_tree import ServiceTree


class TestOneClassPerEntity:
    STORAGE: ClassVar[str] = "backend/swarm-storage/src/swarm_storage/drones/"
    SERVICE: ClassVar[str] = "backend/swarm-service/src/swarm_service/drones/"

    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path, files)
        return OneClassPerEntity().violations(ServiceTree(tmp_path))

    def test_the_rule_is_named_one_class_per_entity(self) -> None:
        assert OneClassPerEntity.NAME == "one_class_per_entity"

    def test_a_repository_without_backend_has_no_violation(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {"README.md": "x"}) == []

    def test_one_class_per_entity_in_each_layer_is_allowed(self, tmp_path: Path) -> None:
        files = {
            f"{self.STORAGE}drone_repository.py": "class DroneRepository:\n    pass\n",
            f"{self.STORAGE}squad_repository.py": "class SquadRepository:\n    pass\n",
            f"{self.SERVICE}drone_service.py": "class DroneService:\n    pass\n",
        }
        assert self.violations(tmp_path, files) == []

    def test_two_classes_of_one_entity_in_one_layer_are_reported_with_both_names(self, tmp_path: Path) -> None:
        files = {
            f"{self.SERVICE}drone_service.py": "class DroneService:\n    pass\n",
            f"{self.SERVICE}drone_command_service.py": "class DroneService:\n    pass\n",
        }
        files[f"{self.SERVICE}other/drone_flight_service.py"] = "class DroneFlightService:\n    pass\n"
        found = self.violations(tmp_path, files)
        assert len(found) == 1
        assert "'Drone'" in found[0]
        assert "DroneService, DroneService" in found[0]

    def test_a_duplicate_pair_names_both_classes(self, tmp_path: Path) -> None:
        files = {
            f"{self.STORAGE}a.py": "class DroneRepository:\n    pass\n",
            f"{self.STORAGE}b.py": "class DroneRepository:\n    pass\n",
        }
        found = self.violations(tmp_path, files)
        assert len(found) == 1
        assert "a.py" in found[0]
        assert "b.py" in found[0]

    def test_the_same_entity_in_two_layers_is_allowed(self, tmp_path: Path) -> None:
        files = {
            f"{self.STORAGE}drone_repository.py": "class DroneRepository:\n    pass\n",
            f"{self.SERVICE}drone_service.py": "class DroneService:\n    pass\n",
        }
        assert self.violations(tmp_path, files) == []

    @pytest.mark.parametrize("name", ["DroneServiceFactory", "SEDroneServiceError", "DroneHelper", "Service"])
    def test_factories_exceptions_and_other_names_are_exempt(self, tmp_path: Path, name: str) -> None:
        files = {
            f"{self.SERVICE}drone_service.py": "class DroneService:\n    pass\n",
            f"{self.SERVICE}other.py": f"class {name}:\n    pass\n",
        }
        assert self.violations(tmp_path, files) == []

    @pytest.mark.parametrize(
        ("layer", "role"),
        [
            ("swarm_storage", "Repository"),
            ("swarm_clients", "Client"),
            ("swarm_service", "Service"),
            ("swarm_api", "Router"),
        ],
    )
    def test_each_layer_has_its_fixed_role(self, tmp_path: Path, layer: str, role: str) -> None:
        folder = f"backend/lib/src/{layer}/x/"
        files = {
            f"{folder}a.py": f"class Drone{role}:\n    pass\n",
            f"{folder}b.py": f"class Drone{role}:\n    pass\n",
        }
        assert len(self.violations(tmp_path, files)) == 1

    def test_a_class_with_another_role_in_a_layer_is_ignored(self, tmp_path: Path) -> None:
        files = {
            f"{self.STORAGE}drone_repository.py": "class DroneRepository:\n    pass\n",
            f"{self.STORAGE}drone_service.py": "class DroneService:\n    pass\n",
        }
        assert self.violations(tmp_path, files) == []
