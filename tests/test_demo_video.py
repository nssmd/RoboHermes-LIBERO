from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_demo_video.py"


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_demo_manifest_has_nine_verified_sources_and_bounded_claims() -> None:
    result = _run("--print-manifest")

    assert result.returncode == 0, result.stderr
    manifest = json.loads(result.stdout)
    sources = manifest["sources"]
    paths = [row["path"] for row in sources]
    assert len(sources) == 9
    assert len(set(paths)) == 9
    assert all((ROOT / path).is_file() for path in paths)
    assert {row["platform"] for row in sources} == {"LIBERO", "RoboTwin"}
    assert {row["verdict"] for row in sources} == {
        "native_simulator_success",
        "native_predicate_success",
    }

    assert manifest["duration_s"] == 39.0
    assert sum(scene["duration_s"] for scene in manifest["scenes"]) == 39.0
    assert manifest["adaptive"] == {
        "coverage": [32, 45, 52, 66, 71, 76, 81, 82, 82, 83],
        "total_tasks": 120,
        "caption": (
            "Cross-release adaptive development coverage; "
            "not fixed-policy Pass@10."
        ),
    }
    assert manifest["evolution_video"] == {
        "phases": [
            {"id": "explore", "sources": ["strict-moka-pot-stove"]},
            {"id": "solidify", "sources": ["adaptive-black-bowl-plate"]},
            {
                "id": "reuse",
                "sources": [
                    "strict-ketchup-basket",
                    "strict-bowl-tray",
                    "strict-pudding-basket",
                    "act-corrective-transport",
                ],
            },
        ],
        "caption": (
            "Representative rollout footage synchronized to measured coverage; "
            "not a paired same-task comparison."
        ),
    }
    assert manifest["matched_code"] == {
        "episode_success_delta_pp": 7.5,
        "median_token_reduction_pct": 29.4,
        "median_vlm_call_reduction_pct": 27.2,
        "median_wall_reduction_pct": 17.0,
        "caption": (
            "Matched Code-on/off panels. "
            "Video illustrates code-backed execution."
        ),
    }


def test_demo_smoke_render_is_complete_h264_with_distinct_scenes(tmp_path: Path) -> None:
    cv2 = pytest.importorskip("cv2")
    np = pytest.importorskip("numpy")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        pytest.skip("FFmpeg and FFprobe are required for the demo smoke render")

    output = tmp_path / "demo.mp4"
    poster = tmp_path / "demo-poster.jpg"
    result = _run(
        "--output",
        str(output),
        "--poster",
        str(poster),
        "--width",
        "480",
        "--height",
        "270",
        "--fps",
        "6",
        "--duration-scale",
        "0.1",
    )

    assert result.returncode == 0, result.stderr
    assert output.stat().st_size > 20_000
    assert poster.stat().st_size > 5_000

    probe = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(probe.stdout)
    video_streams = [row for row in metadata["streams"] if row["codec_type"] == "video"]
    audio_streams = [row for row in metadata["streams"] if row["codec_type"] == "audio"]
    assert len(video_streams) == 1
    assert audio_streams == []
    stream = video_streams[0]
    assert stream["codec_name"] == "h264"
    assert stream["pix_fmt"] == "yuv420p"
    assert (stream["width"], stream["height"]) == (480, 270)
    assert 3.7 <= float(metadata["format"]["duration"]) <= 4.2

    decode = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(output), "-f", "null", "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert decode.returncode == 0, decode.stderr

    capture = cv2.VideoCapture(str(output))
    samples = []
    for timestamp_s in (0.6, 1.8, 2.9, 3.65):
        capture.set(cv2.CAP_PROP_POS_MSEC, timestamp_s * 1000)
        ok, frame = capture.read()
        assert ok, timestamp_s
        assert float(frame.std()) > 12.0, timestamp_s
        samples.append(frame.astype(np.float32))
    capture.release()
    for left, right in zip(samples, samples[1:]):
        assert float(np.mean(np.abs(left - right))) > 8.0

    evolution_frames = []
    for timestamp_s in (1.35, 1.75, 2.2):
        capture = cv2.VideoCapture(str(output))
        capture.set(cv2.CAP_PROP_POS_MSEC, timestamp_s * 1000)
        ok, frame = capture.read()
        capture.release()
        assert ok, timestamp_s
        height, width = frame.shape[:2]
        video_region = frame[
            round(0.22 * height) : round(0.80 * height),
            round(0.04 * width) : round(0.51 * width),
        ]
        assert float(video_region.std()) > 20.0, timestamp_s
        evolution_frames.append(video_region.astype(np.float32))
    for left, right in zip(evolution_frames, evolution_frames[1:]):
        assert float(np.mean(np.abs(left - right))) > 15.0

    poster_frame = cv2.imread(str(poster))
    assert poster_frame is not None
    assert poster_frame.shape[:2] == (270, 480)
    assert float(poster_frame.std()) > 12.0
