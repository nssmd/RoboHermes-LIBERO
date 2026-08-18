"""Static desktop dashboard built from the canonical replay result."""

from __future__ import annotations

import importlib.resources
import json
import shutil
import tempfile
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from robohermes_libero.catalog import SHORT_TASK_CATALOG, suite_for
from robohermes_libero.evidence import default_manifest_path, replay_bundle


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_manifest() -> Path:
    return default_manifest_path()


def _publication_path() -> Path:
    source_path = _repo_root() / "evidence" / "publication-v1" / "experiments.json"
    if source_path.is_file():
        return source_path
    packaged = importlib.resources.files("robohermes_libero").joinpath(
        "evidence/publication-v1/experiments.json"
    )
    return Path(str(packaged))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_dashboard_payload(result_path: Path | None = None) -> dict:
    manifest_path = _default_manifest()
    if result_path is None or result_path.name == "manifest.json":
        if result_path is not None:
            manifest_path = result_path.resolve()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result = replay_bundle(manifest_path).to_dict()
        rows = _read_jsonl(manifest_path.parent / manifest["episodes"])
        successes = {row["task_key"]: row for row in rows if row["category"] == "task_success"}
        tasks = []
        for task in manifest["task_catalog"]:
            evidence = successes.get(task)
            source = dict(evidence.get("source") or {}) if evidence else {}
            tasks.append(
                {
                    "task_key": task,
                    "suite": suite_for(task),
                    "solved": evidence is not None,
                    "seed": evidence.get("seed") if evidence else None,
                    "release_id": evidence.get("release_id") if evidence else None,
                    "total_tokens": evidence.get("total_tokens") if evidence else None,
                    "elapsed_s": evidence.get("elapsed_s") if evidence else None,
                    "run_id": source.get("run_id"),
                    "video": source.get("video"),
                    "trajectory": source.get("trajectory"),
                }
            )
        result.update(
            {
                "label": manifest.get("label", "Adaptive task-level Pass@10"),
                "claim_boundary": manifest.get("claim_boundary", ""),
                "usage_scope": manifest.get("usage_scope", ""),
            }
        )
    else:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        solved = set(result.get("solved_task_keys") or ())
        tasks = [
            {
                "task_key": task,
                "suite": suite_for(task),
                "solved": task in solved,
                "seed": None,
                "release_id": None,
                "total_tokens": None,
                "elapsed_s": None,
                "run_id": None,
                "video": None,
                "trajectory": None,
            }
            for task in SHORT_TASK_CATALOG
        ]
        result.setdefault("label", result.get("metric", "LIBERO short evaluation"))
        result.setdefault("claim_boundary", result.get("claim_scope", ""))
        result.setdefault("usage_scope", (result.get("efficiency") or {}).get("scope", ""))
    return {
        "schema": "robohermes.libero_dashboard.v1",
        "product": "RoboHermes",
        "benchmark": "LIBERO Short 120",
        "result": result,
        "publication": json.loads(_publication_path().read_text(encoding="utf-8")),
        "tasks": tasks,
        "commands": {
            "setup": "./setup.sh",
            "configure": "./robohermes configure",
            "replay": (
                "./robohermes results replay --manifest "
                "evidence/adaptive-pass10-v1/manifest.json"
            ),
            "evaluate": "./robohermes eval libero-short --mode adaptive",
        },
    }


def build_static_preview(output: Path, result_path: Path | None = None) -> Path:
    destination = Path(output).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    static = Path(str(importlib.resources.files("robohermes_libero").joinpath("static")))
    for name in ("index.html", "styles.css", "app.js"):
        shutil.copy2(static / name, destination / name)
    (destination / "data.json").write_text(
        json.dumps(build_dashboard_payload(result_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def serve_dashboard(
    *,
    result_path: Path | None,
    host: str,
    port: int,
    open_browser: bool,
) -> None:
    with tempfile.TemporaryDirectory(prefix="robohermes-dashboard-") as temporary:
        site = build_static_preview(Path(temporary), result_path=result_path)
        handler = partial(SimpleHTTPRequestHandler, directory=str(site))
        server = ThreadingHTTPServer((host, port), handler)
        url = f"http://{host}:{server.server_port}/"
        print(f"RoboHermes dashboard: {url}", flush=True)
        if open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
