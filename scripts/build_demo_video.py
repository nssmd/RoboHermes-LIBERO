#!/usr/bin/env python3
"""Build the reproducible roborsi evidence demo from published source media."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src/robohermes_libero/static"
DEFAULT_OUTPUT = STATIC / "media/demo/roborsi-demo.mp4"
DEFAULT_POSTER = STATIC / "media/demo/roborsi-demo-poster.jpg"
ADAPTIVE_CAPTION = (
    "Cross-release adaptive development coverage; not fixed-policy Pass@10."
)
MATCHED_CAPTION = (
    "Matched Code-on/off panels. Video illustrates code-backed execution."
)
SCENES = (
    {"id": "verified_tasks", "duration_s": 12.0},
    {"id": "adaptive_evolution", "duration_s": 12.0},
    {"id": "matched_code", "duration_s": 11.0},
    {"id": "end_slate", "duration_s": 4.0},
)
SOURCE_SPECS = (
    {
        "id": "strict-moka-pot-stove",
        "label": "Moka pot to stove",
        "platform": "LIBERO",
        "offset_s": 2.0,
    },
    {
        "id": "strict-ketchup-basket",
        "label": "Ketchup to basket",
        "platform": "LIBERO",
        "offset_s": 1.0,
    },
    {
        "id": "strict-pudding-basket",
        "label": "Pudding to basket",
        "platform": "LIBERO",
        "offset_s": 1.5,
    },
    {
        "id": "strict-bowl-tray",
        "label": "Black bowl to tray",
        "platform": "LIBERO",
        "offset_s": 1.0,
    },
    {
        "id": "adaptive-black-bowl-plate",
        "label": "Black bowl to plate",
        "platform": "LIBERO",
        "offset_s": 0.5,
    },
    {
        "id": "act-corrective-transport",
        "label": "ACT transport",
        "platform": "LIBERO",
        "offset_s": 0.3,
    },
    {
        "id": "robotwin-grab-roller-seed22",
        "label": "Grab roller",
        "platform": "RoboTwin",
        "offset_s": 18.0,
    },
    {
        "id": "robotwin-place-container-plate-seed21",
        "label": "Container to plate",
        "platform": "RoboTwin",
        "offset_s": 18.0,
    },
    {
        "id": "robotwin-turn-switch-seed23",
        "label": "Turn switch",
        "platform": "RoboTwin",
        "offset_s": 12.0,
    },
)


def _load_evidence() -> tuple[dict[str, Any], dict[str, Any]]:
    publication = json.loads(
        (ROOT / "evidence/publication-v1/experiments.json").read_text(encoding="utf-8")
    )
    robotwin = json.loads(
        (ROOT / "evidence/publication-v1/robotwin_historical.json").read_text(
            encoding="utf-8"
        )
    )
    return publication, robotwin


def build_manifest() -> dict[str, Any]:
    publication, robotwin = _load_evidence()
    publication_media = publication["media"]["videos"]
    robotwin_media = robotwin["media"]["videos"]
    records = {row["id"]: row for row in (*publication_media, *robotwin_media)}
    sources = []
    for spec in SOURCE_SPECS:
        record = records[spec["id"]]
        verdict = (
            "native_simulator_success"
            if spec["platform"] == "LIBERO"
            else "native_predicate_success"
        )
        sources.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "platform": spec["platform"],
                "task": record["task"],
                "seed": record["seed"],
                "path": str((Path("src/robohermes_libero/static") / record["video"])),
                "offset_s": spec["offset_s"],
                "verdict": verdict,
            }
        )

    adaptive = publication["experiments"]["adaptive_sequential"]
    matched = publication["experiments"]["matched_code"]
    return {
        "schema": "roborsi.evidence_demo.v1",
        "duration_s": sum(scene["duration_s"] for scene in SCENES),
        "master": {"width": 1920, "height": 1080, "fps": 30, "audio": False},
        "scenes": [dict(scene) for scene in SCENES],
        "sources": sources,
        "adaptive": {
            "coverage": adaptive["pass_curve"],
            "total_tasks": adaptive["total_tasks"],
            "caption": ADAPTIVE_CAPTION,
        },
        "matched_code": {
            "episode_success_delta_pp": matched["success"]["paired_delta_pp"],
            "median_token_reduction_pct": round(
                100 * matched["efficiency"]["median_total_tokens"]["reduction"], 1
            ),
            "median_vlm_call_reduction_pct": round(
                100 * matched["efficiency"]["median_vlm_calls"]["reduction"], 1
            ),
            "median_wall_reduction_pct": round(
                100 * matched["efficiency"]["median_wall_s"]["reduction"], 1
            ),
            "caption": MATCHED_CAPTION,
        },
    }


def _smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


class VideoSampler:
    def __init__(self, cv2: Any, path: Path, offset_s: float) -> None:
        self.cv2 = cv2
        self.path = path
        if not path.is_file():
            raise RuntimeError(f"demo source is missing: {path}")
        self.capture = cv2.VideoCapture(str(path))
        if not self.capture.isOpened():
            raise RuntimeError(f"demo source is not decodable: {path}")
        self.fps = float(self.capture.get(cv2.CAP_PROP_FPS) or 0.0)
        self.frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if self.fps <= 0 or self.frame_count <= 0:
            raise RuntimeError(f"demo source has invalid timing metadata: {path}")
        self.duration_s = self.frame_count / self.fps
        self.offset_s = offset_s % self.duration_s
        self.current_index = -1
        self.last_frame = None

    def _read_index(self, target_index: int) -> Any:
        if (
            self.current_index < 0
            or target_index < self.current_index
            or target_index - self.current_index > max(2, int(self.fps))
        ):
            self.capture.set(self.cv2.CAP_PROP_POS_FRAMES, target_index)
            ok, frame = self.capture.read()
            if not ok:
                raise RuntimeError(
                    f"demo source failed at frame {target_index}: {self.path}"
                )
            self.current_index = target_index
            self.last_frame = frame
            return frame

        while self.current_index < target_index:
            ok, frame = self.capture.read()
            if not ok:
                self.capture.set(self.cv2.CAP_PROP_POS_FRAMES, target_index)
                ok, frame = self.capture.read()
            if not ok:
                raise RuntimeError(
                    f"demo source failed at frame {target_index}: {self.path}"
                )
            self.current_index += 1
            self.last_frame = frame
        return self.last_frame

    def sample(self, elapsed_s: float, width: int, height: int) -> Any:
        source_s = (self.offset_s + elapsed_s) % self.duration_s
        target_index = min(self.frame_count - 1, int(source_s * self.fps))
        frame = self._read_index(target_index)
        source_height, source_width = frame.shape[:2]
        scale = max(width / source_width, height / source_height)
        resized_width = max(width, math.ceil(source_width * scale))
        resized_height = max(height, math.ceil(source_height * scale))
        interpolation = (
            self.cv2.INTER_AREA if scale < 1.0 else self.cv2.INTER_CUBIC
        )
        resized = self.cv2.resize(
            frame, (resized_width, resized_height), interpolation=interpolation
        )
        left = (resized_width - width) // 2
        top = (resized_height - height) // 2
        return resized[top : top + height, left : left + width].copy()

    def close(self) -> None:
        self.capture.release()


class FontBook:
    def __init__(self, image_font: Any, scale: float) -> None:
        self.image_font = image_font
        self.scale = scale
        self.paths = {
            "serif": STATIC / "fonts/source-serif-4-latin.woff2",
            "mono": STATIC / "fonts/jetbrains-mono-latin.woff2",
        }
        self.cache: dict[tuple[str, int], Any] = {}

    def get(self, family: str, design_size: float) -> Any:
        size = max(6, round(design_size * self.scale))
        key = (family, size)
        if key not in self.cache:
            self.cache[key] = self.image_font.truetype(str(self.paths[family]), size)
        return self.cache[key]


class DemoRenderer:
    PAPER = (246, 246, 239)
    WHITE = (255, 255, 255)
    INK = (19, 21, 19)
    INK_SOFT = (85, 89, 85)
    MUTED = (117, 122, 117)
    DARK = (15, 18, 16)
    DARK_SOFT = (27, 31, 28)
    GREEN = (68, 124, 86)
    GREEN_SOFT = (229, 238, 230)
    RUST = (153, 102, 83)
    BLUE = (61, 100, 112)
    HAIRLINE = (205, 207, 201)

    def __init__(
        self,
        *,
        width: int,
        height: int,
        manifest: dict[str, Any],
        publication: dict[str, Any],
        cv2: Any,
        np: Any,
        image: Any,
        image_draw: Any,
        image_font: Any,
    ) -> None:
        self.width = width
        self.height = height
        self.x_scale = width / 1920.0
        self.y_scale = height / 1080.0
        self.scale = min(self.x_scale, self.y_scale)
        self.manifest = manifest
        self.publication = publication
        self.cv2 = cv2
        self.np = np
        self.image = image
        self.image_draw = image_draw
        self.fonts = FontBook(image_font, self.scale)
        self.samplers = {
            source["id"]: VideoSampler(
                cv2, ROOT / source["path"], float(source["offset_s"])
            )
            for source in manifest["sources"]
        }
        self.sources = manifest["sources"]

    def x(self, value: float) -> int:
        return round(value * self.x_scale)

    def y(self, value: float) -> int:
        return round(value * self.y_scale)

    def s(self, value: float) -> int:
        return max(1, round(value * self.scale))

    @staticmethod
    def _bgr(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
        return rgb[2], rgb[1], rgb[0]

    def blank(self, rgb: tuple[int, int, int]) -> Any:
        frame = self.np.empty((self.height, self.width, 3), dtype=self.np.uint8)
        frame[:, :] = self._bgr(rgb)
        return frame

    def begin_draw(self, frame: Any) -> tuple[Any, Any]:
        rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        canvas = self.image.fromarray(rgb)
        return canvas, self.image_draw.Draw(canvas, "RGBA")

    def finish_draw(self, canvas: Any) -> Any:
        rgb = self.np.asarray(canvas)
        return self.cv2.cvtColor(rgb, self.cv2.COLOR_RGB2BGR)

    def edge_fade(self, frame: Any, progress: float) -> Any:
        edge = min(1.0, progress / 0.035, (1.0 - progress) / 0.035)
        edge = _smoothstep(edge)
        if edge >= 0.999:
            return frame
        dark = self.blank(self.DARK)
        return self.cv2.addWeighted(frame, edge, dark, 1.0 - edge, 0)

    def render(self, scene_id: str, progress: float) -> Any:
        if scene_id == "verified_tasks":
            frame = self.render_task_grid(progress)
        elif scene_id == "adaptive_evolution":
            frame = self.render_evolution(progress)
        elif scene_id == "matched_code":
            frame = self.render_matched_code(progress)
        elif scene_id == "end_slate":
            frame = self.render_end_slate(progress)
        else:
            raise RuntimeError(f"unknown demo scene: {scene_id}")
        return self.edge_fade(frame, progress)

    def render_task_grid(self, progress: float) -> Any:
        frame = self.blank(self.DARK)
        tile = self.s(300)
        gap = self.s(12)
        x0 = self.x(498)
        y0 = self.y(78)
        source_elapsed = progress * SCENES[0]["duration_s"]
        reveals = []
        for index, source in enumerate(self.sources):
            row, column = divmod(index, 3)
            left = x0 + column * (tile + gap)
            top = y0 + row * (tile + gap)
            sample = self.samplers[source["id"]].sample(source_elapsed, tile, tile)
            reveal = _smoothstep(progress * 2.0 - index * 0.055)
            if reveal < 1.0:
                dark_tile = self.np.full_like(sample, self._bgr(self.DARK_SOFT))
                sample = self.cv2.addWeighted(sample, reveal, dark_tile, 1.0 - reveal, 0)
            frame[top : top + tile, left : left + tile] = sample
            reveals.append((left, top, source, reveal))

        canvas, draw = self.begin_draw(frame)
        mono_10 = self.fonts.get("mono", 10)
        mono_12 = self.fonts.get("mono", 12)
        mono_14 = self.fonts.get("mono", 14)
        serif_30 = self.fonts.get("serif", 30)
        serif_62 = self.fonts.get("serif", 62)
        for left, top, source, reveal in reveals:
            if reveal <= 0.02:
                continue
            label_height = self.s(54)
            draw.rectangle(
                (left, top + tile - label_height, left + tile, top + tile),
                fill=(*self.DARK, 218),
            )
            draw.rectangle(
                (left, top, left + tile - 1, top + tile - 1),
                outline=(*self.WHITE, 115),
                width=self.s(1),
            )
            draw.ellipse(
                (
                    left + self.s(13),
                    top + tile - self.s(22),
                    left + self.s(19),
                    top + tile - self.s(16),
                ),
                fill=(*self.GREEN, 255),
            )
            draw.text(
                (left + self.s(28), top + tile - self.s(29)),
                source["label"],
                font=mono_12,
                fill=(*self.WHITE, 240),
            )
            draw.text(
                (left + tile - self.s(12), top + self.s(11)),
                source["platform"].upper(),
                font=mono_10,
                fill=(*self.WHITE, 210),
                anchor="ra",
            )

        draw.text(
            (self.x(64), self.y(61)),
            "01 / QUALITATIVE EVIDENCE",
            font=mono_12,
            fill=(*self.GREEN, 255),
        )
        draw.multiline_text(
            (self.x(64), self.y(104)),
            "Nine verified\nrobot tasks",
            font=serif_62,
            fill=(*self.WHITE, 245),
            spacing=self.s(4),
        )
        draw.line(
            (self.x(64), self.y(286), self.x(412), self.y(286)),
            fill=(*self.WHITE, 90),
            width=self.s(1),
        )
        draw.text(
            (self.x(64), self.y(324)),
            "6",
            font=serif_30,
            fill=(*self.WHITE, 245),
        )
        draw.text(
            (self.x(114), self.y(338)),
            "LIBERO",
            font=mono_14,
            fill=(*self.WHITE, 170),
        )
        draw.text(
            (self.x(64), self.y(380)),
            "3",
            font=serif_30,
            fill=(*self.WHITE, 245),
        )
        draw.text(
            (self.x(114), self.y(394)),
            "ROBOTWIN",
            font=mono_14,
            fill=(*self.WHITE, 170),
        )
        draw.text(
            (self.x(1475), self.y(82)),
            "FINAL VERDICT",
            font=mono_12,
            fill=(*self.GREEN, 255),
        )
        draw.text(
            (self.x(1475), self.y(121)),
            "9 / 9",
            font=serif_62,
            fill=(*self.WHITE, 245),
        )
        draw.multiline_text(
            (self.x(1475), self.y(217)),
            "Named success videos\nNative simulator or\npredicate authority",
            font=mono_14,
            fill=(*self.WHITE, 170),
            spacing=self.s(12),
        )
        draw.line(
            (self.x(1475), self.y(340), self.x(1840), self.y(340)),
            fill=(*self.WHITE, 90),
            width=self.s(1),
        )
        draw.text(
            (self.x(1475), self.y(902)),
            "QUALITATIVE EPISODES",
            font=mono_10,
            fill=(*self.RUST, 255),
        )
        draw.multiline_text(
            (self.x(1475), self.y(930)),
            "Examples are evidence\nfor named tasks, not a\nleaderboard denominator.",
            font=mono_12,
            fill=(*self.WHITE, 165),
            spacing=self.s(8),
        )
        draw.text(
            (self.x(64), self.y(1015)),
            "roborsi / native-success media archive",
            font=mono_10,
            fill=(*self.WHITE, 120),
        )
        return self.finish_draw(canvas)

    def render_evolution(self, progress: float) -> Any:
        frame = self.blank(self.PAPER)
        canvas, draw = self.begin_draw(frame)
        mono_11 = self.fonts.get("mono", 11)
        mono_13 = self.fonts.get("mono", 13)
        serif_24 = self.fonts.get("serif", 24)
        serif_46 = self.fonts.get("serif", 46)
        serif_72 = self.fonts.get("serif", 72)

        draw.text(
            (self.x(76), self.y(58)),
            "02 / SELF-EVOLUTION",
            font=mono_13,
            fill=(*self.GREEN, 255),
        )
        draw.text(
            (self.x(76), self.y(98)),
            "Reviewed experience expands task coverage",
            font=serif_46,
            fill=(*self.INK, 255),
        )
        draw.text(
            (self.x(78), self.y(166)),
            "Measured sequential adaptive rounds",
            font=mono_13,
            fill=(*self.MUTED, 255),
        )

        chart = (self.x(76), self.y(242), self.x(1302), self.y(858))
        draw.rectangle(chart, fill=(*self.WHITE, 255), outline=(*self.HAIRLINE, 255))
        plot_left = self.x(154)
        plot_right = self.x(1242)
        plot_top = self.y(302)
        plot_bottom = self.y(790)
        total = self.manifest["adaptive"]["total_tasks"]
        values = self.manifest["adaptive"]["coverage"]
        for tick in (0, 30, 60, 90, 120):
            y = round(plot_bottom - tick / total * (plot_bottom - plot_top))
            draw.line(
                (plot_left, y, plot_right, y),
                fill=(*self.HAIRLINE, 150),
                width=self.s(1),
            )
            draw.text(
                (plot_left - self.s(18), y),
                str(tick),
                font=mono_11,
                fill=(*self.MUTED, 255),
                anchor="rm",
            )

        base_points = []
        for index, value in enumerate(values):
            x = round(plot_left + index / (len(values) - 1) * (plot_right - plot_left))
            y = round(plot_bottom - value / total * (plot_bottom - plot_top))
            base_points.append((x, y))
            draw.text(
                (x, plot_bottom + self.s(25)),
                str(index + 1),
                font=mono_11,
                fill=(*self.MUTED, 255),
                anchor="ma",
            )

        reveal = _smoothstep(min(1.0, progress / 0.82))
        position = reveal * (len(values) - 1)
        index = min(len(values) - 1, int(position))
        fraction = position - index
        visible_points = base_points[: index + 1]
        current_value = float(values[index])
        current_round = index + 1
        if index < len(values) - 1 and fraction > 0:
            x0, y0 = base_points[index]
            x1, y1 = base_points[index + 1]
            visible_points.append(
                (round(x0 + fraction * (x1 - x0)), round(y0 + fraction * (y1 - y0)))
            )
            current_value += fraction * (values[index + 1] - values[index])
            current_round = index + 1 + fraction

        area = [(visible_points[0][0], plot_bottom), *visible_points]
        area.append((visible_points[-1][0], plot_bottom))
        draw.polygon(area, fill=(*self.GREEN_SOFT, 235))
        if len(visible_points) > 1:
            draw.line(visible_points, fill=(*self.GREEN, 255), width=self.s(5), joint="curve")
        for point in base_points[: index + 1]:
            radius = self.s(6)
            draw.ellipse(
                (point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius),
                fill=(*self.WHITE, 255),
                outline=(*self.GREEN, 255),
                width=self.s(3),
            )
        last_x, last_y = visible_points[-1]
        radius = self.s(8)
        draw.ellipse(
            (last_x - radius, last_y - radius, last_x + radius, last_y + radius),
            fill=(*self.GREEN, 255),
        )
        draw.text(
            (plot_left, self.y(822)),
            "ADAPTIVE ROUND",
            font=mono_11,
            fill=(*self.MUTED, 255),
        )

        right_x = self.x(1390)
        draw.text(
            (right_x, self.y(246)),
            f"{round(current_value)} / 120",
            font=serif_72,
            fill=(*self.INK, 255),
        )
        draw.text(
            (right_x, self.y(336)),
            f"ROUND {max(1, math.ceil(current_round))} / 10",
            font=mono_13,
            fill=(*self.GREEN, 255),
        )
        stages = (
            ("01", "Observe", "RGB-D + visible trace"),
            ("02", "Diagnose", "Planner / Engineer / Reviewer"),
            ("03", "Solidify", "successful behavior to code"),
            ("04", "Reuse", "next tasks inherit the skill"),
        )
        active_stage = min(3, int(progress * 4))
        for stage_index, (number, label, detail) in enumerate(stages):
            top = self.y(405 + stage_index * 112)
            stage_color = self.RUST if stage_index == active_stage else self.MUTED
            if stage_index == active_stage:
                draw.rectangle(
                    (right_x - self.s(12), top - self.s(13), self.x(1842), top + self.s(72)),
                    fill=(*self.GREEN_SOFT, 255),
                )
            draw.text(
                (right_x, top),
                number,
                font=mono_11,
                fill=(*stage_color, 255),
            )
            draw.text(
                (right_x + self.s(48), top - self.s(5)),
                label,
                font=serif_24,
                fill=(*self.INK, 255),
            )
            draw.text(
                (right_x + self.s(48), top + self.s(35)),
                detail,
                font=mono_11,
                fill=(*self.MUTED, 255),
            )
            if stage_index < len(stages) - 1:
                draw.line(
                    (
                        right_x + self.s(12),
                        top + self.s(78),
                        right_x + self.s(12),
                        top + self.s(96),
                    ),
                    fill=(*self.HAIRLINE, 255),
                    width=self.s(1),
                )

        draw.line(
            (self.x(76), self.y(922), self.x(1842), self.y(922)),
            fill=(*self.HAIRLINE, 255),
            width=self.s(1),
        )
        draw.text(
            (self.x(76), self.y(954)),
            ADAPTIVE_CAPTION,
            font=mono_13,
            fill=(*self.INK_SOFT, 255),
        )
        if progress > 0.68:
            alpha = round(255 * _smoothstep((progress - 0.68) / 0.18))
            draw.text(
                (self.x(1842), self.y(1000)),
                "Later locked releases extend cross-release coverage to 95/120.",
                font=mono_11,
                fill=(*self.BLUE, alpha),
                anchor="ra",
            )
        return self.finish_draw(canvas)

    def render_matched_code(self, progress: float) -> Any:
        frame = self.blank(self.DARK)
        video_left = self.x(76)
        video_top = self.y(214)
        video_size = self.s(760)
        source_elapsed = progress * SCENES[2]["duration_s"]
        video = self.samplers["adaptive-black-bowl-plate"].sample(
            source_elapsed, video_size, video_size
        )
        frame[
            video_top : video_top + video_size,
            video_left : video_left + video_size,
        ] = video

        canvas, draw = self.begin_draw(frame)
        mono_10 = self.fonts.get("mono", 10)
        mono_12 = self.fonts.get("mono", 12)
        mono_16 = self.fonts.get("mono", 16)
        serif_25 = self.fonts.get("serif", 25)
        serif_46 = self.fonts.get("serif", 46)
        draw.text(
            (self.x(76), self.y(58)),
            "03 / MATCHED CODE-ON/OFF",
            font=mono_12,
            fill=(*self.GREEN, 255),
        )
        draw.text(
            (self.x(76), self.y(98)),
            "Solidified code improves outcomes and cost",
            font=serif_46,
            fill=(*self.WHITE, 245),
        )
        draw.rectangle(
            (
                video_left,
                video_top,
                video_left + video_size - 1,
                video_top + video_size - 1,
            ),
            outline=(*self.WHITE, 125),
            width=self.s(1),
        )
        label_height = self.s(82)
        draw.rectangle(
            (
                video_left,
                video_top + video_size - label_height,
                video_left + video_size,
                video_top + video_size,
            ),
            fill=(*self.DARK, 224),
        )
        draw.text(
            (video_left + self.s(22), video_top + video_size - self.s(58)),
            "ILLUSTRATIVE CODE-BACKED SUCCESS",
            font=mono_10,
            fill=(*self.GREEN, 255),
        )
        draw.text(
            (video_left + self.s(22), video_top + video_size - self.s(34)),
            "libero_spatial_swap/1 / seed 14 / native simulator success",
            font=mono_12,
            fill=(*self.WHITE, 210),
        )

        matched = self.publication["experiments"]["matched_code"]
        efficiency = matched["efficiency"]
        on_success = matched["success"]["code_on"]["success"] / 600
        off_success = matched["success"]["code_off"]["success"] / 600
        rows = (
            {
                "label": "EPISODE SUCCESS",
                "value": "29.0% vs 21.5%",
                "delta": "+7.5 pp",
                "on": on_success / 0.35,
                "off": off_success / 0.35,
            },
            {
                "label": "MEDIAN TOKENS",
                "value": "2.58M vs 3.65M",
                "delta": "-29.4%",
                "on": (
                    efficiency["median_total_tokens"]["code_on"]
                    / efficiency["median_total_tokens"]["code_off"]
                ),
                "off": 1.0,
            },
            {
                "label": "MEDIAN VLM CALLS",
                "value": "29.5 vs 40.5",
                "delta": "-27.2%",
                "on": (
                    efficiency["median_vlm_calls"]["code_on"]
                    / efficiency["median_vlm_calls"]["code_off"]
                ),
                "off": 1.0,
            },
            {
                "label": "MEDIAN WALL TIME",
                "value": "701s vs 845s",
                "delta": "-17.0%",
                "on": (
                    efficiency["median_wall_s"]["code_on"]
                    / efficiency["median_wall_s"]["code_off"]
                ),
                "off": 1.0,
            },
        )
        right_left = self.x(988)
        right_right = self.x(1842)
        draw.multiline_text(
            (right_left, self.y(184)),
            "Code-on exposes the solidified visual_pick_place compound.\n"
            "Code-off keeps model, release, tasks, seeds, base tools, and budget matched.",
            font=mono_12,
            fill=(*self.WHITE, 165),
            spacing=self.s(7),
        )
        bar_left = right_left
        bar_right = right_right - self.s(122)
        for index, row in enumerate(rows):
            top = self.y(300 + index * 157)
            reveal = _smoothstep((progress - 0.06 - index * 0.13) / 0.22)
            draw.line(
                (right_left, top - self.s(24), right_right, top - self.s(24)),
                fill=(*self.WHITE, 55),
                width=self.s(1),
            )
            draw.text(
                (right_left, top),
                row["label"],
                font=mono_12,
                fill=(*self.WHITE, round(150 + 90 * reveal)),
            )
            draw.text(
                (right_left, top + self.s(31)),
                row["value"],
                font=serif_25,
                fill=(*self.WHITE, round(155 + 90 * reveal)),
            )
            draw.text(
                (right_right, top + self.s(31)),
                row["delta"],
                font=mono_16,
                fill=(*self.GREEN, round(120 + 135 * reveal)),
                anchor="ra",
            )
            track_width = bar_right - bar_left
            off_width = round(track_width * row["off"] * reveal)
            on_width = round(track_width * row["on"] * reveal)
            draw.rectangle(
                (bar_left, top + self.s(77), bar_left + off_width, top + self.s(85)),
                fill=(*self.WHITE, 72),
            )
            draw.rectangle(
                (bar_left, top + self.s(94), bar_left + on_width, top + self.s(106)),
                fill=(*self.GREEN, 255),
            )
            draw.text(
                (bar_right + self.s(20), top + self.s(75)),
                "OFF",
                font=mono_10,
                fill=(*self.WHITE, 110),
            )
            draw.text(
                (bar_right + self.s(20), top + self.s(95)),
                "ON",
                font=mono_10,
                fill=(*self.GREEN, 255),
            )

        draw.line(
            (self.x(76), self.y(1013), self.x(1842), self.y(1013)),
            fill=(*self.WHITE, 65),
            width=self.s(1),
        )
        draw.text(
            (self.x(76), self.y(1039)),
            MATCHED_CAPTION,
            font=mono_12,
            fill=(*self.WHITE, 150),
        )
        return self.finish_draw(canvas)

    def render_end_slate(self, progress: float) -> Any:
        frame = self.blank(self.DARK)
        source_ids = (
            "strict-moka-pot-stove",
            "adaptive-black-bowl-plate",
            "robotwin-place-container-plate-seed21",
        )
        column_width = math.ceil(self.width / 3)
        source_elapsed = progress * SCENES[3]["duration_s"]
        for index, source_id in enumerate(source_ids):
            left = index * column_width
            width = min(column_width, self.width - left)
            sample = self.samplers[source_id].sample(source_elapsed, width, self.height)
            frame[:, left : left + width] = sample
        dark = self.blank(self.DARK)
        frame = self.cv2.addWeighted(frame, 0.25, dark, 0.75, 0)

        canvas, draw = self.begin_draw(frame)
        mono_13 = self.fonts.get("mono", 13)
        mono_18 = self.fonts.get("mono", 18)
        serif_138 = self.fonts.get("serif", 138)
        draw.rectangle(
            (self.x(390), self.y(310), self.x(1530), self.y(770)),
            fill=(*self.DARK, 210),
            outline=(*self.WHITE, 52),
            width=self.s(1),
        )
        draw.text(
            (self.x(960), self.y(387)),
            "SIMULATOR-VERIFIED ROBOT SELF-IMPROVEMENT",
            font=mono_13,
            fill=(*self.GREEN, 255),
            anchor="ma",
        )
        draw.text(
            (self.x(960), self.y(448)),
            "roborsi",
            font=serif_138,
            fill=(*self.WHITE, 245),
            anchor="ma",
        )
        draw.line(
            (self.x(650), self.y(625), self.x(1270), self.y(625)),
            fill=(*self.WHITE, 85),
            width=self.s(1),
        )
        draw.text(
            (self.x(960), self.y(664)),
            "verified experience to inspectable code",
            font=mono_18,
            fill=(*self.WHITE, 185),
            anchor="ma",
        )
        draw.text(
            (self.x(960), self.y(721)),
            "robo-rsi.com",
            font=mono_13,
            fill=(*self.WHITE, 225),
            anchor="ma",
        )
        return self.finish_draw(canvas)

    def close(self) -> None:
        for sampler in self.samplers.values():
            sampler.close()


def _validate_render_options(args: argparse.Namespace) -> None:
    if args.width < 320 or args.height < 180:
        raise ValueError("width and height must be at least 320 x 180")
    if args.width % 2 or args.height % 2:
        raise ValueError("width and height must be even for yuv420p")
    if abs(args.width / args.height - 16 / 9) > 0.01:
        raise ValueError("the demo renderer requires a 16:9 frame")
    if args.fps <= 0:
        raise ValueError("fps must be positive")
    if not 0 < args.duration_scale <= 1:
        raise ValueError("duration-scale must be in (0, 1]")
    if not 0 <= args.crf <= 51:
        raise ValueError("crf must be between 0 and 51")


def render_demo(args: argparse.Namespace, manifest: dict[str, Any]) -> None:
    try:
        import cv2
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError(
            "rendering requires OpenCV, NumPy, and Pillow; install the runtime extra"
        ) from exc

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to render the demo")
    publication, _robotwin = _load_evidence()
    renderer = DemoRenderer(
        width=args.width,
        height=args.height,
        manifest=manifest,
        publication=publication,
        cv2=cv2,
        np=np,
        image=Image,
        image_draw=ImageDraw,
        image_font=ImageFont,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.poster.parent.mkdir(parents=True, exist_ok=True)
    temporary_video = args.output.with_name(f"{args.output.stem}.tmp{args.output.suffix}")
    temporary_poster = args.poster.with_name(f"{args.poster.stem}.tmp{args.poster.suffix}")
    command = [
        ffmpeg,
        "-y",
        "-v",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "bgr24",
        "-s:v",
        f"{args.width}x{args.height}",
        "-r",
        str(args.fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        args.preset,
        "-crf",
        str(args.crf),
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(temporary_video),
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=16 * 1024 * 1024,
    )
    if process.stdin is None or process.stderr is None:
        renderer.close()
        raise RuntimeError("failed to open the FFmpeg render pipe")

    scaled_scenes = [
        {**scene, "scaled_duration_s": scene["duration_s"] * args.duration_scale}
        for scene in manifest["scenes"]
    ]
    total_duration = manifest["duration_s"] * args.duration_scale
    total_frames = max(1, round(total_duration * args.fps))
    poster_frame = None
    next_progress_report = 0
    try:
        for frame_index in range(total_frames):
            timestamp = (frame_index + 0.5) / args.fps
            cursor = 0.0
            selected = scaled_scenes[-1]
            progress = 1.0
            for scene in scaled_scenes:
                end = cursor + scene["scaled_duration_s"]
                if timestamp < end:
                    selected = scene
                    progress = (timestamp - cursor) / scene["scaled_duration_s"]
                    break
                cursor = end
            progress = max(0.0, min(1.0, progress))
            frame = renderer.render(selected["id"], progress)
            if poster_frame is None and timestamp >= scaled_scenes[0]["scaled_duration_s"] * 0.55:
                poster_frame = frame.copy()
            try:
                process.stdin.write(frame.tobytes())
            except BrokenPipeError as exc:
                stderr = process.stderr.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"FFmpeg render pipe failed: {stderr.strip()}") from exc
            percent = int(100 * (frame_index + 1) / total_frames)
            if percent >= next_progress_report:
                print(f"demo render {percent:3d}%", file=sys.stderr, flush=True)
                next_progress_report += 10
        process.stdin.close()
        stderr = process.stderr.read().decode("utf-8", errors="replace")
        returncode = process.wait()
        if returncode != 0:
            raise RuntimeError(f"FFmpeg exited {returncode}: {stderr.strip()}")
        if poster_frame is None:
            poster_frame = renderer.render("verified_tasks", 0.55)
        if not cv2.imwrite(
            str(temporary_poster),
            poster_frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 94],
        ):
            raise RuntimeError(f"failed to write demo poster: {temporary_poster}")
        temporary_video.replace(args.output)
        temporary_poster.replace(args.poster)
    except Exception:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        raise
    finally:
        renderer.close()
    print(
        f"wrote {args.output} ({total_frames} frames, {total_frames / args.fps:.2f}s)",
        file=sys.stderr,
    )
    print(f"wrote {args.poster}", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--poster", type=Path, default=DEFAULT_POSTER)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--duration-scale", type=float, default=1.0)
    parser.add_argument("--crf", type=int, default=19)
    parser.add_argument("--preset", default="medium")
    parser.add_argument("--print-manifest", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_manifest()
    if args.print_manifest:
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    try:
        _validate_render_options(args)
        render_demo(args, manifest)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
