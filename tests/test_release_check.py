from __future__ import annotations

from pathlib import Path

from scripts.release_check import collect_findings


def test_release_tree_passes_publication_gate() -> None:
    root = Path(__file__).resolve().parents[1]

    assert collect_findings(root) == []
