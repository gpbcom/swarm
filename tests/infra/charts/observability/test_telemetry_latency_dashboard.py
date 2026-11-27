from __future__ import annotations

# Standard library imports
import json
from pathlib import Path
from typing import ClassVar, Dict, List, Tuple, cast

# Third-party imports
from pydantic import JsonValue


class TestTelemetryLatencyDashboard:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[4]
    DASHBOARD: ClassVar[Path] = ROOT / "infra" / "charts" / "observability" / "dashboards" / "telemetry-latency.json"
    ENCODING: ClassVar[str] = "utf-8"
    UID: ClassVar[str] = "swarm-telemetry-latency"
    UID_KEY: ClassVar[str] = "uid"
    TITLE_KEY: ClassVar[str] = "title"
    PANELS_KEY: ClassVar[str] = "panels"
    TYPE_KEY: ClassVar[str] = "type"
    TARGETS_KEY: ClassVar[str] = "targets"
    EXPR_KEY: ClassVar[str] = "expr"
    FIELD_CONFIG_KEY: ClassVar[str] = "fieldConfig"
    DEFAULTS_KEY: ClassVar[str] = "defaults"
    UNIT_KEY: ClassVar[str] = "unit"
    THRESHOLDS_KEY: ClassVar[str] = "thresholds"
    STEPS_KEY: ClassVar[str] = "steps"
    VALUE_KEY: ClassVar[str] = "value"
    PANEL_TYPE: ClassVar[str] = "timeseries"
    UNIT: ClassVar[str] = "ms"
    PANEL_COUNT: ClassVar[int] = 3
    QUANTILE: ClassVar[str] = "histogram_quantile(0.95"
    TELEMETRY_BUCKET: ClassVar[str] = "swarm_telemetry_drone_to_screen_milliseconds_bucket"
    FRAME_BUCKET: ClassVar[str] = "swarm_live_frame_to_pixels_milliseconds_bucket"
    CELL_LABEL: ClassVar[str] = 'swarm_live_path="cell"'
    EDGE_LABEL: ClassVar[str] = 'swarm_live_path="edge"'
    FORBIDDEN_LABEL: ClassVar[str] = "drone_id"
    CASES: ClassVar[List[Tuple[str, List[str], float]]] = [
        ("through the cell", [TELEMETRY_BUCKET, CELL_LABEL], 400),
        ("at the edge", [TELEMETRY_BUCKET, EDGE_LABEL], 150),
        ("frame to pixels", [FRAME_BUCKET], 50),
    ]

    def _text(self) -> str:
        return self.DASHBOARD.read_text(encoding=self.ENCODING)

    def _dashboard(self) -> Dict[str, JsonValue]:
        loaded = json.loads(self._text())
        assert isinstance(loaded, dict)
        return cast(Dict[str, JsonValue], loaded)

    def _panels(self) -> List[Dict[str, JsonValue]]:
        panels = self._dashboard()[self.PANELS_KEY]
        assert isinstance(panels, list)
        result: List[Dict[str, JsonValue]] = []
        for panel in panels:
            assert isinstance(panel, dict)
            result.append(cast(Dict[str, JsonValue], panel))
        return result

    def _expressions(self, panel: Dict[str, JsonValue]) -> List[str]:
        targets = panel[self.TARGETS_KEY]
        assert isinstance(targets, list)
        expressions: List[str] = []
        for target in targets:
            assert isinstance(target, dict)
            expression = target[self.EXPR_KEY]
            assert isinstance(expression, str)
            expressions.append(expression)
        return expressions

    def _defaults(self, panel: Dict[str, JsonValue]) -> Dict[str, JsonValue]:
        config = panel[self.FIELD_CONFIG_KEY]
        assert isinstance(config, dict)
        defaults = config[self.DEFAULTS_KEY]
        assert isinstance(defaults, dict)
        return cast(Dict[str, JsonValue], defaults)

    def _threshold_values(self, panel: Dict[str, JsonValue]) -> List[float]:
        thresholds = self._defaults(panel)[self.THRESHOLDS_KEY]
        assert isinstance(thresholds, dict)
        steps = thresholds[self.STEPS_KEY]
        assert isinstance(steps, list)
        values: List[float] = []
        for step in steps:
            assert isinstance(step, dict)
            value = step[self.VALUE_KEY]
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                values.append(float(value))
        return values

    def _panel_for(self, parts: List[str]) -> Dict[str, JsonValue]:
        matches = [
            panel
            for panel in self._panels()
            if any(all(part in expression for part in parts) for expression in self._expressions(panel))
        ]
        assert len(matches) == 1
        return matches[0]

    def test_the_dashboard_is_valid_json_with_its_uid_and_a_title(self) -> None:
        dashboard = self._dashboard()
        assert dashboard[self.UID_KEY] == self.UID
        title = dashboard[self.TITLE_KEY]
        assert isinstance(title, str)
        assert title.strip()

    def test_it_has_exactly_three_timeseries_panels_in_milliseconds(self) -> None:
        panels = self._panels()
        assert len(panels) == self.PANEL_COUNT
        for panel in panels:
            assert panel[self.TYPE_KEY] == self.PANEL_TYPE
            assert self._defaults(panel)[self.UNIT_KEY] == self.UNIT

    def test_every_panel_has_a_prometheus_target(self) -> None:
        for panel in self._panels():
            assert self._expressions(panel)

    def test_every_panel_is_a_p95_over_its_histogram_with_its_budget_as_a_threshold(self) -> None:
        for name, parts, budget in self.CASES:
            panel = self._panel_for(parts)
            assert all(self.QUANTILE in expression for expression in self._expressions(panel)), name
            assert budget in self._threshold_values(panel), name

    def test_the_cell_and_edge_panels_filter_on_their_own_path_only(self) -> None:
        cell = self._panel_for([self.TELEMETRY_BUCKET, self.CELL_LABEL])
        edge = self._panel_for([self.TELEMETRY_BUCKET, self.EDGE_LABEL])
        assert not any(self.EDGE_LABEL in expression for expression in self._expressions(cell))
        assert not any(self.CELL_LABEL in expression for expression in self._expressions(edge))

    def test_drone_id_appears_nowhere_in_the_dashboard(self) -> None:
        assert self.FORBIDDEN_LABEL not in self._text()
