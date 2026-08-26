# roborsi Evidence Demo Video Design

## 2026-08-26 Remotion Narrated Revision

The current production film supersedes the original silent OpenCV compositor.
It is a 60-second Remotion 4.0.517 composition with five scenes:
introduction, verified rollout wall, matched ACT corrective case with the
separate adaptive curve, matched Code-on/off results, and end slate.

English and Simplified Chinese are first-class renders. Each has synchronized
burned-in narration captions, a separate optional WebVTT track, and a committed
voiceover set. The browser player is no longer muted by default.

ElevenLabs `eleven_v3` is the preferred speech provider. The voice ID, model,
scripts, timing, output format, and voice settings are pinned in
`remotion/voiceover.json`. Generated MP3 files are committed so rendering does
not require an API key. If no ElevenLabs key is available, the documented
Microsoft Neural fallback may generate audition tracks; the actual provider is
recorded in `generated_provider`.

`scripts/build_demo_video.py` remains the stable public entrypoint. It loads the
canonical evidence bundle, builds Remotion props, invokes the
`RoborsiDemo` composition, and normalizes the output to H.264 `yuv420p`,
BT.709, AAC stereo, and fast-start MP4. The TypeScript composition owns all
layout, animation, media looping, captions, and audio sequencing.

## Status

Approved for direct implementation. The user requested one published demo that
shows a 3 x 3 task grid, self-evolution, and faster execution after successful
experience is solidified into code. No additional experiment is required.

## Goal

Produce a deterministic, source-controlled project video that communicates
three evidence-backed claims in under 40 seconds and can be regenerated with
one command from the public repository.

## Claim Contract

The video keeps three evidence scopes separate:

1. The 3 x 3 grid is qualitative evidence from nine named, final-verdict
   success videos. It is not a denominator or leaderboard.
2. The `32 -> 83/120` curve is cross-release adaptive development coverage.
   It is not fixed-policy Pass@10 and does not use the Strict Standard-130
   retry curve as evidence of evolution.
3. Faster execution is supported only by the matched Code-on/off panels:
   `+7.5 pp` episode success, `-29.4%` median tokens, `-27.2%` median VLM
   calls, and `-17.0%` median wall time. The accompanying rollout illustrates
   code-backed execution; it is not presented as one of the 118 timing pairs.

All success labels refer to post-episode native simulator or archived native
predicate verdicts. Hidden task truth is never shown to the agent or exposed in
the demo.

## Storyboard

Historical note: the first master was 39 seconds and silent. The current master
is 60 seconds, 1920 x 1080, 30 fps, H.264 `yuv420p`, with AAC narration.

### 0.0-12.0 s: Rotating 3 x 3 Task Wall

A 3 x 3 grid plays nine real task videos concurrently, then rotates to a second
page. The union covers all 13 existing success recordings while retaining the
nine-cell visual composition. Compact labels identify task and platform; a
simulator-confirmed status line establishes the evidence contract without
implying that the videos are a benchmark denominator.

The 13 sources are:

- LIBERO: moka pot to stove, ketchup to basket, pudding to basket, bowl to
  tray, adaptive bowl to plate, and ACT corrective transport.
- RoboTwin historical: grab roller, place container on plate, and turn switch.
- LIBERO-Plus: camera, lighting, layout, and initial-state perturbation cases.

RoboTwin footage is retained at its native exposure. The compositor may crop
or letterbox it but must not substitute or fabricate frames.

### 12.0-24.0 s: Self-Evolution

Two videos show `libero_spatial_swap/0`, seed 3, side by side. Before corrective
data, bounded ACT completes 120 transport steps but under-transports and loses
the hold during placement; the final simulator verdict is false. After
corrective data and fine-tuning, ACT completes 304 steps and wrist-verified
placement reaches a true final verdict. Both videos use normalized episode
progress because their archived durations differ.

A separate chart reveals `[32, 45, 52, 66, 71, 76, 81, 82, 82, 83]`. The film
explicitly separates this aggregate cross-release coverage measure from the
single matched ACT case. The final frame states:

> Cross-release adaptive development coverage; not fixed-policy Pass@10.

### 24.0-35.0 s: Better And Faster With Code

A real adaptive `visual_pick_place` rollout plays beside four animated matched
results. Code-on is defined as exposing the solidified compound; Code-off keeps
the model, release, tasks, seeds, base tools, and budget matched while removing
that compound. The footer states:

> Matched Code-on/off results. Video illustrates code-backed execution.

### 35.0-39.0 s: End Slate

The lowercase `roborsi` brand and `robo-rsi.com` close the video with a brief
reference to simulator-verified experience becoming inspectable code.

## Visual System

The video follows the website's ENPIRE manuscript language: charcoal, a pure
white paper background, light-neutral figure wells, muted green, rust, and blue; Source Serif 4 for
editorial text and JetBrains Mono for data labels. Layout uses thin rules,
stable geometry, and at most 8 px radii. There are no gradients, decorative
orbs, bokeh, oversized marketing copy, or fabricated robot imagery.

Transitions use short opacity and positional easing while retaining a stable
frame. Text must remain inside safe margins at both the production and smoke
render dimensions.

## Implementation

Historical note: the original implementation used OpenCV and Pillow. The
current implementation is source-controlled under `remotion/`; Python now
serves only as the evidence-aware render wrapper and final media normalizer.

Command-line controls support output path, poster path, dimensions, frame rate,
and a duration scale. The scale exists for fast deterministic tests; scene
semantics and normalized animations remain identical.

The production outputs are:

- `src/robohermes_libero/static/media/demo/roborsi-demo.mp4`
- `src/robohermes_libero/static/media/demo/roborsi-demo-poster.jpg`
- `src/robohermes_libero/static/media/demo/roborsi-demo-zh.mp4`
- `src/robohermes_libero/static/media/demo/roborsi-demo-zh-poster.jpg`

## Bilingual Publication

The public release has two first-class static documents. `/index.html` is the
English project page and `/zh.html` is the Simplified Chinese project page.
Both pages retain the same section order, result values, task identifiers,
figures, video library, and evidence boundaries. A fixed `EN / 中文` control
switches documents without runtime machine translation.

English copy follows a formal research-project register. Chinese copy is
written independently for technical readers. Standard identifiers such as
LIBERO, ACT, Pass@k, Code-on/off, Planner, Engineer, and Reviewer are retained,
while avoidable internal shorthand is translated. Dynamic video titles, trace
states, comparison rows, cost metrics, and failure verdicts follow the active
document language.

The compositor accepts `--language en|zh`. The Chinese master is rendered with
the locally vendored WenQuanYi Micro Hei collection, so every frame is
reproducible without host font discovery. English continues to use Source
Serif 4 and JetBrains Mono. Font provenance and redistribution terms are
recorded in `fonts/FONT-LICENSES.md`.

## Website Integration

Add a `Demo` manuscript section immediately after Abstract and a corresponding
outline link. The video uses native controls, muted inline playback, a poster,
and metadata preload. Its caption lists the three claim scopes. Below it, one
matched ACT Before/After block exposes the retained failure and success clips.
A unified library then exposes all 14 recordings with native controls and a
Trace action for each available tool chain. Historical RoboTwin clips remain
explicitly final-verdict-only because their per-call logs were not archived.

The visible Task evidence and Reproduce sections, their outline links, and
their dedicated JavaScript/CSS are removed. The underlying public evidence and
repository reproduction files remain unchanged. `build_static_preview()`
continues to copy the static tree, so no new packaging mechanism is introduced.

## Verification

The test suite must first fail while the generator is absent. A low-resolution
smoke render then verifies dimensions, H.264, `yuv420p`, no audio, expected
duration, a nonblank poster, visually distinct nonblank scene samples, and
two distinct rotating grid pages and distinct final Before/After frames.

Release verification includes the full pytest suite, Ruff, release checks,
JavaScript syntax, wheel/sdist build, a complete decode of every published MP4,
and desktop Chromium QA at 1440 x 1000 and 1728 x 1117. Browser QA checks that
each language loads its corresponding master, the poster/video are nonblank,
controls work, and all 14 library videos and their available traces render in
the selected language without request, console, overflow, or overlap failures.
