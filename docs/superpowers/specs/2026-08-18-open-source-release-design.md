# RoboHermes LIBERO Open-Source Release Design

## Purpose

Create a clean, LIBERO-short-only repository that a new user can configure,
inspect, and run without knowing the private research environment. The release
must preserve skill evolution while keeping hidden simulator truth outside
every agent-visible prompt and trace.

## Result Boundary

The reported `95/120` result is **Adaptive task-level Pass@10** accumulated
across evolving releases. It is not a frozen-policy score and is not reproduced
by running one latest release once. The public interface exposes three separate
paths:

1. `results replay` recomputes the reported metric from normalized retained
   evidence.
2. `eval libero-short --mode adaptive` starts a new ten-round adaptive campaign
   whose skill overlay may change between rounds.
3. `eval libero-short --mode fixed` evaluates one immutable release and reports
   it separately from adaptive coverage.

Only a final simulator predicate can create a `task_success` record. Provider,
transport, image, resource, and interrupted records are retained but excluded
from the task denominator.

## Repository Shape

- `src/robohermes_libero/`: config, CLI, launch, evidence, integrity, and
  dashboard modules.
- `src/robohermes/`: allowlisted production runtime and LIBERO skills required
  by the evaluator.
- `configs/`: one canonical YAML schema and checked-in example.
- `evidence/`: normalized result bundle and machine-readable claim metadata.
- `scripts/`: one-command setup and service launch.
- `web/`: static desktop dashboard driven by replay JSON.
- `tests/`: protocol, CLI, dashboard, leak, and release-content tests.

## Configuration

`robohermes.yaml` is the single source of truth. It records the Responses
endpoint and API-key environment variable, `responses/gpt-5.6-sol` with medium
reasoning, paths, devices, services, ordered seeds `0..9`, horizon, image size,
tool budget, evaluation mode, and integrity invariants.

Secrets are never written to YAML. `configure` stores only the environment
variable name. `doctor` fails closed on missing paths, provider mismatch,
unavailable required services, or an invalid integrity mode.

## Runtime And Evolution

The runtime is Planner -> Engineer -> Reviewer. The roles see only the current
instruction, camera RGB/RGB-D, robot proprioception, registered tools, and
retained visible memory. The host calls the simulator predicate only after the
episode and appends its verdict to the journal.

Adaptive changes live in a campaign overlay rather than mutating the installed
package. A proposal must pass syntax, import, forbidden-input, focused tests,
and a simulator harness before promotion. Every proposal, rejection, release
manifest, journal, trace, trajectory, and video is retained.

## User Interface

The terminal UI provides `configure`, `doctor`, `eval`, `results`, and
`dashboard`. The desktop dashboard shows campaign status, Pass@k, suite
coverage, token/time efficiency, task rows, artifact links, and explicit claim
labels. It reads generated JSON and has no second metric implementation.

## Reproducibility

`setup.sh` creates an isolated environment, installs this package, checks out a
pinned upstream LIBERO revision, generates configuration, and runs `doctor`.
Every evaluation writes a resolved config snapshot, task catalog, release
identity, ordered seed schedule, append-only journals, and final summary.
Resume skips terminal task/seed pairs and never reruns a successful pair.

## Release Hygiene

The public tree contains no credentials, private endpoints, private paths,
generated experiment logs, unrelated simulators, hidden-ground-truth inputs,
or excluded benchmark code. Apache-2.0 is declared consistently.
