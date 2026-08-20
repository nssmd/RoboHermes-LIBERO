# LIBERO-Plus ENPIRE Results Design

## Purpose

Extend the existing ENPIRE-inspired RoboHermes project page with the completed
840-identity LIBERO-Plus evaluation. The page must make the fixed-to-adaptive
gain legible without merging this identity-level perturbation panel with the
120-task adaptive Pass@10, strict Standard-130, Code-on/off, or ACT results.

## Evidence Contract

The published LIBERO-Plus result is generated only after all 840 fixed
identities and every scheduled adaptive Pass@2 identity have a final simulator
verdict. Provider, transport, resource, randomization, and interrupted records
remain preserved but do not enter the denominator. Planner-, Engineer-, and
Reviewer-visible inputs do not contain task predicates, rewards, object poses,
or post-hoc simulator truth.

One sanitized JSON object is the source for every displayed LIBERO-Plus number.
It contains fixed/adaptive metrics, seven perturbation categories, three short
suites, release-stage cost, and four representative native-success videos with
sanitized tool-call chains.

## Page Structure

Keep the full-bleed rollout hero and sticky paper-style outline. Add
`LIBERO-Plus` between simulator rollouts and the prior experiment ledger, so
the order remains architecture, simulation, then experiments.

The section contains:

1. A large fixed-to-adaptive result lockup with the literal 840-identity scope.
2. A Matplotlib figure with a hero comparison, seven perturbation rows, three
   suite rows, and release contributions.
3. A release timeline showing new successes, tokens, and active wall time.
4. Four distinct-task success videos opening the existing tool-trace dialog.
5. A note that adaptive Pass@2 is not a direct cross-project leaderboard.

## Visual Direction

Follow ENPIRE's editorial language without copying assets. Brighten the real
rollout hero; make the RoboHermes wordmark the first-viewport signal; combine
serif display text, compact sans-serif copy, and monospace evidence labels.
Use charcoal, white, cool gray, signal green, muted blue, and one coral accent.
Do not use gradients, decorative blobs, nested cards, or oversized panel type.

## Media And Figure Rules

Every video must fully decode, contain nonblank frames, and map to a final
simulator-success record. Publish one video per task. Tool chains expose only
registered tool names and boolean outcomes, never private paths, coordinates,
hidden state, or prompts.

Generate the figure with Matplotlib from the sanitized final JSON and export
editable SVG plus high-resolution PNG. The plotting script must not duplicate
metric literals.

## Verification And Release

Run focused and full Python tests, Ruff, JavaScript syntax, static-preview
build, full MP4 decoding, representative-frame inspection, and desktop
Chromium checks at 1440x1000 and 1728x1117. Verify nonblank media, dialogs,
overflow, overlap, console errors, and failed requests. Publish `gh-pages`
only after these gates pass and verify the public result and media responses.
