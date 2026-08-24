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


def test_dashboard_includes_strict_dynamics_and_historical_robotwin() -> None:
    experiments = build_dashboard_payload()["publication"]["experiments"]
    strict = experiments["strict_standard130"]
    dynamics = strict["round_dynamics"]

    assert dynamics["scheduled_tasks"] == [130, 107, 95, 87, 81, 74, 70, 69, 67, 66]
    assert dynamics["median_total_tokens"] == [
        3_688_439.0,
        3_856_719.0,
        2_877_367.0,
        2_059_593.0,
        2_609_440.0,
        1_944_753.0,
        1_973_671.5,
        2_831_001.0,
        2_486_296.0,
        2_652_550.0,
    ]
    assert dynamics["median_elapsed_s"] == [
        830.836,
        870.264,
        953.839,
        943.92,
        866.945,
        816.9045,
        822.2785,
        944.749,
        939.461,
        960.94,
    ]
    assert dynamics["claim_scope"] == "descriptive_residual_rounds_not_evolution"
    assert dynamics["first5_to_last5_median_change"]["tokens"] == -0.13591279805461032
    assert dynamics["first5_to_last5_median_change"]["wall"] == 0.07951265363154159

    robotwin = experiments["robotwin_historical"]
    assert robotwin["status"] == "historical_audited_summary"
    assert robotwin["tasks"] == 50
    assert robotwin["pure_engineer_solved"] == 9
    assert robotwin["three_role_solved"] == 36
    assert robotwin["successful_episodes"] == 104
    assert robotwin["verdict_episodes"] == 422
    assert robotwin["per_episode_success_rate"] == 104 / 422
    assert robotwin["elapsed_hours"] == [
        0.0,
        1.127,
        1.792,
        3.799,
        17.642,
        18.791,
        25.086,
        38.622,
        62.85,
        87.26,
    ]
    assert robotwin["solved_over_time"] == [17, 19, 20, 21, 25, 26, 29, 34, 33, 36]
    assert robotwin["parallel_overlap_fraction"] == 0.87
    assert robotwin["claim_scope"] == "historical_parallel_solution_discovery_not_fixed_policy"
    assert robotwin["provenance"]["full_episode_ledger_in_public_repo"] is False
    assert len(robotwin["media"]["videos"]) == 3
    assert {row["verdict"] for row in robotwin["media"]["videos"]} == {
        "simulator_predicate_success"
    }
    assert {row["trace_scope"] for row in robotwin["media"]["videos"]} == {
        "final_verdict_only"
    }


def test_static_preview_packages_robotwin_media_and_dynamics_figure(tmp_path: Path) -> None:
    output = build_static_preview(tmp_path / "site")
    robotwin = build_dashboard_payload()["publication"]["experiments"]["robotwin_historical"]

    figure_references = (
        "media/figures/evolution-dynamics.svg",
        "media/figures/evolution-dynamics.png",
    )
    for reference in figure_references:
        path = output / reference
        assert path.is_file(), reference
        assert path.stat().st_size > 10_000
    for video in robotwin["media"]["videos"]:
        for field in ("video", "poster"):
            path = output / video[field]
            assert path.is_file(), path
            assert path.stat().st_size > 3_000

    html = (output / "index.html").read_text(encoding="utf-8")
    assert 'id="dynamics"' in html
    assert 'id="robotwin"' in html
    assert 'id="robotwin-video-grid"' in html
    assert "Pass@k is not an evolution curve" in html


def test_static_preview_packages_evidence_demo(tmp_path: Path) -> None:
    output = build_static_preview(tmp_path / "site")
    video = output / "media/demo/roborsi-demo.mp4"
    poster = output / "media/demo/roborsi-demo-poster.jpg"

    assert video.is_file()
    assert video.stat().st_size > 1_000_000
    assert poster.is_file()
    assert poster.stat().st_size > 50_000

    html = (output / "index.html").read_text(encoding="utf-8")
    abstract_start = html.index('<section id="abstract"')
    abstract_end = html.index("</section>", abstract_start)
    demo_start = html.index('<section id="demo"')
    architecture_start = html.index('<section id="architecture"')
    assert abstract_end < demo_start < architecture_start
    assert 'href="#demo">Demo</a>' in html
    assert 'src="media/demo/roborsi-demo.mp4"' in html
    assert 'poster="media/demo/roborsi-demo-poster.jpg"' in html
    demo_markup = html[demo_start:architecture_start]
    assert "controls" in demo_markup
    assert 'id="demo-video-grid"' in demo_markup
    assert "Cross-release adaptive development coverage; not fixed-policy Pass@10." in html
    assert "Matched Code-on/off panels. Video illustrates code-backed execution." in html
    assert "styles.css?v=20260824e" in html
    assert "app.js?v=20260824e" in html


def test_demo_library_unifies_all_recordings_and_available_traces() -> None:
    static = Path(__file__).resolve().parents[1] / "src/robohermes_libero/static"
    payload = build_dashboard_payload()["publication"]
    videos = [
        *payload["media"]["videos"],
        *payload["experiments"]["libero_plus"]["media"]["videos"],
        *payload["experiments"]["robotwin_historical"]["media"]["videos"],
    ]
    html = (static / "index.html").read_text(encoding="utf-8")
    javascript = (static / "app.js").read_text(encoding="utf-8")

    assert len(videos) == 13
    assert len({row["id"] for row in videos}) == 13
    assert all(row["tool_chain"] for row in videos)
    assert all(row["tool_chain"][-1]["tool"] == "final_simulator_verdict" for row in videos)
    assert 'id="demo-video-grid"' in html
    assert (
        'getElementById("demo-video-grid").innerHTML = '
        'videoFigures(videos, {controls: true})'
    ) in javascript
    assert 'id="tasks"' not in html
    assert 'id="reproduce"' not in html
    assert 'href="#tasks"' not in html
    assert 'href="#reproduce"' not in html


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

    sections = [
        "architecture",
        "simulations",
        "libero-plus",
        "experiments",
        "comparison",
    ]
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


def test_project_page_exposes_enpire_style_libero_plus_evidence_surface() -> None:
    static = Path(__file__).resolve().parents[1] / "src/robohermes_libero/static"
    html = (static / "index.html").read_text(encoding="utf-8")

    for element_id in (
        "hero-plus-score",
        "plus-fixed-score",
        "plus-adaptive-score",
        "plus-uplift-score",
        "plus-stage-grid",
        "plus-video-grid",
    ):
        assert f'id="{element_id}"' in html
    assert "media/figures/libero-plus-final.svg" in html
    assert "840 stratified perturbation identities" in html
    assert "Adaptive Pass@2" in html


def test_project_page_uses_exact_roborsi_enpire_manuscript() -> None:
    static = Path(__file__).resolve().parents[1] / "src/robohermes_libero/static"
    html = (static / "index.html").read_text(encoding="utf-8")
    css = (static / "styles.css").read_text(encoding="utf-8")

    hero = html[html.index('id="overview"') : html.index("</section>")]
    assert "roborsi: verified robot experience as inspectable code" in html
    assert "RoboHermes |" not in html
    assert "article-hero__wordmark" not in hero
    assert "hero-shade" not in hero
    assert 'class="scroll-cue"' in hero
    assert 'class="article-margin"' in html
    assert 'class="article-sidenote"' in html
    assert html.index('id="overview"') < html.index('id="article-content"')
    assert html.index('id="article-title"') < html.index('id="architecture"')
    assert "minmax(320px, 1fr)" in css
    assert "min(965px" in css
    assert "width: 264px" in css
    assert 'url("fonts/source-serif-4-latin.woff2")' in css
    assert 'url("fonts/jetbrains-mono-latin.woff2")' in css
    assert "linear-gradient" not in css
    assert "radial-gradient" not in css
    assert "--paper: #ffffff;" in css
    assert "#f6f6ef" not in css


def test_static_preview_packages_manuscript_fonts(tmp_path: Path) -> None:
    output = build_static_preview(tmp_path / "site")

    assert (output / "fonts/source-serif-4-latin.woff2").stat().st_size > 10_000
    assert (output / "fonts/jetbrains-mono-latin.woff2").stat().st_size > 10_000
    assert (output / "fonts/FONT-LICENSES.md").is_file()


def test_static_preview_preserves_custom_domain(tmp_path: Path) -> None:
    output = build_static_preview(tmp_path / "site")

    assert (output / "CNAME").read_text(encoding="utf-8") == "robo-rsi.com\n"


def test_project_page_renders_rollouts_as_case_figures() -> None:
    static = Path(__file__).resolve().parents[1] / "src/robohermes_libero/static"
    html = (static / "index.html").read_text(encoding="utf-8")
    javascript = (static / "app.js").read_text(encoding="utf-8")

    assert 'id="data-status"' in html
    assert "function videoFigures(videos, {controls = false} = {})" in javascript
    assert 'class="case-figure ' in javascript
    assert 'class="video-card"' not in javascript
    assert 'document.getElementById("data-status")' in javascript
    assert 'document.querySelector(".project-intro' not in javascript
