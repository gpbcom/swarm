from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest
from tests.conventions.helpers import write_files
from tests.conventions.rules.classes.pydantic_models_in_models import PydanticModelsInModels
from tests.conventions.rules.service_tree import ServiceTree


class TestPydanticModelsInModels:
    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        root = tmp_path / "services" / "sample"
        write_files(root, files)
        return PydanticModelsInModels().violations(ServiceTree(root))

    def test_the_rule_has_a_name(self) -> None:
        assert PydanticModelsInModels.NAME == "pydantic_models_in_models"

    @pytest.mark.parametrize(
        "path, source",
        [
            ("src/sample/service/customer.py", "class Customer(BaseModel):\n    pass\n"),
            ("src/sample/api/customer.py", "class Customer(pydantic.BaseModel):\n    pass\n"),
            ("src/sample/service/numbers.py", "class Numbers(RootModel[List[int]]):\n    pass\n"),
            ("tests/service/customer.py", "class Customer(BaseModel):\n    pass\n"),
        ],
    )
    def test_a_model_outside_models_gives_one_violation(self, tmp_path: Path, path: str, source: str) -> None:
        found = self.violations(tmp_path, {path: source})
        assert len(found) == 1
        assert found[0].startswith(f"sample/{path}:")

    def test_a_subclass_of_a_models_layer_model_in_service_gives_one_violation(self, tmp_path: Path) -> None:
        files = {
            "src/sample/models/customer.py": "class Customer(BaseModel):\n    pass\n",
            "src/sample/service/vip.py": "class Vip(Customer):\n    pass\n",
        }
        found = self.violations(tmp_path, files)
        assert len(found) == 1
        assert "service/vip.py" in found[0]

    @pytest.mark.parametrize(
        "path",
        ["src/sample/models/customer.py", "src/sample/models/customers/enums/customer.py"],
    )
    def test_a_model_in_models_gives_no_violation(self, tmp_path: Path, path: str) -> None:
        assert self.violations(tmp_path, {path: "class Customer(BaseModel):\n    pass\n"}) == []

    def test_a_plain_class_gives_no_violation(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {"src/sample/service/customer.py": "class Customer:\n    pass\n"}) == []
