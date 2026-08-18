# RoboHermes ENPIRE-Inspired Media Release Design

## Purpose

Turn the current evidence-replay console into a research project page that can
serve three audiences from the same verified sources: researchers checking the
method and protocol, engineers reproducing the release, and media readers
looking for a concise account of what was demonstrated.

The release remains LIBERO-short-only. It does not import or make claims about
OPD, ProLong, or long-horizon artifacts.

## Claim Boundary

The page presents five distinct evidence tracks without merging their metrics:

1. Adaptive development coverage: `95/120` cumulative tasks across evolving
   releases. This is not a frozen or single-release Pass@10 result.
2. Sequential adaptive campaign: `32/120` at Pass@1 to `83/120` at Pass@10,
   with measured token and active wall-time accounting.
3. Strict Standard-130: `67/130` task-level Pass@10 under the final-simulator-
   verdict-only protocol.
4. Matched Code-on/off: 600 task-seed pairs per arm for success, plus a
   separate 118-task matched panel for token and wall-time efficiency.
5. ACT: one matched seed-3 simulator success. It is a demonstrated case, not
   held-out policy generalization.

All cross-project numbers appear in a protocol matrix, not in a shared
leaderboard chart. RoboHarness and OpenETA results are described with their
policy dependencies, visible checker contract, image views, horizons, trial
counts, and evaluation scope.

## Information Architecture

The page adapts ENPIRE's editorial research-page language without copying its
assets or wording:

1. A full-bleed LIBERO-success video hero with the literal product name,
   concise method statement, and paper/code/evidence links.
2. A sticky desktop article outline.
3. Architecture first: Planner, Engineer, Reviewer, code-backed skills,
   simulator execution, and post-hoc host adjudication.
4. Simulation evidence: one representative video per task, native verdict,
   seed/release scope, and an expandable tool-call chain.
5. Experimental results: adaptive coverage, strict Standard-130, matched
   Code-on/off, efficiency, and ACT, each with its own evidence label.
6. Competitive context: source-backed RoboHarness, OpenETA, ENPIRE, and
   `vla-evaluation-harness` comparison plus explicit gaps and strengths.
7. Full 120-task evidence table and one-command reproduction entrypoints.

The visual system uses editorial serif headings, compact sans-serif data text,
white and light-gray bands, charcoal, green, coral, and blue accents. Cards are
reserved for repeated video items and evidence tracks; page sections remain
unframed. No decorative gradients or color blobs are introduced.

## Data And Media

`evidence/publication-v1/experiments.json` is the canonical publication data
source. The dashboard payload embeds it without recomputing experimental
statistics. It contains only sanitized aggregate values, public source URLs,
claim labels, and media metadata.

The public media set contains four healthy 512x512 Standard-130 success clips,
one adaptive success clip, one ACT success clip, generated posters, and a
LIBERO-only hero mosaic. Every gallery row identifies one task and one video.
Published tool chains contain tool names and boolean outcomes, not private
paths, hidden state, or demonstration coordinates.

## Documents

- `docs/EXPERIMENTS_AND_COMPARISON.md`: current experiment inventory,
  protocol-aware competitive analysis, evidence sources, gaps, and next tests.
- `PRESS_KIT_ZH.md`: evidence-bounded Chinese media draft.
- `SOCIAL_COPY.md`: one-post X copy, a thread, captions, and alt text.
- `README.md`: updated project-page links, result tracks, videos, and claim
  labels.

## Validation

Tests must establish that publication values match locked artifacts, media
references are copied into static previews, private paths are absent, and page
sections occur in the required order. Release verification additionally runs
the full test suite, Ruff on maintained release modules, JavaScript syntax,
FFprobe plus multi-frame FFmpeg decoding for every public video, package build,
evidence replay, release hygiene, and desktop Playwright checks for console
errors, failed requests, layout overlap, and nonblank video frames.
