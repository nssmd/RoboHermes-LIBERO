# roborsi ENPIRE-Exact Project Page Design

## Status

Approved direction: structural ENPIRE recreation in the existing static
RoboHermes-LIBERO website, with the public brand changed to lowercase
`roborsi`.

This specification supersedes the earlier "ENPIRE-inspired" interpretation.
That version copied only a full-screen video, serif type, and a left outline.
It incorrectly added a giant hero wordmark, retained a dashboard-like card
system, omitted ENPIRE's right margin notes, and used generic Georgia/sans
typography. Those choices are explicitly rejected here.

## Goals

1. Recreate ENPIRE's visual hierarchy, density, rhythm, and paper-page
   composition without copying its text, code, figures, or robot assets.
2. Make `roborsi` the exact public-facing brand in the page title, metadata,
   hero accessibility label, article title, and footer.
3. Preserve every verified RoboHermes LIBERO result, figure, rollout video,
   tool trace, source link, and claim boundary without changing any value.
4. Keep the existing static HTML/CSS/JavaScript and evidence-generated
   `data.json` pipeline so GitHub Pages and `robo-rsi.com` remain reproducible.
5. Remove visual patterns that make the page look template- or AI-generated:
   oversized text over media, gradients, decorative blobs, floating section
   cards, metric-card walls, pill-heavy UI, and repetitive boxed components.

## Non-Goals

- No experiment reruns, metric recomputation, evidence edits, or media
  replacement.
- No OPD or long-horizon inspection or publication changes.
- No package, Python namespace, repository, or CLI rename in this release.
  The website brand is `roborsi`; source compatibility remains unchanged.
- No invented authors, affiliations, venue, acceptance status, awards, or
  citations. The title block uses only verified project metadata.
- No migration to Next.js, React, Tailwind, or a new hosting provider.

## Reference Contract

The implementation uses the captured ENPIRE desktop reference and its visible
design grammar as the acceptance reference:

- a full-viewport real robot video with no overlaid product wordmark;
- only a restrained bottom-center "Scroll to explore" cue on the hero;
- a warm near-white paper canvas after the hero;
- Source Serif 4 for display and prose, JetBrains Mono for technical labels;
- a three-column article frame: sticky contents, central manuscript, and
  narrow right-hand annotations;
- compact paper title, release metadata, resource links, and Abstract before
  the method sections;
- full-width figures, captions, and side notes instead of dashboard panels;
- sparse muted green, rust, and blue accents with charcoal body text;
- thin rules, square media, and minimal radii; no decorative background.

The implementation may independently reproduce these visual principles. It
must not copy ENPIRE's source code, prose, figures, logos, or media files.

## Visual System

### Background And Colour

The hero background is the real RoboRSI rollout video itself. It receives only
a minimal contrast treatment needed for the scroll cue; there is no gradient,
blur, vignette, generated texture, or dark colour wash.

The article uses ENPIRE's `#f6f6ef` near-white paper base rather than the
current cream dashboard composition. Figure wells use clean white, while
margin notes use a slightly cooler neutral. Charcoal is the default text
colour. Muted green, rust, and blue are reserved for links, evidence status,
and figure accents.
No page-sized monochrome beige field, coloured section band, orb, glow, or
floating decorative layer is allowed.

### Typography

- Display/prose: locally hosted Source Serif 4 with an explicit open-font
  licence notice and a Georgia fallback.
- Technical labels and trace metadata: locally hosted JetBrains Mono with a
  monospace fallback.
- Body prose is 19 px with a manuscript-like 1.6 line height.
- Section headings are compact manuscript headings, not hero-scale panel
  labels.
- Letter spacing remains zero except restrained uppercase metadata labels.

### Geometry

The desktop manuscript follows ENPIRE's measured grid. Above 1240 px, the
layout is at most 1720 px wide with two `minmax(320px, 1fr)` side zones and a
central manuscript capped at 965 px. The left zone contains a 176 px sticky
outline. Right margin notes are 264 px wide and begin 56 px beyond the central
manuscript. This yields an 800 px manuscript at 1440 px and a 965 px
manuscript at 1728 px, matching the reference's responsive proportions.

Sections are unframed and separated by whitespace or one-pixel rules. Cards
are used only for genuinely repeated interactive media items when a figure
layout cannot carry the interaction. Nested cards are prohibited.

## Page Structure

### 1. Video Hero

- One real simulator rollout fills the first viewport.
- No `roborsi`, score, headline, link bar, card, or dark overlay appears over
  the video.
- A small bottom-centre scroll cue and vertical hairline are the only visible
  UI.
- The next paper section begins immediately after the viewport.

### 2. Paper Title And Abstract

The paper begins with the exact public brand in the title:

> roborsi: verified robot experience as inspectable code

The title block contains the verified project release date/status, GitHub,
evidence, and reproduction links. It does not fabricate an author list.
Headline values appear as restrained inline facts after the abstract, not as
four dashboard cards.

### 3. Architecture

Architecture remains first. Replace the current Planner/Engineer/Reviewer
boxes with one manuscript figure that explains visible context, code-backed
skills, action execution, adaptive promotion, and the host-only simulator
verdict. Put the trust-boundary explanation in a right margin note.

### 4. Simulation Evidence

Present rollout evidence as ENPIRE-style case figures rather than a uniform
three-column card grid. Each task keeps exactly one representative video. A
large primary frame, compact task/seed/release caption, and adjacent trace
annotation lead to the existing full tool-chain dialog.

All ten currently published task videos remain available. No video, poster,
trace, or native-success verdict is removed.

### 5. Experimental Results

Each evidence track becomes a manuscript subsection with one dominant figure,
caption, and right-hand interpretation note:

1. LIBERO-Plus fixed `261/840` versus adaptive `398/840`, uplift `+137` and
   `+16.3 pp`.
2. Adaptive short development coverage `95/120`, clearly labelled as
   cross-release coverage.
3. Strict Standard-130 `67/130` Pass@10.
4. Matched Code-on/off result and measured token/time accounting.
5. ACT matched success as one demonstrated case, not a general metric.

The existing publication JSON remains the single source of every dynamic
value. The page must not merge incompatible protocols into one leaderboard.

### 6. Context, Limitations, And Reproduction

Competitive context uses a compact manuscript table with protocol notes,
followed by explicit limitations, source links, and the one-command
reproduction surface. These sections remain visually quiet and unframed.

## Interaction And Data Flow

`build_static_preview()` continues to copy static assets and generate
`data.json`. `app.js` continues to render evidence from that payload. Existing
video dialogs and ordered tool traces remain functional, but their visual
presentation adopts the manuscript system.

Critical headline facts must have truthful static HTML fallbacks so the title
page never displays `--` while JavaScript or `data.json` is loading. Dynamic
rendering then verifies/replaces those fallbacks from the canonical payload.

The stylesheet and JavaScript references receive a release query/version so
the custom domain cannot continue serving the previous cached dashboard look.
The existing root `CNAME` must survive every preview build and deployment.

## Failure Handling

- Missing `data.json`: keep static verified headline values visible and show a
  restrained evidence-unavailable note in dynamic-only sections.
- Missing video: retain its caption and trace link, show a neutral media
  fallback, and never substitute a different task video.
- Broken trace metadata: hide only the trace action for that item; do not hide
  the simulator verdict or invent a chain.
- Custom-domain certificate delay remains operationally separate from this
  visual release and must not trigger changes to evidence or DNS content.

## Test And Acceptance Plan

Implementation follows test-first development. The initial failing tests must
assert the corrected ENPIRE contract:

- no hero wordmark or hero result/link blocks;
- exact visible brand `roborsi` and no public `RoboHermes` title branding;
- hero contains only the real video and scroll cue;
- a three-column article frame with contents, manuscript, and margin notes;
- local Source Serif 4 and JetBrains Mono font assets;
- no gradient, decorative blob, nested-card, or floating-section classes;
- static fallback metrics match the canonical publication JSON;
- all existing media and tool-chain references remain packaged.

Release verification includes the full Python tests, scoped Ruff, JavaScript
syntax, release check, wheel/sdist build, static preview generation, complete
media decoding, and direct artifact inspection.

Desktop browser QA is performed at 1440 x 1000 and 1728 x 1117 against the
captured ENPIRE composition. It checks the hero, title/abstract, architecture,
one simulation case, LIBERO-Plus, and one later evidence section for overflow,
overlap, blank media, failed requests, and console errors. Canvas/SVG plots
must be nonblank. The custom domain is checked after deployment with cache-
busted CSS and JavaScript URLs.

## Release Sequence

1. Implement and verify on the feature branch.
2. Generate a local static preview and complete desktop visual inspection.
3. Merge the verified source to `main`.
4. Publish the exact preview to `gh-pages` while preserving `CNAME`.
5. Verify the GitHub Pages origin and `robo-rsi.com` assets and evidence.
6. Let the existing bounded supervisor enable enforced HTTPS when GitHub's
   certificate is available.
