#!/usr/bin/env python3
"""Render the final LIBERO-Plus publication figure from release evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

FIXED = "#aab3af"
ADAPTIVE = "#16845b"
BLUE = "#4e76a8"
CORAL = "#d45c45"
INK = "#171a18"
MUTED = "#66706a"
GRID = "#e5e9e6"


def _load_evidence(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != "robohermes.libero_plus_adaptive_final.v1":
        raise ValueError("unexpected LIBERO-Plus evidence schema")
    if payload.get("status") != "final":
        raise ValueError("LIBERO-Plus evidence is not final")
    return payload


def _panel_label(axis: Any, label: str, title: str) -> None:
    axis.text(
        -0.08,
        1.08,
        label,
        transform=axis.transAxes,
        color=INK,
        fontsize=13,
        fontweight="bold",
        va="bottom",
    )
    axis.text(
        0,
        1.08,
        title,
        transform=axis.transAxes,
        color=INK,
        fontsize=12,
        fontweight="bold",
        va="bottom",
    )


def _style_rate_axis(axis: Any, maximum: float) -> None:
    axis.set_xlim(0, maximum)
    axis.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}%"))
    axis.grid(axis="x", color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0, colors=INK, labelsize=9)
    axis.tick_params(axis="x", colors=MUTED, labelsize=8)


def _draw_dumbbells(
    axis: Any,
    rows: Sequence[dict[str, Any]],
    *,
    labels: Sequence[str],
    maximum: float,
) -> None:
    y_positions = list(range(len(rows)))[::-1]
    fixed = [100 * float(row["fixed_rate"]) for row in rows]
    adaptive = [100 * float(row["adaptive_rate"]) for row in rows]
    for y, before, after in zip(y_positions, fixed, adaptive, strict=True):
        axis.plot([before, after], [y, y], color="#bdc6c1", linewidth=2.2, zorder=1)
        axis.scatter(before, y, s=35, color=FIXED, edgecolor="white", linewidth=0.8, zorder=2)
        axis.scatter(after, y, s=42, color=ADAPTIVE, edgecolor="white", linewidth=0.8, zorder=3)
        axis.text(
            before - 0.8,
            y + 0.19,
            f"{before:.1f}",
            ha="right",
            va="center",
            color=MUTED,
            fontsize=7.5,
        )
        axis.text(
            after + 0.8,
            y + 0.19,
            f"{after:.1f}",
            ha="left",
            va="center",
            color=ADAPTIVE,
            fontsize=7.5,
            fontweight="bold",
        )
    axis.set_yticks(y_positions, labels)
    _style_rate_axis(axis, maximum)


def render_libero_plus_figure(evidence_path: Path, output_dir: Path) -> dict[str, Path]:
    evidence = _load_evidence(Path(evidence_path))
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    outputs = {
        "svg": destination / "libero-plus-final.svg",
        "png": destination / "libero-plus-final.png",
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
    figure = plt.figure(figsize=(14.4, 8.1), facecolor="white")
    grid = figure.add_gridspec(
        2,
        4,
        width_ratios=(1.05, 0.95, 1.25, 1.25),
        height_ratios=(1.08, 0.92),
        left=0.08,
        right=0.98,
        top=0.91,
        bottom=0.09,
        wspace=0.72,
        hspace=0.52,
    )
    score_axis = figure.add_subplot(grid[0, :2])
    suite_axis = figure.add_subplot(grid[1, :2])
    category_axis = figure.add_subplot(grid[0, 2:])
    stage_axis = figure.add_subplot(grid[1, 2:])

    # a: headline fixed-to-adaptive comparison.
    fixed = evidence["fixed"]
    adaptive = evidence["adaptive"]
    score_rates = [100 * float(fixed["rate"]), 100 * float(adaptive["rate"])]
    score_axis.barh([1, 0], score_rates, height=0.48, color=[FIXED, ADAPTIVE])
    score_axis.set_yticks([1, 0], ["Fixed", "Adaptive"])
    _style_rate_axis(score_axis, 55)
    score_axis.set_ylim(-0.7, 1.7)
    for y, rate, row, color in zip(
        [1, 0], score_rates, [fixed, adaptive], [MUTED, ADAPTIVE], strict=True
    ):
        score_axis.text(
            rate + 1.0,
            y,
            f"{row['success']} / {row['success'] + row['failure']}  ({rate:.1f}%)",
            va="center",
            color=color,
            fontsize=11,
            fontweight="bold",
        )
    score_axis.text(
        0,
        -0.52,
        f"+{evidence['uplift']['successes']} identities  |  "
        f"+{evidence['uplift']['percentage_points']:.1f} percentage points",
        color=CORAL,
        fontsize=10,
        fontweight="bold",
    )
    _panel_label(score_axis, "a", "Adaptive Pass@2 improves the full perturbation panel")

    # b: all seven perturbation categories.
    category_rows = list(evidence["by_category"])
    _draw_dumbbells(
        category_axis,
        category_rows,
        labels=[str(row["name"]) for row in category_rows],
        maximum=65,
    )
    _panel_label(category_axis, "b", "Success by perturbation category")
    category_axis.text(
        0.98,
        1.08,
        "Fixed     Adaptive",
        transform=category_axis.transAxes,
        ha="right",
        va="bottom",
        color=MUTED,
        fontsize=8,
    )

    # c: the three official short suites.
    suite_rows = list(evidence["by_suite"])
    suite_labels = {
        "libero_spatial": "Spatial",
        "libero_object": "Object",
        "libero_goal": "Goal",
    }
    _draw_dumbbells(
        suite_axis,
        suite_rows,
        labels=[suite_labels[str(row["name"])] for row in suite_rows],
        maximum=70,
    )
    _panel_label(suite_axis, "c", "Success by suite")

    # d: cumulative release contribution with measured token cost.
    stages = list(evidence["stages"])
    x_values = list(range(len(stages) + 1))
    cumulative = [int(fixed["success"]), *[int(row["cumulative_success"]) for row in stages]]
    stage_axis.plot(x_values, cumulative, color=BLUE, linewidth=2.2, marker="o", markersize=5)
    stage_axis.fill_between(x_values, cumulative, min(cumulative) - 8, color="#e8eef5", alpha=1)
    stage_axis.set_ylim(min(cumulative) - 8, max(cumulative) + 27)
    stage_axis.set_xlim(-0.25, len(stages) + 0.25)
    stage_axis.set_xticks(
        x_values,
        ["Fixed r149", "r160\ncluster", "r160\nwave", "r164\nsemantic", "r164\nPass@2"],
    )
    stage_axis.set_ylabel("Solved identities", color=MUTED, fontsize=8)
    stage_axis.grid(axis="y", color=GRID, linewidth=0.8)
    stage_axis.spines[["top", "right"]].set_visible(False)
    stage_axis.tick_params(axis="both", colors=MUTED, labelsize=8)
    for index, value in enumerate(cumulative):
        stage_axis.text(
            index,
            value + 3.2,
            str(value),
            ha="center",
            color=INK,
            fontsize=9,
            fontweight="bold",
        )
        if index:
            row = stages[index - 1]
            token_millions = float(row["efficiency"]["total_tokens"]) / 1_000_000
            stage_axis.text(
                index,
                min(cumulative) - 5.5,
                f"+{row['new_successes']} | {token_millions:.1f}M tok",
                ha="center",
                va="bottom",
                color=ADAPTIVE if row["new_successes"] else MUTED,
                fontsize=7.2,
            )
    _panel_label(stage_axis, "d", "Release contribution and metered cost")

    figure.text(
        0.08,
        0.025,
        "840 LIBERO-Plus identities · final simulator verdict only · "
        "GPT-5.6 Sol (medium) · JOINT_POSITION",
        color=MUTED,
        fontsize=8,
    )
    figure.savefig(outputs["svg"], format="svg", facecolor="white")
    figure.savefig(outputs["png"], format="png", dpi=300, facecolor="white")
    plt.close(figure)
    return outputs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    outputs = render_libero_plus_figure(Path(args.evidence), Path(args.output_dir))
    print(json.dumps({name: str(path) for name, path in outputs.items()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
