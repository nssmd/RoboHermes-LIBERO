from __future__ import annotations

import json
from pathlib import Path

from robohermes_libero.dashboard import build_dashboard_payload, build_static_preview


def test_default_dashboard_uses_replayed_metric_and_all_120_tasks() -> None:
    payload = build_dashboard_payload()

    assert payload["result"]["solved_tasks"] == 95
    assert payload["result"]["total_tasks"] == 120
    assert payload["result"]["claim_scope"] == "adaptive_cross_release_development_coverage"
    assert len(payload["tasks"]) == 120
    assert sum(row["solved"] for row in payload["tasks"]) == 95


def test_static_preview_is_self_contained_and_has_no_private_paths(tmp_path: Path) -> None:
    output = build_static_preview(tmp_path / "site")

    expected = {"index.html", "styles.css", "app.js", "data.json"}
    assert {path.name for path in output.iterdir()} == expected
    data = json.loads((output / "data.json").read_text(encoding="utf-8"))
    assert data["result"]["rate"] == 95 / 120
    combined = "\n".join(path.read_text(encoding="utf-8") for path in output.iterdir())
    assert "/mnt" + "/workspace" not in combined
    assert "/data" + "/yijia" not in combined
    assert "Adaptive task-level Pass@10" in combined
    assert 'id="architecture"' in combined
    assert "Host-only adjudicator" in combined
