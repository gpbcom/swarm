from __future__ import annotations

# Standard library imports
import json
import re
from pathlib import Path
from typing import Dict

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from tests.conventions.helpers import repo_root


class TestTypescriptSettings:
    PACKAGE: str = "frontend/packages/config"

    def path(self, name: str) -> Path:
        return repo_root() / self.PACKAGE / name

    def load_json(self, name: str) -> Dict[str, JsonValue]:
        path = self.path(name)
        assert path.is_file(), f"{self.PACKAGE}/{name} is missing."
        return json.loads(path.read_text(encoding="utf-8"))

    def as_dict(self, value: JsonValue) -> Dict[str, JsonValue]:
        assert isinstance(value, dict)
        return value

    @pytest.mark.parametrize("name", ["package.json", "tsconfig.base.json", "tsconfig.json", "eslint.config.js"])
    def test_each_file_exists(self, name: str) -> None:
        assert self.path(name).is_file()

    def test_the_lock_file_exists(self) -> None:
        assert (repo_root() / "pnpm-lock.yaml").is_file()

    def test_the_package_is_a_private_module_named_swarm_config(self) -> None:
        package = self.load_json("package.json")
        assert package.get("name") == "@swarm/config"
        assert package.get("private") is True
        assert package.get("type") == "module"

    def test_the_package_exports_the_eslint_and_tsconfig_files(self) -> None:
        exports = self.as_dict(self.load_json("package.json").get("exports"))
        assert exports.get("./eslint") == "./eslint.config.js"
        assert exports.get("./tsconfig.base.json") == "./tsconfig.base.json"

    def test_the_package_has_lint_and_typecheck_scripts(self) -> None:
        scripts = self.as_dict(self.load_json("package.json").get("scripts"))
        assert "eslint" in str(scripts.get("lint"))
        typecheck = str(scripts.get("typecheck"))
        assert "tsc" in typecheck
        assert "--noEmit" in typecheck

    @pytest.mark.parametrize("name", ["eslint", "@eslint/js", "typescript", "typescript-eslint"])
    def test_each_dev_dependency_is_pinned_to_an_exact_version(self, name: str) -> None:
        dependencies = self.as_dict(self.load_json("package.json").get("devDependencies"))
        version = dependencies.get(name)
        assert isinstance(version, str)
        assert re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.\-]+)?", version), f"{name} is not pinned: {version!r}."

    @pytest.mark.parametrize(
        "option",
        [
            "strict",
            "noUncheckedIndexedAccess",
            "exactOptionalPropertyTypes",
            "noImplicitOverride",
            "noImplicitReturns",
            "noFallthroughCasesInSwitch",
            "noUnusedLocals",
            "noUnusedParameters",
            "noPropertyAccessFromIndexSignature",
            "forceConsistentCasingInFileNames",
            "isolatedModules",
            "verbatimModuleSyntax",
        ],
    )
    def test_each_strict_compiler_option_is_on(self, option: str) -> None:
        options = self.as_dict(self.load_json("tsconfig.base.json").get("compilerOptions"))
        assert options.get(option) is True

    def test_the_tsconfig_extends_the_base(self) -> None:
        assert self.load_json("tsconfig.json").get("extends") == "./tsconfig.base.json"

    @pytest.mark.parametrize("text", ["typescript-eslint", "strictTypeChecked", "stylisticTypeChecked"])
    def test_the_eslint_config_uses_the_strict_presets(self, text: str) -> None:
        path = self.path("eslint.config.js")
        assert path.is_file(), f"{self.PACKAGE}/eslint.config.js is missing."
        assert text in path.read_text(encoding="utf-8")

    def test_the_lock_file_has_the_config_importer(self) -> None:
        path = repo_root() / "pnpm-lock.yaml"
        assert path.is_file(), "pnpm-lock.yaml is missing."
        assert f"{self.PACKAGE}:" in path.read_text(encoding="utf-8")
