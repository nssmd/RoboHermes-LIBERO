from __future__ import annotations

from pathlib import Path

from PIL import Image

from scripts.plot_evolution_dynamics import render_evolution_dynamics

ROOT = Path(__file__).resolve().parents[1]


def test_render_evolution_dynamics_uses_publication_evidence(tmp_path: Path) -> None:
    outputs = render_evolution_dynamics(
        experiments_path=ROOT / "evidence/publication-v1/experiments.json",
        strict_path=ROOT / "evidence/publication-v1/strict_round_dynamics.json",
        robotwin_path=ROOT / "evidence/publication-v1/robotwin_historical.json",
        output_dir=tmp_path,
    )

    svg = outputs["svg"].read_text(encoding="utf-8")
    assert "Strict Standard-130" in svg
    assert "Pass@k is retry coverage" in svg
    assert "Adaptive LIBERO" in svg
    assert "Historical RoboTwin" in svg
    assert "Matched efficiency" in svg
    image = Image.open(outputs["png"])
    assert image.width >= 3000
    assert image.height >= 1800
