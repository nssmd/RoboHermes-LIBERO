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


def test_dashboard_includes_final_libero_plus_adaptive_result() -> None:
    plus = build_dashboard_payload()["publication"]["experiments"]["libero_plus"]

    assert plus["schema"] == "robohermes.libero_plus_adaptive_final.v1"
    assert plus["status"] == "final"
    assert plus["panel"] == {
        "identities": 840,
        "categories": 7,
        "suites": 3,
        "seed": 0,
        "source_commit": "4976dc30028e805ff8094b55501d532c48fec182",
    }
    assert plus["fixed"]["success"] == 261
    assert plus["fixed"]["failure"] == 579
    assert plus["fixed"]["rate"] == 261 / 840
    assert plus["adaptive"]["success"] == 398
    assert plus["adaptive"]["failure"] == 442
    assert plus["adaptive"]["rate"] == 398 / 840
    assert plus["uplift"]["successes"] == 137
    assert plus["uplift"]["percentage_points"] == 100 * 137 / 840
    assert [row["new_successes"] for row in plus["stages"]] == [15, 104, 6, 12]
    assert plus["adaptive"]["efficiency"]["total_tokens"] == 1_473_552_635
    assert plus["adaptive"]["efficiency"]["unmetered_vlm_calls"] == 0

    assert [row["name"] for row in plus["by_category"]] == [
        "Background Textures",
        "Camera Viewpoints",
        "Language Instructions",
        "Light Conditions",
        "Objects Layout",
        "Robot Initial States",
        "Sensor Noise",
    ]
    assert [row["total"] for row in plus["by_category"]] == [120] * 7
    assert [row["adaptive_success"] for row in plus["by_category"]] == [
        67,
        54,
        70,
        65,
        52,
        66,
        24,
    ]
    assert [row["name"] for row in plus["by_suite"]] == [
        "libero_spatial",
        "libero_object",
        "libero_goal",
    ]
    assert [row["adaptive_success"] for row in plus["by_suite"]] == [140, 169, 89]
    assert len(plus["fixed_success_task_keys"]) == 261
    assert len(plus["adaptive_success_task_keys"]) == 398
    assert set(plus["fixed_success_task_keys"]) <= set(plus["adaptive_success_task_keys"])
    assert plus["integrity"] == {
        "adaptive_pass2_infrastructure_records": 0,
        "adaptive_pass2_terminal_identities": 68,
        "check_task_visible": False,
        "checkpoint_or_policy": False,
        "completion_latch": False,
        "controller": "JOINT_POSITION",
        "final_simulator_verdict_only": True,
        "fixed_terminal_identities": 840,
        "hidden_ground_truth_visible": False,
        "osc": False,
        "reasoning_effort": "medium",
        "requested_model": "responses/gpt-5.6-sol",
        "served_models": ["gpt-5.6-sol"],
        "unmetered_vlm_calls": 0,
    }


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
    names = {path.name for path in output.iterdir()}
    assert expected <= names
    assert "media" in names
    data = json.loads((output / "data.json").read_text(encoding="utf-8"))
    assert data["result"]["rate"] == 95 / 120
    combined = "\n".join(
        (output / name).read_text(encoding="utf-8")
        for name in ("index.html", "styles.css", "app.js", "data.json")
    )
    assert "/mnt" + "/workspace" not in combined
    assert "/data" + "/yijia" not in combined
    assert "Adaptive task-level Pass@10" in combined
    assert 'id="architecture"' in combined
    assert "Host-only adjudicator" in combined


def test_static_preview_packages_verified_publication_media(tmp_path: Path) -> None:
    output = build_static_preview(tmp_path / "site")
    media = build_dashboard_payload()["publication"]["media"]

    assert media["hero"] == "media/hero-libero-short.mp4"
    assert len(media["videos"]) == 6
    assert len({video["task"] for video in media["videos"]}) == 6
    assert {video["verdict"] for video in media["videos"]} == {"simulator_success"}
    assert all(video["tool_chain"] for video in media["videos"])

    references = [media["hero"]]
    for video in media["videos"]:
        references.extend((video["video"], video["poster"]))
    for reference in references:
        path = output / reference
        assert path.is_file(), reference
        assert path.stat().st_size > 1_000, reference

    payload_text = (output / "data.json").read_text(encoding="utf-8")
    assert "/mnt" + "/workspace" not in payload_text
    assert "/data" + "/yijia" not in payload_text


def test_static_preview_packages_four_libero_plus_success_videos(tmp_path: Path) -> None:
    output = build_static_preview(tmp_path / "site")
    plus = build_dashboard_payload()["publication"]["experiments"]["libero_plus"]
    videos = plus["media"]["videos"]

    assert len(videos) == 4
    assert len({video["task"] for video in videos}) == 4
    assert {video["perturbation"] for video in videos} == {
        "Camera Viewpoints",
        "Light Conditions",
        "Objects Layout",
        "Robot Initial States",
    }
    assert {video["verdict"] for video in videos} == {"simulator_success"}
    assert {video["experiment"] for video in videos} == {"libero_plus"}
    assert all(video["tool_chain"] for video in videos)
    assert all(
        video["tool_chain"][-1]
        == {"tool": "final_simulator_verdict", "ok": True}
        for video in videos
    )

    for video in videos:
        for field in ("video", "poster"):
            path = output / video[field]
            assert path.is_file(), path
            assert path.stat().st_size > 1_000, path


def test_project_page_orders_evidence_sections_and_exposes_video_trace_dialog() -> None:
    static = Path(__file__).resolve().parents[1] / "src/robohermes_libero/static"
    html = (static / "index.html").read_text(encoding="utf-8")

    sections = ["architecture", "simulations", "experiments", "comparison", "tasks", "reproduce"]
    offsets = [html.index(f'id="{section}"') for section in sections]
    assert offsets == sorted(offsets)

    assert 'class="article-outline"' in html
    assert 'id="video-dialog"' in html
    assert 'id="video-tool-chain"' in html
    assert 'id="video-grid"' in html
    assert 'id="comparison-body"' in html
    assert "Adaptive development coverage" in html
    assert "Strict Standard-130" in html
    assert "Protocols differ; this is not a shared leaderboard." in html
