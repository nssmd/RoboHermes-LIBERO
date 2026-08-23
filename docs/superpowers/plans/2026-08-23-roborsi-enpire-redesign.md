# roborsi ENPIRE-Exact Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current dashboard-like project page with an ENPIRE-accurate manuscript page branded `roborsi`, while preserving every verified result, video, trace, and deployment contract.

**Architecture:** Keep the static `index.html`/`styles.css`/`app.js` surface and the Python-generated `data.json` contract. Recompose the DOM into an ENPIRE hero plus three-column manuscript, render existing videos as case figures, vendor the two open fonts locally, and retain all dynamic IDs required by the evidence renderer.

**Tech Stack:** Static HTML5, CSS, vanilla JavaScript, Python/pytest, GitHub Pages, local WOFF2 fonts, Chromium CDP.

---

### Task 1: Lock The Corrected ENPIRE Contract

**Files:**
- Modify: `tests/test_dashboard.py`
- Test: `tests/test_dashboard.py`

- [ ] **Step 1: Replace the superseded layout assertion with failing contract tests**

Use assertions equivalent to:

```python
def test_project_page_uses_exact_roborsi_enpire_manuscript() -> None:
    static = Path(__file__).resolve().parents[1] / "src/robohermes_libero/static"
    html = (static / "index.html").read_text(encoding="utf-8")
    css = (static / "styles.css").read_text(encoding="utf-8")

    hero = html[html.index('id="overview"') : html.index("</section>")]
    assert "roborsi: verified robot experience as inspectable code" in html
    assert "RoboHermes |" not in html
    assert "article-hero__wordmark" not in hero
    assert "hero-shade" not in hero
    assert 'class="scroll-cue"' in hero
    assert 'class="article-margin"' in html
    assert 'class="article-sidenote"' in html
    assert "minmax(320px, 1fr)" in css
    assert "min(965px" in css
    assert "width: 264px" in css
    assert 'url("fonts/source-serif-4-latin.woff2")' in css
    assert 'url("fonts/jetbrains-mono-latin.woff2")' in css
    assert "linear-gradient" not in css
    assert "radial-gradient" not in css


def test_static_preview_packages_manuscript_fonts(tmp_path: Path) -> None:
    output = build_static_preview(tmp_path / "site")
    assert (output / "fonts/source-serif-4-latin.woff2").stat().st_size > 10_000
    assert (output / "fonts/jetbrains-mono-latin.woff2").stat().st_size > 10_000
    assert (output / "fonts/FONT-LICENSES.md").is_file()
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
PYTHONPATH=src python -m pytest -q \
  tests/test_dashboard.py::test_project_page_uses_exact_roborsi_enpire_manuscript \
  tests/test_dashboard.py::test_static_preview_packages_manuscript_fonts
```

Expected: failures for the old wordmark/two-column layout and missing fonts.

### Task 2: Vendor The ENPIRE Typography

**Files:**
- Create: `src/robohermes_libero/static/fonts/source-serif-4-latin.woff2`
- Create: `src/robohermes_libero/static/fonts/jetbrains-mono-latin.woff2`
- Create: `src/robohermes_libero/static/fonts/FONT-LICENSES.md`
- Modify: `src/robohermes_libero/static/styles.css`
- Test: `tests/test_dashboard.py`

- [ ] **Step 1: Download the pinned Latin WOFF2 assets**

```bash
mkdir -p src/robohermes_libero/static/fonts
curl -L --fail -o src/robohermes_libero/static/fonts/source-serif-4-latin.woff2 \
  https://fonts.gstatic.com/s/sourceserif4/v14/vEFI2_tTDB4M7-auWDN0ahZJW1gb8tc.woff2
curl -L --fail -o src/robohermes_libero/static/fonts/jetbrains-mono-latin.woff2 \
  https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxDcwg.woff2
```

- [ ] **Step 2: Record font provenance and SIL Open Font License links**

`FONT-LICENSES.md` must identify Source Serif 4 and JetBrains Mono, their
upstream repositories, and that both assets are distributed under SIL OFL
1.1. It must not claim ownership of either font.

- [ ] **Step 3: Add local font faces to the stylesheet**

```css
@font-face {
  font-family: "Source Serif 4";
  src: url("fonts/source-serif-4-latin.woff2") format("woff2");
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
}

@font-face {
  font-family: "JetBrains Mono";
  src: url("fonts/jetbrains-mono-latin.woff2") format("woff2");
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
}
```

- [ ] **Step 4: Run the font packaging test**

Run:

```bash
PYTHONPATH=src python -m pytest -q \
  tests/test_dashboard.py::test_static_preview_packages_manuscript_fonts
```

Expected: PASS.

### Task 3: Recompose The HTML As A Paper

**Files:**
- Modify: `src/robohermes_libero/static/index.html`
- Test: `tests/test_dashboard.py`

- [ ] **Step 1: Replace the hero with real media only**

The hero must have this shape and no wordmark/shade:

```html
<section id="overview" class="article-hero" aria-label="roborsi robot rollout">
  <div class="article-hero__sticky">
    <video class="article-hero__video" autoplay loop muted playsinline preload="auto"
      src="media/hero-libero-short.mp4"></video>
    <a class="scroll-cue" href="#article-content">Scroll to explore</a>
  </div>
</section>
```

- [ ] **Step 2: Build the three-column title/abstract frame**

The article frame must contain `article-outline`, `article-shell`, and
`article-margin`. The title starts with the exact lowercase brand. Use static
fallback values `398/840`, `+16.3 pp`, `95/120`, and `67/130` rather than `--`.

```html
<div class="article-layout">
  <aside class="article-outline">
    <nav aria-label="Contents"><a href="#abstract">Abstract</a></nav>
  </aside>
  <article class="article-shell">
    <header id="article-title" class="article-title-block">
      <p class="article-kicker">PUBLIC RELEASE / 23 AUG 2026</p>
      <h1>roborsi: verified robot experience as inspectable code</h1>
      <nav class="article-links">
        <a href="https://github.com/nssmd/RoboHermes-LIBERO">GitHub</a>
        <a href="#reproduce">Reproduce</a>
      </nav>
    </header>
    <section id="abstract" class="paper-section">
      <h2>Abstract</h2>
      <p>roborsi turns verified robot experience into inspectable code-backed skills.</p>
    </section>
  </article>
  <aside class="article-margin" aria-label="Paper annotations">
    <div class="article-sidenote">
      <strong>Claim boundary</strong>
      <p>Adaptive, strict, matched, and ACT evidence remain separate.</p>
    </div>
  </aside>
</div>
```

- [ ] **Step 3: Preserve every renderer and interaction anchor**

Keep all current IDs consumed by `app.js`: `hero-plus-score`,
`hero-plus-uplift`, `hero-adaptive`, `plus-fixed-score`, `plus-fixed-rate`,
`plus-adaptive-score`, `plus-adaptive-rate`, `plus-uplift-score`,
`plus-uplift-identities`, `plus-token-cost`, `plus-active-wall`,
`plus-attempt-count`, `plus-unmetered`, `plus-stage-grid`, `video-grid`,
`plus-video-grid`, `adaptive-chart`, `strict-chart`, `code-chart`,
`efficiency-grid`, `comparison-body`, `gap-list`, `advantage-list`,
`task-body`, `table-count`, `task-search`, `command-list`, and dialog IDs.

- [ ] **Step 4: Apply the public brand without changing source identity**

Change title metadata, descriptive copy, comparison headings, and footer to
`roborsi`. Keep literal GitHub URLs and package/repository names unchanged.
Version static references as `styles.css?v=20260823` and
`app.js?v=20260823`.

- [ ] **Step 5: Run the focused layout tests and verify remaining failures are CSS-only**

```bash
PYTHONPATH=src python -m pytest -q tests/test_dashboard.py
```

Expected: existing evidence/ordering/media tests pass; exact grid assertions
remain red until Task 4.

### Task 4: Replace The Dashboard CSS With The ENPIRE Manuscript System

**Files:**
- Modify: `src/robohermes_libero/static/styles.css`
- Test: `tests/test_dashboard.py`

- [ ] **Step 1: Define the paper tokens and stable desktop dimensions**

```css
:root {
  --paper: #f6f6ef;
  --figure: #fff;
  --ink: rgba(12, 12, 12, 0.90);
  --ink-soft: rgba(12, 12, 12, 0.68);
  --muted: rgba(12, 12, 12, 0.52);
  --hairline: rgba(12, 12, 12, 0.15);
  --hairline-strong: rgba(12, 12, 12, 0.24);
  --green: #447c56;
  --rust: #996653;
  --blue: #3d6470;
  --serif: "Source Serif 4", Georgia, serif;
  --mono: "JetBrains Mono", ui-monospace, monospace;
}
```

- [ ] **Step 2: Implement the reference hero without decoration**

Use `height: 100svh`, `object-fit: cover`, a 14 px scroll cue at the bottom,
and a 2 px vertical rule. Do not use any CSS gradient, blur, glow, orb, or
vignette.

- [ ] **Step 3: Implement the measured ENPIRE grid**

```css
@media (min-width: 1240px) {
  .article-layout {
    display: grid;
    grid-template-columns:
      minmax(320px, 1fr)
      minmax(0, min(965px, calc(100% - 640px)))
      minmax(320px, 1fr);
    width: min(1720px, 100%);
    margin: 0 auto;
  }
  .article-outline { grid-column: 1; width: 176px; justify-self: end; }
  .article-shell { grid-column: 2; width: min(965px, 100%); }
  .article-margin { grid-column: 3; width: 264px; margin-left: 56px; }
}
```

- [ ] **Step 4: Style manuscript sections, figures, notes, and tables**

Body prose is 19 px/1.6. Title is 48 px/1.06. Headings are 36 px/1.1.
Sections use whitespace and one-pixel rules. Videos, charts, and the
LIBERO-Plus SVG are paper figures with captions. Only dialogs and repeated
task evidence may retain bounded containers; no section is a floating card.

- [ ] **Step 5: Add a graceful narrow layout without changing desktop priority**

Below 1240 px, hide the sticky outline and move margin notes inline. Below
820 px, contain the hero video, reduce prose to 17 px, and keep all text and
controls non-overlapping.

- [ ] **Step 6: Run the focused contract tests and verify GREEN**

```bash
PYTHONPATH=src python -m pytest -q tests/test_dashboard.py
```

Expected: all dashboard tests pass.

### Task 5: Render Videos As ENPIRE Case Figures

**Files:**
- Modify: `src/robohermes_libero/static/app.js`
- Modify: `src/robohermes_libero/static/styles.css`
- Test: `tests/test_dashboard.py`

- [ ] **Step 1: Replace card markup with figure markup**

```javascript
function videoFigures(videos) {
  return videos.map((video, index) => `
    <figure class="case-figure ${index % 2 ? "case-figure--reverse" : ""}">
      <div class="case-media">
        <video autoplay loop muted playsinline preload="metadata"
          poster="${escapeHtml(video.poster)}" src="${escapeHtml(video.video)}"></video>
        <button class="trace-open" type="button" data-video-id="${escapeHtml(video.id)}"
          aria-label="Open evidence for ${escapeHtml(video.title)}">Trace</button>
      </div>
      <figcaption>
        <span>${escapeHtml(video.subtitle)}</span>
        <strong>${escapeHtml(video.title)}</strong>
        <small>${escapeHtml(video.task)} · seed ${video.seed} · ${video.duration_s.toFixed(1)}s</small>
      </figcaption>
    </figure>`).join("");
}
```

- [ ] **Step 2: Keep the existing dialog and exact tool-chain behavior**

`renderVideos()` must still combine six prior videos and four LIBERO-Plus
videos into `state.videos`, attach one click listener per trace button, and
open the same native-success dialog. No arguments, coordinates, or hidden
state are added to public traces.

- [ ] **Step 3: Make data-load failure local and non-destructive**

Add a `#data-status` note. On fetch failure, update only that note and retain
the static abstract and fallback metrics. Do not replace the project abstract
with an error string.

- [ ] **Step 4: Check JavaScript syntax and focused tests**

```bash
node --check src/robohermes_libero/static/app.js
PYTHONPATH=src python -m pytest -q tests/test_dashboard.py
```

Expected: syntax valid and dashboard tests pass.

### Task 6: Full Verification And Desktop Visual QA

**Files:**
- Modify: `docs/assets/dashboard.png`
- Verify: all release files

- [ ] **Step 1: Run automated verification**

```bash
PYTHONPATH=src python -m pytest -q
python -m ruff check src/robohermes_libero tests scripts/release_check.py scripts/plot_libero_plus_final.py
python scripts/release_check.py
node --check src/robohermes_libero/static/app.js
.venv/bin/python -m build
```

Expected: 0 failures, 0 lint findings, release PASS, valid JS, wheel and sdist.

- [ ] **Step 2: Build and serve a fresh static preview**

```bash
PYTHONPATH=src python - <<'PY'
from pathlib import Path
from robohermes_libero.dashboard import build_static_preview
build_static_preview(Path("/tmp/roborsi-enpire-preview"))
PY
python -m http.server 8899 --directory /tmp/roborsi-enpire-preview
```

- [ ] **Step 3: Capture desktop reference views**

Use Chromium at 1440x1000 and 1728x1117. Capture hero, title/abstract,
architecture, simulation, LIBERO-Plus, and later evidence sections. Confirm
zero horizontal overflow, overlap, console errors, failed requests, or blank
media. Confirm all chart canvases/SVGs have non-background pixels.

- [ ] **Step 4: Update the README screenshot**

Replace `docs/assets/dashboard.png` with the verified 1728 px project-page
capture and update its alt text/link to `https://robo-rsi.com/` without
renaming the source package.

### Task 7: Integrate And Publish

**Files:**
- Publish: `main`
- Publish: `gh-pages`
- Preserve: `gh-pages/CNAME`

- [ ] **Step 1: Commit the verified redesign**

```bash
git add src/robohermes_libero/static tests/test_dashboard.py README.md docs/assets/dashboard.png
git commit -m "feat: rebuild project page as roborsi ENPIRE manuscript"
```

- [ ] **Step 2: Merge the feature branch to main after final verification**

Use a non-interactive fast-forward merge and push `main`. Do not rewrite
history or touch unrelated branches.

- [ ] **Step 3: Build the exact static preview into the gh-pages worktree**

Generate the site into the existing `gh-pages` worktree, verify that `CNAME`
still contains `robo-rsi.com`, commit, and push.

- [ ] **Step 4: Verify public deployment**

Check HTML, cache-busted CSS/JS, `data.json`, the LIBERO-Plus SVG, hero video,
and all ten rollout videos. Verify public values remain `95/120`, `261/840`,
`398/840`, and `+137`.

- [ ] **Step 5: Recheck custom-domain HTTPS**

If GitHub's certificate now exists, enable enforced HTTPS and stop the bounded
supervisor after it records success. If DNS caches still block issuance, leave
the supervisor active and report the deployment and certificate states
separately.
