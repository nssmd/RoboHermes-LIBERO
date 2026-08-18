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


def test_dashboard_includes_locked_publication_experiment_matrix() -> None:
    publication = build_dashboard_payload()["publication"]

    assert publication["schema"] == "robohermes.libero_publication.v1"
    assert publication["headline"] == {
        "label": "Adaptive task-level Pass@10",
        "solved_tasks": 95,
        "total_tasks": 120,
        "rate": 95 / 120,
        "scope": "adaptive_cross_release_development_coverage",
    }

    adaptive = publication["experiments"]["adaptive_sequential"]
    assert adaptive["pass_curve"] == [32, 45, 52, 66, 71, 76, 81, 82, 82, 83]
    assert adaptive["total_tokens"] == 2_342_408_295
    assert adaptive["active_round_wall_s"] == 39_922.417962

    strict = publication["experiments"]["strict_standard130"]
    assert strict["pass_curve"] == [23, 35, 43, 49, 56, 60, 61, 63, 64, 67]
    assert strict["solved_tasks"] == 67
    assert strict["total_tasks"] == 130
    assert strict["valid_task_seed_verdicts"] == 846

    matched = publication["experiments"]["matched_code"]
    assert matched["success"]["code_on"] == {"success": 174, "episodes": 600}
    assert matched["success"]["code_off"] == {"success": 129, "episodes": 600}
    assert matched["success"]["paired_delta_pp"] == 7.5
    assert matched["success"]["mcnemar_p"] == 8.06219814539768e-05
    assert matched["efficiency"]["matched_tasks"] == 118
    assert matched["efficiency"]["median_total_tokens"] == {
        "code_on": 2_577_694.0,
        "code_off": 3_653_234.5,
        "reduction": 0.29440773648666685,
    }

    act = publication["experiments"]["act"]
    assert act["simulator_successes"] == 1
    assert act["trials"] == 1
    assert act["held_out"] is False
    assert act["claim_scope"] == "matched_success_case_not_generalization"


def test_publication_sources_cover_competitive_reference_set() -> None:
    sources = build_dashboard_payload()["publication"]["sources"]
    urls = {source["url"] for source in sources}

    assert "https://arxiv.org/abs/2603.24060" in urls
    assert "https://arxiv.org/abs/2607.18060" in urls
    assert "https://arxiv.org/abs/2608.03924" in urls
    assert "https://arxiv.org/abs/2606.19980" in urls
    assert "https://github.com/allenai/vla-evaluation-harness" in urls


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
