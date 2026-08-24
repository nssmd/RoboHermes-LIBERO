#!/usr/bin/env python3
"""Render the claim-bounded evolution dynamics figure from public evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

INK = "#171a18"
MUTED = "#69716c"
GRID = "#e4e8e4"
GREEN = "#447c56"
RUST = "#996653"
BLUE = "#3d6470"
NEUTRAL = "#9aa39e"


def _read(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _panel_label(axis: Any, label: str, title: str) -> None:
    axis.text(
        -0.08,
        1.09,
        label,
        transform=axis.transAxes,
        color=INK,
        fontsize=13,
        fontweight="bold",
        va="bottom",
    )
    axis.text(
        0,
        1.09,
        title,
        transform=axis.transAxes,
        color=INK,
        fontsize=12,
        fontweight="bold",
        va="bottom",
    )


def _style_line_axis(axis: Any, *, xlabel: str, ylabel: str) -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.set_xlabel(xlabel, color=MUTED, fontsize=8)
    axis.set_ylabel(ylabel, color=MUTED, fontsize=8)
    axis.tick_params(axis="both", colors=MUTED, labelsize=8)
    axis.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))


def _end_labels(axis: Any, x: list[float], y: list[float], color: str) -> None:
    for index in (0, len(x) - 1):
        axis.text(
            x[index],
            y[index] + 2.0,
            str(int(y[index])),
            color=color,
            fontsize=9,
            fontweight="bold",
            ha="center",
        )


def render_evolution_dynamics(
    *,
    experiments_path: Path,
    strict_path: Path,
    robotwin_path: Path,
    output_dir: Path,
) -> dict[str, Path]:
    experiments = _read(experiments_path)["experiments"]
    strict = _read(strict_path)
    robotwin = _read(robotwin_path)
    if strict.get("schema") != "roborsi.strict_round_dynamics.v1":
        raise ValueError("unexpected strict dynamics schema")
    if robotwin.get("schema") != "roborsi.robotwin_historical.v1":
        raise ValueError("unexpected RoboTwin historical schema")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    outputs = {
        "svg": destination / "evolution-dynamics.svg",
        "png": destination / "evolution-dynamics.png",
    }

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "svg.fonttype": "none",
            "font.size": 9,
            "axes.linewidth": 1.0,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "legend.frameon": False,
        }
    )
    figure, axes = plt.subplots(2, 2, figsize=(14.4, 8.1), facecolor="white")
    figure.subplots_adjust(left=0.08, right=0.97, top=0.90, bottom=0.11, wspace=0.30, hspace=0.48)

    # a: strict cumulative retry coverage, deliberately not framed as evolution.
    strict_axis = axes[0, 0]
    strict_x = list(range(1, len(strict["pass_curve"]) + 1))
    strict_y = [float(value) for value in strict["pass_curve"]]
    strict_axis.plot(strict_x, strict_y, color=BLUE, linewidth=2.2, marker="o", markersize=4.5)
    strict_axis.fill_between(strict_x, strict_y, 18, color="#e8eef0")
    strict_axis.set_xlim(0.7, 10.3)
    strict_axis.set_ylim(18, 74)
    strict_axis.set_xticks(strict_x)
    _style_line_axis(strict_axis, xlabel="Ordered seed budget k", ylabel="Tasks solved / 130")
    _end_labels(strict_axis, strict_x, strict_y, BLUE)
    strict_axis.text(
        0.02,
        0.04,
        "Pass@k is retry coverage, not evolution",
        transform=strict_axis.transAxes,
        color=RUST,
        fontsize=9,
        fontweight="bold",
    )
    _panel_label(strict_axis, "a", "Strict Standard-130")

    # b: the actual ordered adaptive process with evolving releases.
    adaptive_axis = axes[0, 1]
    adaptive = experiments["adaptive_sequential"]
    adaptive_x = list(range(1, len(adaptive["pass_curve"]) + 1))
    adaptive_y = [float(value) for value in adaptive["pass_curve"]]
    adaptive_axis.plot(
        adaptive_x, adaptive_y, color=GREEN, linewidth=2.2, marker="o", markersize=4.5
    )
    adaptive_axis.fill_between(adaptive_x, adaptive_y, 26, color="#e6eee8")
    adaptive_axis.set_xlim(0.7, 10.3)
    adaptive_axis.set_ylim(26, 91)
    adaptive_axis.set_xticks(adaptive_x)
    _style_line_axis(adaptive_axis, xlabel="Adaptive round", ylabel="Tasks solved / 120")
    _end_labels(adaptive_axis, adaptive_x, adaptive_y, GREEN)
    adaptive_axis.text(
        0.02,
        0.04,
        "Evolving releases; cumulative development coverage",
        transform=adaptive_axis.transAxes,
        color=MUTED,
        fontsize=8.5,
    )
    _panel_label(adaptive_axis, "b", "Adaptive LIBERO")

    # c: historical RoboTwin wall-clock campaign with explicit audit correction.
    robotwin_axis = axes[1, 0]
    robotwin_x = [float(value) for value in robotwin["elapsed_hours"]]
    robotwin_y = [float(value) for value in robotwin["solved_over_time"]]
    robotwin_axis.plot(
        robotwin_x, robotwin_y, color=RUST, linewidth=2.2, marker="o", markersize=4.5
    )
    robotwin_axis.axhline(
        float(robotwin["pure_engineer_solved"]),
        color=NEUTRAL,
        linewidth=1.4,
        linestyle="--",
    )
    robotwin_axis.text(
        87,
        float(robotwin["pure_engineer_solved"]) + 1.0,
        "historical pure Engineer report: 9 / 50",
        ha="right",
        color=MUTED,
        fontsize=8,
    )
    robotwin_axis.annotate(
        "audit correction",
        xy=(robotwin_x[8], robotwin_y[8]),
        xytext=(50, 25),
        color=RUST,
        fontsize=8,
        arrowprops={"arrowstyle": "->", "color": RUST, "linewidth": 1.0},
    )
    robotwin_axis.set_xlim(-2, 91)
    robotwin_axis.set_ylim(5, 41)
    _style_line_axis(robotwin_axis, xlabel="Campaign wall clock (h)", ylabel="Tasks solved / 50")
    _end_labels(robotwin_axis, robotwin_x, robotwin_y, RUST)
    robotwin_axis.text(
        0.0,
        1.01,
        "87% adjacent-attempt overlap; historical campaign progress",
        transform=robotwin_axis.transAxes,
        color=MUTED,
        fontsize=8,
        va="bottom",
    )
    _panel_label(robotwin_axis, "c", "Historical RoboTwin")

    # d: the matched causal efficiency evidence.
    efficiency_axis = axes[1, 1]
    efficiency = experiments["matched_code"]["efficiency"]
    labels = ["Median tokens", "Median VLM calls", "Median wall time"]
    reductions = [
        100 * float(efficiency["median_total_tokens"]["reduction"]),
        100 * float(efficiency["median_vlm_calls"]["reduction"]),
        100 * float(efficiency["median_wall_s"]["reduction"]),
    ]
    y_positions = [2, 1, 0]
    efficiency_axis.barh(y_positions, reductions, height=0.5, color=[GREEN, BLUE, RUST])
    efficiency_axis.set_yticks(y_positions, labels)
    efficiency_axis.set_xlim(0, 34)
    efficiency_axis.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}%"))
    efficiency_axis.grid(axis="x", color=GRID, linewidth=0.8)
    efficiency_axis.set_axisbelow(True)
    efficiency_axis.spines[["top", "right", "left"]].set_visible(False)
    efficiency_axis.tick_params(axis="y", length=0, colors=INK, labelsize=9)
    efficiency_axis.tick_params(axis="x", colors=MUTED, labelsize=8)
    efficiency_axis.set_xlabel("Reduction with Code-on", color=MUTED, fontsize=8)
    for y, reduction in zip(y_positions, reductions, strict=True):
        efficiency_axis.text(
            reduction + 0.7,
            y,
            f"{reduction:.1f}%",
            va="center",
            color=INK,
            fontsize=9,
            fontweight="bold",
        )
    efficiency_axis.text(
        0.0,
        1.01,
        "118-task matched panel; this supports the faster claim",
        transform=efficiency_axis.transAxes,
        color=MUTED,
        fontsize=8,
        va="bottom",
    )
    _panel_label(efficiency_axis, "d", "Matched efficiency")

    figure.text(
        0.08,
        0.025,
        "Claim boundary: strict is retry coverage; adaptive and RoboTwin are evolving campaigns; "
        "only Code-on/off is a matched efficiency comparison.",
        color=MUTED,
        fontsize=8,
    )
    figure.savefig(outputs["svg"], format="svg", facecolor="white")
    figure.savefig(outputs["png"], format="png", dpi=300, facecolor="white")
    plt.close(figure)
    return outputs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiments", required=True)
    parser.add_argument("--strict", required=True)
    parser.add_argument("--robotwin", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    outputs = render_evolution_dynamics(
        experiments_path=Path(args.experiments),
        strict_path=Path(args.strict),
        robotwin_path=Path(args.robotwin),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps({name: str(path) for name, path in outputs.items()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
