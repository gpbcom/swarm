from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.api.api_only_endpoints import ApiOnlyEndpoints
from tests.conventions.rules.service_tree import ServiceTree


class TestApiOnlyEndpoints:
    PATH: ClassVar[str] = "backend/swarm-api/src/swarm_api/v1/drones/drone_router.py"
    OTHER_PATH: ClassVar[str] = "backend/swarm-service/src/swarm_service/drones/drone_service.py"
    HEADER: ClassVar[str] = "from fastapi import APIRouter, Depends\n\nrouter = APIRouter()\n\n"

    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path, files)
        return ApiOnlyEndpoints().violations(ServiceTree(tmp_path))

    def test_the_rule_is_named_api_only_endpoints(self) -> None:
        assert ApiOnlyEndpoints.NAME == "api_only_endpoints"

    def test_a_repository_without_backend_has_no_violation(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {"README.md": "x"}) == []

    @pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete", "websocket"])
    def test_a_function_decorated_by_a_router_method_is_allowed(self, tmp_path: Path, method: str) -> None:
        source = f'{self.HEADER}@router.{method}("/x")\nasync def endpoint() -> None:\n    pass\n'
        assert self.violations(tmp_path, {self.PATH: source}) == []

    def test_a_router_subclass_and_a_middleware_are_allowed(self, tmp_path: Path) -> None:
        source = (
            "class DroneRouter(APIRouter):\n    pass\n\nclass IdempotencyMiddleware(BaseHTTPMiddleware):\n    pass\n"
        )
        assert self.violations(tmp_path, {self.PATH: source}) == []

    def test_a_pure_asgi_middleware_is_allowed(self, tmp_path: Path) -> None:
        source = "class KeyMiddleware:\n    async def __call__(self, scope, receive, send) -> None:\n        pass\n"
        assert self.violations(tmp_path, {self.PATH: source}) == []

    def test_a_class_whose_call_is_no_asgi_call_is_reported(self, tmp_path: Path) -> None:
        source = "class Builder:\n    def __call__(self, app) -> None:\n        pass\n"
        found = self.violations(tmp_path, {self.PATH: source})
        assert len(found) == 1
        assert "'Builder'" in found[0]

    def test_a_class_that_registers_exception_handlers_is_allowed(self, tmp_path: Path) -> None:
        source = (
            "class ProblemHandlers:\n"
            "    def install(self, app) -> None:\n"
            "        app.add_exception_handler(Exception, self.handle)\n\n"
            "    async def handle(self, request, error) -> None:\n"
            "        pass\n"
        )
        assert self.violations(tmp_path, {self.PATH: source}) == []

    def test_a_depends_provider_function_and_class_are_allowed(self, tmp_path: Path) -> None:
        source = (
            f"{self.HEADER}def get_service() -> None:\n    pass\n\n"
            "class Pagination:\n    pass\n\n"
            '@router.get("/x")\n'
            "async def endpoint(a=Depends(get_service), b=Depends(Pagination)) -> None:\n    pass\n"
        )
        assert self.violations(tmp_path, {self.PATH: source}) == []

    def test_exception_handlers_are_allowed_by_name_or_registration(self, tmp_path: Path) -> None:
        source = (
            "async def problem_handler(request, error) -> None:\n    pass\n\n"
            "async def on_missing(request, error) -> None:\n    pass\n\n"
            "def install(app) -> None:\n    app.add_exception_handler(KeyError, on_missing)\n"
        )
        found = self.violations(tmp_path, {self.PATH: source})
        assert len(found) == 1
        assert "'install'" in found[0]

    def test_a_helper_function_is_reported_with_its_line(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.PATH: "def helper() -> None:\n    pass\n"})
        assert len(found) == 1
        assert ":1:" in found[0]
        assert "'helper'" in found[0]

    def test_a_plain_class_is_reported(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.PATH: "class Builder:\n    pass\n"})
        assert len(found) == 1
        assert "'Builder'" in found[0]

    @pytest.mark.parametrize(
        "base", ["Runnable", "AsyncRunnable", "RunnableFactory[Router]", "AsyncRunnableFactory", "swarm.AsyncRunnable"]
    )
    def test_a_runnable_or_a_factory_is_reported(self, tmp_path: Path, base: str) -> None:
        found = self.violations(tmp_path, {self.PATH: f"class Server({base}):\n    pass\n"})
        assert len(found) == 1
        assert "service layer" in found[0]

    def test_a_runnable_that_also_subclasses_a_router_is_still_reported(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.PATH: "class Both(APIRouter, AsyncRunnable):\n    pass\n"})
        assert len(found) == 1

    def test_other_layers_are_not_checked(self, tmp_path: Path) -> None:
        source = "class DroneService(AsyncRunnable):\n    pass\n"
        assert self.violations(tmp_path, {self.OTHER_PATH: source}) == []
