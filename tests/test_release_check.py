from __future__ import annotations

import os
import subprocess
import sys
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


def test_release_check_cli_runs_without_pythonpath() -> None:
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)

    completed = subprocess.run(
        [sys.executable, "scripts/release_check.py"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PASS public release checks" in completed.stdout
