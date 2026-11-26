from __future__ import annotations

# Standard library imports
import ast

# First-party imports
from tests.conventions.rules.trees.imported_names import ImportedNames


class TestImportedNames:
    def test_plain_and_from_imports_give_absolute_names(self) -> None:
        tree = ast.parse("import a.b\nfrom c.d import e, f\nfrom g import *\n")
        assert ImportedNames.of(tree) == [(1, "a.b"), (2, "c.d.e"), (2, "c.d.f"), (3, "g")]

    def test_relative_imports_give_nothing(self) -> None:
        assert ImportedNames.of(ast.parse("from . import a\nfrom .b import c\n")) == []

    def test_nested_imports_are_found(self) -> None:
        tree = ast.parse("if True:\n    import a\n")
        assert ImportedNames.of(tree) == [(2, "a")]
