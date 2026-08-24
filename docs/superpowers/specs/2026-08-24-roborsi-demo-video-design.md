# roborsi Evidence Demo Video Design

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

The master is 39 seconds, 1920 x 1080, 30 fps, H.264, `yuv420p`, silent.

### 0.0-12.0 s: Nine Verified Tasks

A 3 x 3 grid plays nine real task videos concurrently. Compact labels identify
the task and platform; a simulator-confirmed status line establishes the
evidence contract without implying that nine examples are a metric.

The nine sources are:

- LIBERO: moka pot to stove, ketchup to basket, pudding to basket, bowl to
  tray, adaptive bowl to plate, and ACT corrective transport.
- RoboTwin historical: grab roller, place container on plate, and turn switch.

RoboTwin footage is retained at its native exposure. The compositor may crop
or letterbox it but must not substitute or fabricate frames.

### 12.0-24.0 s: Self-Evolution

An animated line reveals the measured adaptive sequence
`[32, 45, 52, 66, 71, 76, 81, 82, 82, 83]`. A synchronized loop highlights
Observe, Diagnose, Solidify, and Reuse. The final frame states:

> Cross-release adaptive development coverage; not fixed-policy Pass@10.

### 24.0-35.0 s: Better And Faster With Code

A real adaptive `visual_pick_place` rollout plays beside four animated matched
results. Code-on is defined as exposing the solidified compound; Code-off keeps
the model, release, tasks, seeds, base tools, and budget matched while removing
that compound. The footer states:

> Matched Code-on/off panels. Video illustrates code-backed execution.

### 35.0-39.0 s: End Slate

The lowercase `roborsi` brand and `robo-rsi.com` close the video with a brief
reference to simulator-verified experience becoming inspectable code.

## Visual System

The video follows the website's ENPIRE manuscript language: charcoal, warm
paper, white figure wells, muted green, rust, and blue; Source Serif 4 for
editorial text and JetBrains Mono for data labels. Layout uses thin rules,
stable geometry, and at most 8 px radii. There are no gradients, decorative
orbs, bokeh, oversized marketing copy, or fabricated robot imagery.

Transitions use short opacity and positional easing while retaining a stable
frame. Text must remain inside safe margins at both the production and smoke
render dimensions.

## Implementation

`scripts/build_demo_video.py` owns the storyboard. OpenCV samples existing MP4
sources, Pillow renders local fonts and vector-like overlays, and FFmpeg
receives raw BGR frames and encodes H.264. Rendering is streaming and does not
create an intermediate frame directory.

Command-line controls support output path, poster path, dimensions, frame rate,
and a duration scale. The scale exists for fast deterministic tests; scene
semantics and normalized animations remain identical.

The production outputs are:

- `src/robohermes_libero/static/media/demo/roborsi-demo.mp4`
- `src/robohermes_libero/static/media/demo/roborsi-demo-poster.jpg`

## Website Integration

Add a `Demo` manuscript section immediately after Abstract and a corresponding
outline link. The video uses native controls, muted inline playback, a poster,
and metadata preload. Its caption lists the three claim scopes and links users
to the detailed evidence sections. `build_static_preview()` continues to copy
the static tree, so no new packaging mechanism is introduced.

## Verification

The test suite must first fail while the generator is absent. A low-resolution
smoke render then verifies dimensions, H.264, `yuv420p`, no audio, expected
duration, a nonblank poster, and visually distinct nonblank scene samples.

Release verification includes the full pytest suite, Ruff, release checks,
JavaScript syntax, wheel/sdist build, a complete decode of every published MP4,
and desktop Chromium QA at 1440 x 1000 and 1728 x 1117. Browser QA checks that
the demo reaches ready state, the poster/video are nonblank, controls work, and
there are no request, console, overflow, or overlap failures.
