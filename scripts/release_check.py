#!/usr/bin/env python3
"""Fail-closed checks for the public repository contents."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

IGNORED_DIRS = {
    ".deps",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".runtime",
    ".venv",
    ".venv-pyroki",
    ".remotion",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "out",
    "runs",
    "site-preview",
}
TEXT_SUFFIXES = {
    "",
    ".cff",
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".vtt",
    ".yaml",
    ".yml",
}


def _files(root: Path):
    for directory, child_dirs, filenames in os.walk(root, topdown=True):
        child_dirs[:] = [
            name
            for name in child_dirs
            if name not in IGNORED_DIRS and not name.endswith(".egg-info")
        ]
        base = Path(directory)
        for filename in filenames:
            if filename == "robohermes.yaml":
                continue
            yield base / filename


def _directories(root: Path):
    for directory, child_dirs, _filenames in os.walk(root, topdown=True):
        child_dirs[:] = [
            name
            for name in child_dirs
            if name not in IGNORED_DIRS and not name.endswith(".egg-info")
        ]
        base = Path(directory)
        for name in child_dirs:
            yield base / name


def _local_markdown_links(text: str) -> list[str]:
    links = []
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
        target = target.split("#", 1)[0]
        if target and "://" not in target and not target.startswith("mailto:"):
            links.append(target)
    return links


def collect_findings(root: Path) -> list[str]:
    root = Path(root).resolve()
    findings: list[str] = []
    required = (
        "README.md",
        "REPRODUCING.md",
        "LICENSE",
        "pyproject.toml",
        "setup.sh",
        "robohermes",
        "configs/default.yaml",
        "evidence/adaptive-pass10-v1/manifest.json",
        "evidence/adaptive-pass10-v1/episodes.jsonl",
        "evidence/publication-v1/experiments.json",
        "docs/EXPERIMENTS_AND_COMPARISON.md",
        "PRESS_KIT_ZH.md",
        "SOCIAL_COPY.md",
        "src/robohermes_libero/static/zh.html",
        "src/robohermes_libero/static/fonts/wqy-microhei.ttc",
        "src/robohermes_libero/static/media/demo/roborsi-demo-zh.mp4",
        "src/robohermes_libero/static/media/demo/roborsi-demo-zh-poster.jpg",
        "src/robohermes_libero/static/media/demo/roborsi-demo-en.vtt",
        "src/robohermes_libero/static/media/demo/roborsi-demo-zh.vtt",
        "src/robohermes_libero/static/media/demo/voiceover/en/intro.mp3",
        "src/robohermes_libero/static/media/demo/voiceover/en/verified-tasks.mp3",
        "src/robohermes_libero/static/media/demo/voiceover/en/adaptive-evolution.mp3",
        "src/robohermes_libero/static/media/demo/voiceover/en/matched-code.mp3",
        "src/robohermes_libero/static/media/demo/voiceover/en/end-slate.mp3",
        "src/robohermes_libero/static/media/demo/voiceover/zh/intro.mp3",
        "src/robohermes_libero/static/media/demo/voiceover/zh/verified-tasks.mp3",
        "src/robohermes_libero/static/media/demo/voiceover/zh/adaptive-evolution.mp3",
        "src/robohermes_libero/static/media/demo/voiceover/zh/matched-code.mp3",
        "src/robohermes_libero/static/media/demo/voiceover/zh/end-slate.mp3",
        "remotion/package.json",
        "remotion/package-lock.json",
        "remotion/voiceover.json",
        "remotion/src/RoborsiDemo.tsx",
    )
    for relative in required:
        if not (root / relative).is_file():
            findings.append(f"missing required file: {relative}")
    for relative in ("setup.sh", "robohermes", "scripts/bootstrap.py"):
        path = root / relative
        if path.is_file() and not os.access(path, os.X_OK):
            findings.append(f"entrypoint is not executable: {relative}")

    forbidden = (
        "/mnt" + "/workspace",
        "/data" + "/yijia",
        "copilot" + "-proxy-local",
        "ANTHROPIC" + "_AUTH_TOKEN",
        "gho_" + "********************************",
    )
    secret_patterns = (
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"gh[opurs]_[A-Za-z0-9]{20,}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    )
    for path in _files(root):
        if path.suffix in {".pyc", ".pyo"}:
            findings.append(f"compiled artifact included: {path.relative_to(root)}")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(root)
        if relative != Path("scripts/release_check.py"):
            for needle in forbidden:
                if needle in text:
                    findings.append(f"private default {needle!r}: {relative}")
            for pattern in secret_patterns:
                if pattern.search(text):
                    findings.append(f"possible secret ({pattern.pattern}): {relative}")
        if path.suffix.lower() == ".md":
            for target in _local_markdown_links(text):
                if not (path.parent / target).resolve().exists():
                    findings.append(f"broken local link {target!r}: {relative}")

    excluded_names = {"pro_long", "opd"}
    for path in _directories(root):
        if path.name.lower() in excluded_names:
            findings.append(f"excluded scope directory included: {path.relative_to(root)}")

    pyproject_path = root / "pyproject.toml"
    license_path = root / "LICENSE"
    pyproject = (
        pyproject_path.read_text(encoding="utf-8") if pyproject_path.is_file() else ""
    )
    license_text = (
        license_path.read_text(encoding="utf-8") if license_path.is_file() else ""
    )
    if 'license = "Apache-2.0"' not in pyproject:
        findings.append("pyproject license is not Apache-2.0")
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        findings.append("LICENSE is not Apache-2.0 text")

    publication_path = root / "evidence/publication-v1/experiments.json"
    if publication_path.is_file():
        try:
            publication = json.loads(publication_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(f"publication evidence is invalid: {type(exc).__name__}: {exc}")
        else:
            if publication.get("schema") != "robohermes.libero_publication.v1":
                findings.append("publication evidence schema mismatch")
            headline = publication.get("headline") or {}
            if (headline.get("solved_tasks"), headline.get("total_tasks")) != (95, 120):
                findings.append("publication headline does not match 95/120")
            media = publication.get("media") or {}
            videos = media.get("videos") or []
            if len(videos) != 6 or len({row.get("task") for row in videos}) != 6:
                findings.append("publication media must contain six unique task videos")
            references = [media.get("hero")]
            for row in videos:
                references.extend((row.get("video"), row.get("poster")))
                if row.get("verdict") != "simulator_success":
                    findings.append(f"publication video lacks simulator success: {row.get('id')}")
                if not row.get("tool_chain"):
                    findings.append(f"publication video lacks tool chain: {row.get('id')}")
            for reference in references:
                if not isinstance(reference, str) or not reference:
                    findings.append("publication media contains an empty reference")
                elif not (root / "src/robohermes_libero/static" / reference).is_file():
                    findings.append(f"publication media is missing: {reference}")

            act = ((publication.get("experiments") or {}).get("act") or {})
            comparison = act.get("before_after") or {}
            before = comparison.get("before") or {}
            if comparison.get("status") != "same_task_same_seed_matched_case":
                findings.append("ACT before/after comparison status mismatch")
            if (comparison.get("task"), comparison.get("seed")) != (
                "libero_spatial_swap/0",
                3,
            ):
                findings.append("ACT before/after task or seed mismatch")
            if before.get("verdict") != "simulator_failure":
                findings.append("ACT before video must retain simulator failure verdict")
            if not before.get("tool_chain") or before["tool_chain"][-1] != {
                "tool": "final_simulator_verdict",
                "ok": False,
                "detail": "final verdict=false",
            }:
                findings.append("ACT before video lacks exact final failure verdict")
            for field in ("video", "poster"):
                reference = before.get(field)
                if not isinstance(reference, str) or not reference:
                    findings.append(f"ACT before video contains an empty {field}")
                elif not (root / "src/robohermes_libero/static" / reference).is_file():
                    findings.append(f"ACT before media is missing: {reference}")

    report_path = root / "docs/EXPERIMENTS_AND_COMPARISON.md"
    if report_path.is_file():
        report = report_path.read_text(encoding="utf-8")
        source_urls = (
            "https://arxiv.org/abs/2603.24060",
            "https://arxiv.org/abs/2607.18060",
            "https://arxiv.org/abs/2608.03924",
            "https://arxiv.org/abs/2606.19980",
            "https://github.com/allenai/vla-evaluation-harness",
        )
        for url in source_urls:
            if url not in report:
                findings.append(f"competitive report is missing source: {url}")
        if "These protocols are not a shared leaderboard." not in report:
            findings.append("competitive report is missing the protocol boundary")

    if not findings:
        sys.path.insert(0, str(root))
        sys.path.insert(0, str(root / "src"))
        try:
            from robohermes_libero.evidence import replay_bundle

            result = replay_bundle(root / "evidence/adaptive-pass10-v1/manifest.json")
            if (result.solved_tasks, result.total_tasks) != (95, 120):
                findings.append(
                    f"reported evidence replay mismatch: {result.solved_tasks}/{result.total_tasks}"
                )
        except Exception as exc:  # noqa: BLE001
            findings.append(f"evidence replay failed: {type(exc).__name__}: {exc}")
    if not findings:
        workspace = os.environ.pop("ROBOHERMES_WORKSPACE", None)
        try:
            from scripts.check_libero_gt_leak import collect_findings as collect_gt_findings

            findings.extend(f"GT isolation: {finding}" for finding in collect_gt_findings())
        except Exception as exc:  # noqa: BLE001
            findings.append(f"GT isolation audit failed: {type(exc).__name__}: {exc}")
        finally:
            if workspace is not None:
                os.environ["ROBOHERMES_WORKSPACE"] = workspace
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings = collect_findings(args.root)
    if findings:
        for finding in findings:
            print(f"FAIL {finding}")
        return 1
    print("PASS public release checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
