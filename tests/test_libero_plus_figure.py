from __future__ import annotations

from pathlib import Path

from scripts.plot_libero_plus_final import render_libero_plus_figure


def test_libero_plus_figure_is_data_driven_and_exports_editable_svg(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    evidence = root / "evidence/publication-v1/libero_plus_final.json"

    outputs = render_libero_plus_figure(evidence, tmp_path)

    assert outputs == {
        "svg": tmp_path / "libero-plus-final.svg",
        "png": tmp_path / "libero-plus-final.png",
    }
    assert outputs["svg"].stat().st_size > 20_000
    assert outputs["png"].stat().st_size > 100_000

    svg = outputs["svg"].read_text(encoding="utf-8")
    assert "<text" in svg
    for label in (
        "Background Textures",
        "Camera Viewpoints",
        "Language Instructions",
        "Light Conditions",
        "Objects Layout",
        "Robot Initial States",
        "Sensor Noise",
        "Spatial",
        "Object",
        "Goal",
        "Fixed",
        "Adaptive",
    ):
        assert label in svg

    source = (root / "scripts/plot_libero_plus_final.py").read_text(encoding="utf-8")
    for metric_literal in ("1_473_552_635", "398 / 840", "261 / 840"):
        assert metric_literal not in source
