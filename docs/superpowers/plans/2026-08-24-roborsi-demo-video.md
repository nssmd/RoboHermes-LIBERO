# roborsi Evidence Demo Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate and publish a deterministic 39-second demo that shows nine verified tasks, adaptive solution discovery, and matched Code-on efficiency.

**Architecture:** A standalone Python compositor reads the canonical evidence values and nine existing MP4 assets, streams rendered BGR frames to FFmpeg, and emits one H.264 master plus poster. The existing static preview pipeline packages those outputs, while a manuscript section embeds the demo without changing evidence schemas.

**Tech Stack:** Python 3.10+, OpenCV, Pillow, NumPy, FFmpeg/libx264, pytest, static HTML/CSS, Chromium.

---

### Task 1: Lock The Video Contract With A Failing Smoke Test

**Files:**
- Create: `tests/test_demo_video.py`
- Test: `tests/test_demo_video.py`

- [ ] **Step 1: Write a subprocess smoke-render test**

Run `scripts/build_demo_video.py` at 480 x 270, 6 fps, and duration scale 0.1.
Probe the result with FFprobe and assert H.264, `yuv420p`, exact dimensions, no
audio, and duration between 3.7 and 4.2 seconds. Decode samples from all four
scenes with OpenCV and require nontrivial luminance variance and pairwise scene
difference. Require a nonblank JPEG poster.

- [ ] **Step 2: Write a source-and-caption contract test**

Invoke `--print-manifest` and assert 14 unique source paths, two nine-cell grid
pages whose union contains 13 successes, the same-task same-seed ACT pair, the
adaptive sequence `[32,45,52,66,71,76,81,82,82,83]`, the four matched values,
and all claim-boundary captions.

- [ ] **Step 3: Run the test and verify RED**

```bash
PYTHONPATH=src python -m pytest -q tests/test_demo_video.py
```

Expected: failure because `scripts/build_demo_video.py` does not exist.

### Task 2: Implement The Deterministic Streaming Compositor

**Files:**
- Create: `scripts/build_demo_video.py`
- Test: `tests/test_demo_video.py`

- [ ] **Step 1: Add the canonical storyboard manifest**

Define the 13 success paths, one retained failure path, task/platform labels,
source offsets, scene durations, adaptive points, and matched Code-on values as immutable
module constants. `--print-manifest` serializes this data without rendering.

- [ ] **Step 2: Implement media sampling and frame geometry**

Create a bounded `VideoSampler` that seeks once to each source offset, advances
only when the requested source frame changes, loops at EOF, and returns a
center-cropped BGR frame for a stable rectangle. Fail with the exact missing or
undecodable source path.

- [ ] **Step 3: Implement the four scenes**

Render the rotating 3 x 3 task wall, matched ACT Before/After beside the
separate adaptive curve, code-backed rollout with matched metric bars, and final brand slate. Use the
local Source Serif 4 and JetBrains Mono assets through Pillow. Scale all fixed
geometry from the 1920 x 1080 design coordinate system.

- [ ] **Step 4: Stream frames to FFmpeg and write the poster**

Pipe `bgr24` frames to `libx264` with `-pix_fmt yuv420p`, `-movflags +faststart`,
and no audio stream. Write the poster from a representative 3 x 3 frame with
Pillow/OpenCV JPEG encoding. Surface broken pipes and FFmpeg failures.

- [ ] **Step 5: Run the smoke test and verify GREEN**

```bash
PYTHONPATH=src python -m pytest -q tests/test_demo_video.py
```

Expected: `2 passed` when OpenCV and FFmpeg are available.

### Task 3: Render And Inspect The Production Master

**Files:**
- Create: `src/robohermes_libero/static/media/demo/roborsi-demo.mp4`
- Create: `src/robohermes_libero/static/media/demo/roborsi-demo-poster.jpg`

- [ ] **Step 1: Render 1920 x 1080 at 30 fps**

```bash
python scripts/build_demo_video.py \
  --output src/robohermes_libero/static/media/demo/roborsi-demo.mp4 \
  --poster src/robohermes_libero/static/media/demo/roborsi-demo-poster.jpg
```

- [ ] **Step 2: Verify container and complete decode**

Use FFprobe for duration, dimensions, codec, pixel format, and stream count.
Decode the complete file with `ffmpeg -v error -i ... -f null -` and require a
zero exit code.

- [ ] **Step 3: Inspect a six-frame contact sheet**

Extract frames spanning the grid, adaptive curve, matched panel, and end slate.
Reject blank, clipped, overlapping, misleading, or unreadable frames and adjust
only the compositor if needed.

### Task 4: Embed The Demo In The Manuscript Site

**Files:**
- Modify: `tests/test_dashboard.py`
- Modify: `src/robohermes_libero/static/index.html`
- Modify: `src/robohermes_libero/static/styles.css`

- [ ] **Step 1: Add a failing packaging and markup test**

Require the preview to contain both demo assets, a `#demo` section immediately
after Abstract, one outline link, native video controls, the poster reference,
both claim-boundary captions, a matched Before/After block, and a unified
14-video trace library. Require the
Task evidence and Reproduce sections to be absent and the paper background to
be pure white.

- [ ] **Step 2: Verify RED**

```bash
PYTHONPATH=src python -m pytest -q \
  tests/test_dashboard.py::test_static_preview_packages_evidence_demo
```

Expected: failure because the section is absent.

- [ ] **Step 3: Add the HTML and restrained demo styles**

Insert the section after Abstract, add the outline link, use an unframed
16:9 figure with native controls, add a three-column claim strip, and render all
14 recordings with on-demand controls and Trace actions. Remove the
Task evidence/Reproduce DOM and their dedicated JS/CSS. Bump the CSS and
JavaScript cache query to `20260824f`.

- [ ] **Step 4: Verify GREEN**

Run the focused test, then `tests/test_dashboard.py`; require all to pass.

### Task 5: Complete Release Verification And Desktop QA

**Files:**
- Generated preview only: `/tmp/roborsi-demo-preview`

- [ ] **Step 1: Run the full repository verification**

```bash
PYTHONPATH=src python -m pytest -q
python -m ruff check src/robohermes_libero tests scripts
python scripts/release_check.py
node --check src/robohermes_libero/static/app.js
.venv/bin/python -m build
```

- [ ] **Step 2: Decode every published MP4**

Enumerate `src/robohermes_libero/static/media/**/*.mp4` and completely decode
each file with FFmpeg. Require all files to exit zero.

- [ ] **Step 3: Build and serve a fresh preview**

Call `build_static_preview(Path('/tmp/roborsi-demo-preview'))`, serve it on an
unused localhost port, and open it in Chromium.

- [ ] **Step 4: Perform desktop browser QA**

At 1440 x 1000 and 1728 x 1117, check readyState, duration, poster pixels,
playback advancement, controls, no overflow, and zero request/page/console
errors. Capture the Demo section at 1728 px for release inspection.

### Task 6: Integrate, Publish, And Record Memory

**Files:**
- Publish: `main`
- Publish: `gh-pages`
- Preserve: `gh-pages/CNAME`
- Update: the workspace-level `.memory/log.md` and generated memory state

- [ ] **Step 1: Commit and fast-forward main**

Commit the tested generator, tests, media, and site changes. Fast-forward
`main`, push it, and verify the remote commit.

- [ ] **Step 2: Rebuild the existing gh-pages worktree**

Generate the exact preview into
`/tmp/robohermes-gh-pages-worktree-20260818-r1`, preserve `CNAME`, commit, and
push `gh-pages`.

- [ ] **Step 3: Verify the public domain**

Fetch cache-busted HTML, demo MP4, poster, CSS, JavaScript, and `data.json` from
`robo-rsi.com`. Probe the remote MP4 and confirm the public page references the
new section and assets.

- [ ] **Step 4: Record the verified release**

Run `research-memory ingest --agent codex` if available; otherwise append a
session entry containing source/deployment commits, media properties, tests,
browser QA, public URLs, and remaining external HTTPS state.
