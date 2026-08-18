# RoboHermes LIBERO Open-Source Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a clean repository that configures, replays, evaluates, and visualizes RoboHermes on all 120 LIBERO short tasks.

**Architecture:** A release package owns configuration, evidence aggregation, process launch, integrity checks, and the dashboard. The production runtime is exported through an explicit allowlist and receives machine-specific values through one validated YAML file. Reported adaptive evidence, new adaptive campaigns, and fixed-release evaluations remain separate result tracks.

**Tech Stack:** Python 3.10-3.12, Typer, Rich, Pydantic, PyYAML, OpenAI Responses API, LIBERO/robosuite/MuJoCo, pytest, static HTML/CSS/JavaScript.

---

### Task 1: Configuration Contract

**Files:** `src/robohermes_libero/config.py`, `configs/default.yaml`, `tests/test_config.py`

- [ ] Test GPT Responses defaults, ordered seeds, validation, and secret-free serialization.
- [ ] Verify RED with `pytest tests/test_config.py -q`.
- [ ] Implement typed loading, environment export, and redacted display.
- [ ] Verify focused and full tests.

### Task 2: Evidence Replay

**Files:** `src/robohermes_libero/evidence.py`, `src/robohermes_libero/catalog.py`, `evidence/adaptive-pass10-v1/*`, `tests/test_evidence.py`

- [ ] Test task-level deduplication, infrastructure exclusion, conflict rejection, breakdowns, and claim scope.
- [ ] Verify RED, implement one aggregation path, then verify GREEN.
- [ ] Normalize retained simulator-success rows and reproduce the locked metric without private paths.

### Task 3: CLI And One-Command Configuration

**Files:** `src/robohermes_libero/cli.py`, `src/robohermes_libero/doctor.py`, `robohermes`, `tests/test_cli.py`

- [ ] Test `configure`, offline doctor, replay, dry-run evaluation, and dashboard help.
- [ ] Verify RED, implement actionable commands, and verify in a temporary home.

### Task 4: Short Evaluation Launcher

**Files:** `src/robohermes_libero/protocol.py`, `launcher.py`, `records.py`, `tests/test_protocol.py`, `tests/test_launcher.py`

- [ ] Test the exact 120-task catalog, residual schedules, immutable manifests, success protection, and denominator rules.
- [ ] Implement fixed and adaptive schemas plus dry-run manifests.
- [ ] Verify mocked workers before a simulator smoke.

### Task 5: Production Runtime Export

**Files:** `src/robohermes/embodied/**`, `src/robohermes/agents/**`, `tests/runtime/**`

- [ ] Export only the LIBERO-short transitive dependency closure.
- [ ] Replace internal defaults and remove unused provider/backend branches.
- [ ] Preserve post-hoc adjudication, artifact retention, efficiency fields, and proposal overlays.
- [ ] Run source tests and one mocked episode.

### Task 6: Setup And Service Management

**Files:** `setup.sh`, `scripts/bootstrap.py`, `scripts/start_services.py`, `.env.example`, `tests/test_bootstrap.py`

- [ ] Test pinned metadata, command construction, idempotence, and core-only CI mode.
- [ ] Implement environment creation, LIBERO checkout, install, config, and doctor.
- [ ] Verify a clean core install and optional GPU-service diagnostics.

### Task 7: Desktop Results Dashboard

**Files:** `src/robohermes_libero/dashboard.py`, `web/*`, `tests/test_dashboard.py`

- [ ] Test result JSON, all task rows, claim labels, and asset hygiene.
- [ ] Implement a stable desktop research console.
- [ ] Validate by browser screenshot plus console/network checks.

### Task 8: Documentation And Release Gates

**Files:** `README.md`, `REPRODUCING.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CITATION.cff`, `.github/workflows/ci.yml`, `scripts/release_check.py`, `tests/test_release_hygiene.py`

- [ ] Document setup, three result tracks, resource expectations, outputs, troubleshooting, and claim boundaries.
- [ ] Scan secrets, private paths, excluded scope, hidden truth, links, package metadata, and license consistency.
- [ ] Run clean install, tests, lint, build, CLI smoke, replay, dashboard, and release checks.
- [ ] Create the public GitHub repository only after every gate passes.
