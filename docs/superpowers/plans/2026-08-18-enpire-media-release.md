# RoboHermes ENPIRE-Inspired Media Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish an ENPIRE-inspired RoboHermes project page, verified LIBERO/ACT videos, a protocol-aware competitive report, and Chinese/X launch copy from one sanitized evidence source.

**Architecture:** A canonical publication JSON is packaged beside the existing replay evidence and injected into the dashboard payload without recomputing metrics. The static dashboard recursively packages media and renders an editorial project page with a full-video hero, architecture, video/tool-chain evidence, experiment tracks, comparison matrix, task table, and reproduction commands. Documentation and social copy cite the same values and source URLs.

**Tech Stack:** Python 3.10-3.12, pytest, static HTML/CSS/JavaScript, FFmpeg/FFprobe, Playwright, GitHub Pages.

---

### Task 1: Publication Evidence Contract

**Files:**
- Create: `evidence/publication-v1/experiments.json`
- Modify: `src/robohermes_libero/dashboard.py`
- Modify: `pyproject.toml`
- Test: `tests/test_dashboard.py`

- [ ] **Step 1: Write the failing publication-payload test**

Add assertions that `build_dashboard_payload()["publication"]` contains the
locked adaptive `95/120`, sequential `32 -> 83`, Standard-130 `67/130`, matched
Code-on/off `174/600` versus `129/600`, and ACT one-case scope.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `PYTHONPATH=src pytest tests/test_dashboard.py -q`

Expected: failure because the `publication` key does not exist.

- [ ] **Step 3: Add the canonical JSON and package loader**

Implement a helper that resolves `evidence/publication-v1/experiments.json`
from either a source checkout or packaged resources, loads it with `json`, and
adds it to the dashboard payload. Force-include the directory in the wheel.

- [ ] **Step 4: Verify GREEN and package parity**

Run: `PYTHONPATH=src pytest tests/test_dashboard.py -q`

Expected: all dashboard tests pass and source values exactly match the locked
artifact inventory.

- [ ] **Step 5: Commit**

Run: `git add evidence/publication-v1 pyproject.toml src/robohermes_libero/dashboard.py tests/test_dashboard.py && git commit -m "feat: package publication evidence matrix"`

### Task 2: Verified Media Package

**Files:**
- Create: `src/robohermes_libero/static/media/hero-libero-short.mp4`
- Create: `src/robohermes_libero/static/media/videos/*`
- Create: `src/robohermes_libero/static/media/posters/*`
- Modify: `src/robohermes_libero/dashboard.py`
- Test: `tests/test_dashboard.py`

- [ ] **Step 1: Write the failing recursive-media test**

Require `build_static_preview()` to copy the six publication videos, six
posters, and hero mosaic listed in publication JSON. Assert every referenced
path exists under the preview and no private source path is serialized.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `PYTHONPATH=src pytest tests/test_dashboard.py -q`

Expected: missing media references because only three top-level static files
are currently copied.

- [ ] **Step 3: Import only native-success media**

Copy four healthy 512x512 Standard-130 success clips, one adaptive success
clip, and the ACT matched success. Generate posters from decoded mid-frames.
Generate the 1024x576 hero from the four Standard-130 clips with a 2x2 FFmpeg
stack; do not use historical or long-horizon footage.

- [ ] **Step 4: Implement recursive static copying**

Replace the fixed three-file copy loop with a deterministic recursive copy of
the package static directory, then write generated `data.json` last.

- [ ] **Step 5: Verify media and GREEN**

Run: `PYTHONPATH=src pytest tests/test_dashboard.py -q`

Run FFprobe on every public video, then decode five evenly spaced frames from
each with FFmpeg. Expected: all files report video streams and every decode
command exits zero.

- [ ] **Step 6: Commit**

Run: `git add src/robohermes_libero/static src/robohermes_libero/dashboard.py tests/test_dashboard.py && git commit -m "feat: publish verified rollout media"`

### Task 3: ENPIRE-Inspired Research Page

**Files:**
- Modify: `src/robohermes_libero/static/index.html`
- Modify: `src/robohermes_libero/static/styles.css`
- Modify: `src/robohermes_libero/static/app.js`
- Test: `tests/test_dashboard.py`

- [ ] **Step 1: Write the failing page-contract test**

Assert the HTML contains sections in this order: `architecture`, `simulations`,
`experiments`, `comparison`, `tasks`, `reproduce`. Require the video dialog,
tool-chain target, sticky outline, and explicit adaptive/strict claim labels.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `PYTHONPATH=src pytest tests/test_dashboard.py -q`

Expected: missing sections and modal elements.

- [ ] **Step 3: Implement semantic HTML and editorial styling**

Build the full-bleed hero, article rail, architecture diagram, six-video grid,
evidence-track result bands, protocol comparison table, retained task table,
and reproduction footer. Use fixed desktop constraints, restrained colors,
serif headings, no gradients, and cards only for repeated videos/evidence.

- [ ] **Step 4: Implement data-driven rendering and video dialog**

Render all experimental values and competitor rows from publication JSON.
Open each video in one modal that shows task, seed, claim scope, native verdict,
and ordered tool names/outcomes. Keep existing task filtering and copy buttons.

- [ ] **Step 5: Verify GREEN and JavaScript syntax**

Run: `PYTHONPATH=src pytest tests/test_dashboard.py -q`

Run: `node --check src/robohermes_libero/static/app.js`

Expected: all focused tests and syntax checks pass.

- [ ] **Step 6: Commit**

Run: `git add src/robohermes_libero/static tests/test_dashboard.py && git commit -m "feat: redesign project page around evidence"`

### Task 4: Competitive Report And Launch Copy

**Files:**
- Create: `docs/EXPERIMENTS_AND_COMPARISON.md`
- Create: `PRESS_KIT_ZH.md`
- Create: `SOCIAL_COPY.md`
- Modify: `scripts/release_check.py`
- Test: `tests/test_release_check.py`

- [ ] **Step 1: Write the failing publication-document gate**

Require the three documents and reject a competitive report missing the exact
RoboHarness/OpenETA/ENPIRE/vla-evaluation-harness source URLs or the statement
that incompatible protocols are not a direct leaderboard.

- [ ] **Step 2: Run the release-check test and verify RED**

Run: `PYTHONPATH=src pytest tests/test_release_check.py -q`

Expected: missing required publication documents.

- [ ] **Step 3: Write the experiment and competitive report**

Record the search window `2026-07-18` through `2026-08-18`, distinguish the two
RoboHarness papers and unrelated same-name projects, list current RoboHermes
experiments, compare protocols, and state concrete gaps and advantages without
claiming a direct score win.

- [ ] **Step 4: Write and humanize Chinese/X copy**

Draft a Chinese media article, one-post X copy, a six-post thread, video
captions, and alt text. Remove promotional filler, keep every number tied to a
named experiment, and preserve limitations in the main narrative.

- [ ] **Step 5: Verify GREEN**

Run: `PYTHONPATH=src pytest tests/test_release_check.py -q`

Expected: publication-document and release gates pass.

- [ ] **Step 6: Commit**

Run: `git add docs/EXPERIMENTS_AND_COMPARISON.md PRESS_KIT_ZH.md SOCIAL_COPY.md scripts/release_check.py tests/test_release_check.py && git commit -m "docs: publish competitive analysis and launch copy"`

### Task 5: GitHub Surface And Full Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/assets/dashboard.png`

- [ ] **Step 1: Update the README**

Add the video/project-page entrypoint, separate all five experiment tracks,
link the report and launch kit, and state the main competitive boundary near
the headline result.

- [ ] **Step 2: Build a local preview**

Run: `PYTHONPATH=src ./robohermes dashboard --output site-preview` if supported,
otherwise call `build_static_preview(Path("site-preview"))` from Python.

- [ ] **Step 3: Run desktop Playwright QA**

Serve `site-preview`, capture 1440x1000 and 1728x1117 screenshots, click every
video evidence button, verify modal tool chains, and assert no console errors,
failed requests, overlap, horizontal overflow, or blank video canvases.

- [ ] **Step 4: Replace the README screenshot**

Capture the verified project page at desktop width and store it as
`docs/assets/dashboard.png`.

- [ ] **Step 5: Run the complete release gate**

Run: `PYTHONPATH=src python -m pytest -q`

Run: `python -m ruff check src/robohermes_libero tests scripts/release_check.py scripts/check_libero_gt_leak.py`

Run: `python scripts/release_check.py && node --check src/robohermes_libero/static/app.js && python -m build`

Run a fresh wheel-install replay and static-preview build. Expected: `95/120`,
all tests green, wheel/sdist build, and no release findings.

- [ ] **Step 6: Commit**

Run: `git add README.md docs/assets/dashboard.png && git commit -m "docs: refresh public project surface"`

### Task 6: Publish And Verify Public URLs

**Files:** Git history and generated `gh-pages` branch only.

- [ ] **Step 1: Fast-forward the clean public main branch**

Recheck both worktrees, then fast-forward `main` to the verified feature head
without rewriting unrelated history.

- [ ] **Step 2: Push GitHub main**

Run: `git push origin main`

Expected: non-force push succeeds.

- [ ] **Step 3: Rebuild and publish GitHub Pages**

Build the static preview from the pushed commit and update `gh-pages` using the
repository's existing legacy Pages path because Actions billing remains locked.

- [ ] **Step 4: Verify public deployment**

Require HTTP 200 for the page, data JSON, every video/poster, report links, and
GitHub source links. Repeat desktop Playwright and sample video-pixel checks on
the public URL.

- [ ] **Step 5: Record research memory**

Run: `research-memory ingest --agent codex`, or manually append a verified
session entry if the CLI is unavailable.
