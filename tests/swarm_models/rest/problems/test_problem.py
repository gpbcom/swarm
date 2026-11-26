from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.rest.problems.exceptions import (
    SEInvalidProblemException,
    SEProblemInvalidDetail,
    SEProblemInvalidInstance,
    SEProblemInvalidStatus,
    SEProblemInvalidTitle,
    SEProblemInvalidType,
)
from swarm_models.rest.problems.problem import Problem


class TestProblem:
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "type": "https://swarm.example/problems/not-found",
        "title": "Not Found",
        "status": 404,
        "detail": "No such mission.",
        "instance": "/missions/42",
    }
    DEFAULT_TYPE: ClassVar[str] = "about:blank"
    MEDIA_TYPE_VALUE: ClassVar[str] = "application/problem+json"

    def build(self, **changes: JsonValue) -> Problem:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return Problem.model_validate(values)

    def test_defaults(self) -> None:
        problem = Problem(title="Not Found", status=404)
        assert problem.type == self.DEFAULT_TYPE
        assert problem.detail is None
        assert problem.instance is None

    def test_the_media_type_is_problem_json(self) -> None:
        assert Problem.MEDIA_TYPE == self.MEDIA_TYPE_VALUE

    def test_full_valid_construction(self) -> None:
        problem = self.build()
        assert problem.type == self.VALID["type"]
        assert problem.title == self.VALID["title"]
        assert problem.status == self.VALID["status"]
        assert problem.detail == self.VALID["detail"]
        assert problem.instance == self.VALID["instance"]

    @pytest.mark.parametrize(
        ("name", "default"),
        [("type", "about:blank"), ("detail", None), ("instance", None)],
    )
    def test_none_becomes_the_default(self, name: str, default: JsonValue) -> None:
        assert getattr(self.build(**{name: None}), name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("type", "", SEProblemInvalidType),
            ("type", "   ", SEProblemInvalidType),
            ("type", "about: blank", SEProblemInvalidType),
            ("type", 3, SEProblemInvalidType),
            ("type", True, SEProblemInvalidType),
            ("title", None, SEProblemInvalidTitle),
            ("title", "", SEProblemInvalidTitle),
            ("title", "   ", SEProblemInvalidTitle),
            ("title", 3, SEProblemInvalidTitle),
            ("status", None, SEProblemInvalidStatus),
            ("status", 399, SEProblemInvalidStatus),
            ("status", 600, SEProblemInvalidStatus),
            ("status", True, SEProblemInvalidStatus),
            ("status", 404.5, SEProblemInvalidStatus),
            ("status", "404", SEProblemInvalidStatus),
            ("detail", "", SEProblemInvalidDetail),
            ("detail", "   ", SEProblemInvalidDetail),
            ("detail", 3, SEProblemInvalidDetail),
            ("instance", "", SEProblemInvalidInstance),
            ("instance", "   ", SEProblemInvalidInstance),
            ("instance", "/a b", SEProblemInvalidInstance),
            ("instance", 3, SEProblemInvalidInstance),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    @pytest.mark.parametrize(
        "error",
        [
            SEProblemInvalidType,
            SEProblemInvalidTitle,
            SEProblemInvalidStatus,
            SEProblemInvalidDetail,
            SEProblemInvalidInstance,
        ],
    )
    def test_every_field_error_is_a_problem_exception(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidProblemException)

    def test_the_bounds_of_status(self) -> None:
        assert Problem.STATUS_MIN == 400
        assert Problem.STATUS_MAX == 599

    @pytest.mark.parametrize("bound", [Problem.STATUS_MIN, Problem.STATUS_MAX])
    def test_the_bounds_of_status_are_accepted(self, bound: int) -> None:
        assert self.build(status=bound).status == bound

    def test_strings_are_stripped(self) -> None:
        problem = self.build(title="  Not Found  ", detail="  Gone.  ", instance="  /missions/42  ")
        assert problem.title == "Not Found"
        assert problem.detail == "Gone."
        assert problem.instance == "/missions/42"

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_problem_is_refused(self) -> None:
        problem = self.build()
        with pytest.raises(ValidationError):
            problem.status = 500

    def test_round_trip(self) -> None:
        problem = self.build()
        assert Problem.model_validate(problem.model_dump(exclude_none=True)) == problem

    def test_round_trip_without_the_optional_fields(self) -> None:
        problem = Problem(title="Not Found", status=404)
        dumped = problem.model_dump(exclude_none=True)
        assert set(dumped) == {"type", "title", "status"}
        assert Problem.model_validate(dumped) == problem
