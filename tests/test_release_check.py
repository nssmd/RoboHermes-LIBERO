from __future__ import annotations

from pathlib import Path

from scripts.release_check import collect_findings


def test_release_tree_passes_publication_gate() -> None:
    root = Path(__file__).resolve().parents[1]

    assert collect_findings(root) == []


def test_publication_documents_cover_sources_and_protocol_boundary() -> None:
    root = Path(__file__).resolve().parents[1]
    required = (
        "docs/EXPERIMENTS_AND_COMPARISON.md",
        "PRESS_KIT_ZH.md",
        "SOCIAL_COPY.md",
    )
    for relative in required:
        assert (root / relative).is_file(), relative

    report = (root / required[0]).read_text(encoding="utf-8")
    for url in (
        "https://arxiv.org/abs/2603.24060",
        "https://arxiv.org/abs/2607.18060",
        "https://arxiv.org/abs/2608.03924",
        "https://arxiv.org/abs/2606.19980",
        "https://github.com/allenai/vla-evaluation-harness",
    ):
        assert url in report
    assert "These protocols are not a shared leaderboard." in report
