# LIBERO-Plus ENPIRE Results Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the completed 840-identity LIBERO-Plus fixed/adaptive result, cost accounting, scientific figure, and verified rollout media on the existing ENPIRE-inspired project page.

**Architecture:** A sanitized final JSON becomes the only metric source. The dashboard payload packages it, a Matplotlib script renders the result figure from it, and the static page renders an editorial LIBERO-Plus section plus four trace-backed videos. Generated site output is validated locally before replacing `gh-pages`.

**Tech Stack:** Python 3.11, pytest, Matplotlib, static HTML/CSS/JavaScript, FFmpeg, headless Chromium, GitHub Pages.

---

### Task 1: Import The Final Evidence Object

**Files:**
- Modify: `evidence/publication-v1/experiments.json`
- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Write the failing evidence contract test**

Require `publication["experiments"]["libero_plus"]`, final status, an
840-identity fixed and adaptive denominator, exact arithmetic for rates/uplift,
seven category rows, three suite rows, stage totals, GPT-5.6 Sol medium,
JOINT_POSITION, final-simulator-only adjudication, and zero hidden GT.

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=src python -m pytest tests/test_dashboard.py -q`

Expected: FAIL because `libero_plus` is absent.

- [ ] **Step 3: Add the sanitized final object**

Copy only final aggregate and public provenance fields from the completed
remote report. Do not include private paths, prompts, coordinates, predicates,
or raw hidden-state values. Store all rates as numerator/denominator-derived
floats, not rounded source values.

- [ ] **Step 4: Verify GREEN**

Run: `PYTHONPATH=src python -m pytest tests/test_dashboard.py -q`

Expected: PASS.

### Task 2: Generate The Publication Figure

**Files:**
- Create: `scripts/plot_libero_plus_final.py`
- Create: `tests/test_libero_plus_figure.py`
- Create: `src/robohermes_libero/static/media/figures/libero-plus-final.svg`
- Create: `src/robohermes_libero/static/media/figures/libero-plus-final.png`

- [ ] **Step 1: Write the failing plot test**

Load the publication JSON, call `render_libero_plus_figure`, and require both
SVG and PNG outputs, editable SVG text, all seven category labels, all three
suite labels, and no metric literals inside the plotting module.

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=src python -m pytest tests/test_libero_plus_figure.py -q`

Expected: FAIL because the renderer does not exist.

- [ ] **Step 3: Implement the Matplotlib renderer**

Use one large fixed/adaptive comparison, direct-labelled paired category and
suite rows, and a release-contribution strip. Apply editable SVG text, white
background, restrained neutral/green/blue/coral colors, and no chart title that
duplicates the surrounding page heading.

- [ ] **Step 4: Generate and inspect outputs**

Run: `PYTHONPATH=src python scripts/plot_libero_plus_final.py --publication evidence/publication-v1/experiments.json --output-dir src/robohermes_libero/static/media/figures`

Expected: valid SVG and 300-DPI PNG.

- [ ] **Step 5: Verify GREEN**

Run: `PYTHONPATH=src python -m pytest tests/test_libero_plus_figure.py -q`

Expected: PASS.

### Task 3: Package Four Verified Videos And Tool Chains

**Files:**
- Modify: `evidence/publication-v1/experiments.json`
- Create: `src/robohermes_libero/static/media/videos/plus-*.mp4`
- Create: `src/robohermes_libero/static/media/posters/plus-*.jpg`
- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Write the failing media contract test**

Require four distinct task identities spanning four perturbation categories,
native `simulator_success`, one release and seed per video, nonempty sanitized
tool chains, and packaged files larger than 1,000 bytes.

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=src python -m pytest tests/test_dashboard.py -q`

Expected: FAIL because Plus media is absent.

- [ ] **Step 3: Import and sanitize media**

Copy the selected remote success MP4s without altering originals. Generate
midpoint posters. Extract only ordered registered tool names and boolean
outcomes from visible logs; omit arguments and private paths.

- [ ] **Step 4: Decode all media**

Run FFprobe and `ffmpeg -v error -i <video> -f null -` for every imported MP4.
Extract first/middle/final frames and reject blank or corrupted clips.

- [ ] **Step 5: Verify GREEN**

Run: `PYTHONPATH=src python -m pytest tests/test_dashboard.py -q`

Expected: PASS.

### Task 4: Add The ENPIRE Editorial Section

**Files:**
- Modify: `src/robohermes_libero/static/index.html`
- Modify: `src/robohermes_libero/static/styles.css`
- Modify: `src/robohermes_libero/static/app.js`
- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Write the failing page-order and rendering test**

Require `architecture`, `simulations`, `libero-plus`, `experiments`,
`comparison`, `tasks`, and `reproduce` in that order. Require IDs for the Plus
score, stage accounting, figure, category/suite evidence, and Plus video strip.

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=src python -m pytest tests/test_dashboard.py -q`

Expected: FAIL because the section is absent.

- [ ] **Step 3: Implement semantic HTML and data rendering**

Add the Plus outline entry and section. Render final values exclusively from
`data.json`; use the static Matplotlib figure and route Plus videos through the
existing trace dialog. Keep claim boundaries adjacent to the score.

- [ ] **Step 4: Refine the visual system**

Brighten the hero video, strengthen the RoboHermes wordmark, rebalance the hero
result rail, and add ENPIRE-style thin rules, editorial spacing, direct labels,
and a four-video strip. Keep fixed desktop dimensions and avoid gradients,
decorative blobs, and nested cards.

- [ ] **Step 5: Verify GREEN and JavaScript syntax**

Run: `PYTHONPATH=src python -m pytest tests/test_dashboard.py -q`

Run: `node --check src/robohermes_libero/static/app.js`

Expected: PASS.

### Task 5: Build, Inspect, And Deploy

**Files:**
- Modify: `site-preview/**` (generated)
- Modify: `docs/assets/dashboard.png`
- Modify: `README.md`

- [ ] **Step 1: Build the static preview**

Run: `PYTHONPATH=src ./robohermes dashboard --output site-preview`

Expected: complete static page, data, figures, and media.

- [ ] **Step 2: Run the full release gate**

Run: `PYTHONPATH=src python -m pytest -q`

Run: `python -m ruff check src/robohermes_libero tests scripts`

Run: `node --check src/robohermes_libero/static/app.js`

Run: `python scripts/release_check.py && python -m build`

Expected: all commands pass.

- [ ] **Step 3: Run desktop Chromium QA**

Serve `site-preview` and inspect 1440x1000 and 1728x1117. Assert no console
errors, failed requests, horizontal overflow, text overlap, blank figure/video,
or broken trace dialog. Capture the verified project screenshot.

- [ ] **Step 4: Commit and push source**

Commit final evidence, plotting code, generated figure, media, page source,
tests, README, and screenshot to the feature branch; fast-forward `main` only
after all gates pass.

- [ ] **Step 5: Publish and verify GitHub Pages**

Replace `gh-pages` with the verified generated preview, push, then check the
public HTML for the exact final Plus result. Verify every new figure and MP4
returns HTTP 200/206 and the public desktop page remains error-free.
