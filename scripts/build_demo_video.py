#!/usr/bin/env python3
"""Render the narrated roborsi evidence film with Remotion."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src/robohermes_libero/static"
REMOTION = ROOT / "remotion"
VOICEOVER_PATH = REMOTION / "voiceover.json"
REMOTION_VERSION = "4.0.517"
DEFAULT_OUTPUT = STATIC / "media/demo/roborsi-demo.mp4"
DEFAULT_POSTER = STATIC / "media/demo/roborsi-demo-poster.jpg"
DEFAULT_ZH_OUTPUT = STATIC / "media/demo/roborsi-demo-zh.mp4"
DEFAULT_ZH_POSTER = STATIC / "media/demo/roborsi-demo-zh-poster.jpg"
ADAPTIVE_CAPTION = (
    "Cross-release adaptive development coverage; not fixed-policy Pass@10."
)
MATCHED_CAPTION = (
    "Matched Code-on/off results. Video illustrates code-backed execution."
)
BEFORE_AFTER_CAPTION = (
    "Same task and seed; videos use normalized episode progress. "
    "The aggregate coverage curve is a separate cross-release measure."
)
SCENES = (
    {"id": "intro", "duration_s": 7.0},
    {"id": "verified_tasks", "duration_s": 15.0},
    {"id": "adaptive_evolution", "duration_s": 16.0},
    {"id": "matched_code", "duration_s": 16.0},
    {"id": "end_slate", "duration_s": 6.0},
)
SOURCE_SPECS = (
    {
        "id": "strict-moka-pot-stove",
        "label": "Moka pot to stove",
        "label_zh": "将摩卡壶放到炉灶上",
        "platform": "LIBERO",
        "offset_s": 2.0,
    },
    {
        "id": "strict-ketchup-basket",
        "label": "Ketchup to basket",
        "label_zh": "将番茄酱放入篮筐",
        "platform": "LIBERO",
        "offset_s": 1.0,
    },
    {
        "id": "strict-pudding-basket",
        "label": "Pudding to basket",
        "label_zh": "将布丁放入篮筐",
        "platform": "LIBERO",
        "offset_s": 1.5,
    },
    {
        "id": "strict-bowl-tray",
        "label": "Black bowl to tray",
        "label_zh": "将黑碗放入托盘",
        "platform": "LIBERO",
        "offset_s": 1.0,
    },
    {
        "id": "adaptive-black-bowl-plate",
        "label": "Black bowl to plate",
        "label_zh": "将黑碗放到盘子上",
        "platform": "LIBERO",
        "offset_s": 0.5,
    },
    {
        "id": "act-corrective-transport",
        "label": "ACT transport",
        "label_zh": "ACT 搬运",
        "platform": "LIBERO",
        "offset_s": 0.3,
    },
    {
        "id": "robotwin-grab-roller-seed22",
        "label": "Grab roller",
        "label_zh": "抓取滚筒",
        "platform": "RoboTwin",
        "offset_s": 18.0,
    },
    {
        "id": "robotwin-place-container-plate-seed21",
        "label": "Container to plate",
        "label_zh": "将容器放到盘子上",
        "platform": "RoboTwin",
        "offset_s": 18.0,
    },
    {
        "id": "robotwin-turn-switch-seed23",
        "label": "Turn switch",
        "label_zh": "拨动开关",
        "platform": "RoboTwin",
        "offset_s": 12.0,
    },
    {
        "id": "plus-camera-black-bowl-plate",
        "label": "Camera shift",
        "label_zh": "相机视角变化",
        "platform": "LIBERO",
        "offset_s": 0.0,
    },
    {
        "id": "plus-light-ketchup-basket",
        "label": "Low-light ketchup",
        "label_zh": "低照度番茄酱任务",
        "platform": "LIBERO",
        "offset_s": 0.0,
    },
    {
        "id": "plus-layout-black-bowl-plate",
        "label": "Layout shift",
        "label_zh": "物体布局变化",
        "platform": "LIBERO",
        "offset_s": 0.0,
    },
    {
        "id": "plus-init-black-bowl-plate",
        "label": "Initial-state shift",
        "label_zh": "机器人初始状态变化",
        "platform": "LIBERO",
        "offset_s": 0.0,
    },
    {
        "id": "act-before-corrective",
        "label": "ACT before repair",
        "label_zh": "ACT 修复前",
        "platform": "ACT",
        "offset_s": 0.0,
    },
)
GRID_PAGES = (
    tuple(spec["id"] for spec in SOURCE_SPECS[:9]),
    (
        "plus-camera-black-bowl-plate",
        "plus-light-ketchup-basket",
        "plus-layout-black-bowl-plate",
        "plus-init-black-bowl-plate",
        "strict-moka-pot-stove",
        "strict-pudding-basket",
        "adaptive-black-bowl-plate",
        "act-corrective-transport",
        "robotwin-turn-switch-seed23",
    ),
)


def _load_evidence() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    publication = json.loads(
        (ROOT / "evidence/publication-v1/experiments.json").read_text(
            encoding="utf-8"
        )
    )
    robotwin = json.loads(
        (ROOT / "evidence/publication-v1/robotwin_historical.json").read_text(
            encoding="utf-8"
        )
    )
    libero_plus = json.loads(
        (ROOT / "evidence/publication-v1/libero_plus_final.json").read_text(
            encoding="utf-8"
        )
    )
    return publication, robotwin, libero_plus


def _load_voiceover() -> dict[str, Any]:
    return json.loads(VOICEOVER_PATH.read_text(encoding="utf-8"))


def build_manifest(language: str = "en") -> dict[str, Any]:
    publication, robotwin, libero_plus = _load_evidence()
    voiceover = _load_voiceover()
    publication_media = publication["media"]["videos"]
    robotwin_media = robotwin["media"]["videos"]
    plus_media = libero_plus["media"]["videos"]
    act_before = publication["experiments"]["act"]["before_after"]["before"]
    records = {
        row["id"]: row
        for row in (*publication_media, *robotwin_media, *plus_media, act_before)
    }
    sources = []
    for spec in SOURCE_SPECS:
        record = records[spec["id"]]
        if record["verdict"] == "simulator_failure":
            verdict = "native_simulator_failure"
        elif spec["platform"] == "RoboTwin":
            verdict = "native_predicate_success"
        else:
            verdict = "native_simulator_success"
        sources.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "label_zh": spec["label_zh"],
                "platform": spec["platform"],
                "task": record["task"],
                "seed": record["seed"],
                "path": str(Path("src/robohermes_libero/static") / record["video"]),
                "duration_s": record["duration_s"],
                "offset_s": spec["offset_s"],
                "verdict": verdict,
            }
        )

    adaptive = publication["experiments"]["adaptive_sequential"]
    matched = publication["experiments"]["matched_code"]
    return {
        "schema": "roborsi.evidence_demo.v2",
        "renderer": {
            "engine": "remotion",
            "version": REMOTION_VERSION,
            "entry": "remotion/src/index.ts",
            "composition": "RoborsiDemo",
        },
        "language": language,
        "fonts": {
            "latin_serif": (
                "src/robohermes_libero/static/fonts/source-serif-4-latin.woff2"
            ),
            "latin_mono": (
                "src/robohermes_libero/static/fonts/jetbrains-mono-latin.woff2"
            ),
            "cjk": "src/robohermes_libero/static/fonts/wqy-microhei.ttc",
        },
        "duration_s": sum(scene["duration_s"] for scene in SCENES),
        "master": {"width": 1920, "height": 1080, "fps": 30, "audio": True},
        "scenes": [dict(scene) for scene in SCENES],
        "sources": sources,
        "task_grid": {
            "layout": "3x3",
            "pages": [list(page) for page in GRID_PAGES],
            "unique_success_sources": len(set().union(*map(set, GRID_PAGES))),
        },
        "adaptive": {
            "coverage": adaptive["pass_curve"],
            "total_tasks": adaptive["total_tasks"],
            "caption": (
                "跨版本自适应开发覆盖率；并非固定策略 Pass@10。"
                if language == "zh"
                else ADAPTIVE_CAPTION
            ),
        },
        "before_after": {
            "task": "libero_spatial_swap/0",
            "seed": 3,
            "time_alignment": "normalized_episode_progress",
            "before": {
                "id": "act-before-corrective",
                "transport_steps": 120,
                "verdict": "native_simulator_failure",
            },
            "after": {
                "id": "act-corrective-transport",
                "transport_steps": 304,
                "verdict": "native_simulator_success",
            },
            "caption": (
                "同一任务与随机种子；视频按归一化回合进度对齐。"
                "覆盖率曲线为独立的跨版本统计。"
                if language == "zh"
                else BEFORE_AFTER_CAPTION
            ),
        },
        "matched_code": {
            "episode_success_delta_pp": matched["success"]["paired_delta_pp"],
            "median_token_reduction_pct": round(
                100 * matched["efficiency"]["median_total_tokens"]["reduction"],
                1,
            ),
            "median_vlm_call_reduction_pct": round(
                100 * matched["efficiency"]["median_vlm_calls"]["reduction"],
                1,
            ),
            "median_wall_reduction_pct": round(
                100 * matched["efficiency"]["median_wall_s"]["reduction"],
                1,
            ),
            "caption": (
                "Code-on/off 为配对实验；视频仅展示代码技能的执行过程。"
                if language == "zh"
                else MATCHED_CAPTION
            ),
        },
        "voiceover": {
            "preferred_provider": voiceover["preferred_provider"],
            "generated_provider": voiceover["generated_provider"],
            "model_id": voiceover["model_id"],
            "voice_id": voiceover["voice_id"],
            "output_format": voiceover["output_format"],
            "segments": [
                row["id"] for row in voiceover["languages"][language]
            ],
        },
    }


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


def _render_props(args: argparse.Namespace, manifest: dict[str, Any]) -> dict[str, Any]:
    voiceover = _load_voiceover()
    narration = voiceover["languages"][args.language]
    for segment in narration:
        audio = STATIC / segment["audio"]
        captions = STATIC / segment["captions"]
        if not audio.is_file() or audio.stat().st_size < 10_000:
            raise RuntimeError(
                f"missing narration audio: {audio.relative_to(ROOT)}; "
                "run scripts/generate_voiceover.py"
            )
        if not captions.is_file():
            raise RuntimeError(f"missing captions: {captions.relative_to(ROOT)}")
    return {
        "language": args.language,
        "width": args.width,
        "height": args.height,
        "fps": args.fps,
        "durationScale": args.duration_scale,
        "manifest": manifest,
        "narration": narration,
    }


def _run_remotion(command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=REMOTION,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Remotion command exited with status {result.returncode}"
        )


def _normalize_release_video(
    source: Path,
    destination: Path,
    *,
    crf: int,
    preset: str,
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required to finalize the Remotion render")
    result = subprocess.run(
        [
            ffmpeg,
            "-nostdin",
            "-y",
            "-v",
            "error",
            "-i",
            str(source),
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-pix_fmt",
            "yuv420p",
            "-colorspace",
            "bt709",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
            "-color_range",
            "tv",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(destination),
        ],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg finalization exited with status {result.returncode}"
        )


def render_demo(args: argparse.Namespace, manifest: dict[str, Any]) -> None:
    executable = REMOTION / "node_modules/.bin/remotion"
    if not executable.is_file():
        raise RuntimeError("Remotion dependencies are missing; run npm install in remotion/")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.poster.parent.mkdir(parents=True, exist_ok=True)
    props = _render_props(args, manifest)
    with tempfile.TemporaryDirectory(prefix="roborsi-remotion-") as temporary:
        raw_video = Path(temporary) / "remotion-raw.mp4"
        props_path = Path(temporary) / "props.json"
        props_path.write_text(
            json.dumps(props, ensure_ascii=False),
            encoding="utf-8",
        )
        video_command = [
            str(executable),
            "render",
            "src/index.ts",
            "RoborsiDemo",
            str(raw_video),
            f"--props={props_path}",
            "--codec=h264",
            "--pixel-format=yuv420p",
            "--audio-codec=aac",
            "--audio-bitrate=128k",
            f"--crf={args.crf}",
            "--concurrency=4",
            "--overwrite",
            "--log=error",
        ]
        _run_remotion(video_command)
        _normalize_release_video(
            raw_video,
            args.output.resolve(),
            crf=args.crf,
            preset=args.preset,
        )

        poster_frame = round(
            (
                SCENES[0]["duration_s"]
                + SCENES[1]["duration_s"] * 0.55
            )
            * args.duration_scale
            * args.fps
        )
        still_command = [
            str(executable),
            "still",
            "src/index.ts",
            "RoborsiDemo",
            str(args.poster.resolve()),
            f"--props={props_path}",
            f"--frame={poster_frame}",
            "--image-format=jpeg",
            "--overwrite",
            "--log=error",
        ]
        _run_remotion(still_command)
    print(
        f"wrote {args.output} "
        f"({manifest['duration_s'] * args.duration_scale:.2f}s, Remotion)",
        file=sys.stderr,
    )
    print(f"wrote {args.poster}", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("en", "zh"), default="en")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--poster", type=Path)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--duration-scale", type=float, default=1.0)
    parser.add_argument("--crf", type=int, default=19)
    parser.add_argument("--preset", default="medium")
    parser.add_argument("--print-manifest", action="store_true")
    args = parser.parse_args()
    if args.output is None:
        args.output = DEFAULT_ZH_OUTPUT if args.language == "zh" else DEFAULT_OUTPUT
    if args.poster is None:
        args.poster = DEFAULT_ZH_POSTER if args.language == "zh" else DEFAULT_POSTER
    return args


def main() -> int:
    args = parse_args()
    manifest = build_manifest(args.language)
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
