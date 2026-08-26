from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_demo_video.py"
REMOTION = ROOT / "remotion"
STATIC = ROOT / "src/robohermes_libero/static"


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_demo_manifest_has_rotating_grid_and_matched_before_after() -> None:
    result = _run("--print-manifest")

    assert result.returncode == 0, result.stderr
    manifest = json.loads(result.stdout)
    sources = manifest["sources"]
    paths = [row["path"] for row in sources]
    assert len(sources) == 14
    assert len(set(paths)) == 14
    assert all((ROOT / path).is_file() for path in paths)
    assert {row["platform"] for row in sources} == {"ACT", "LIBERO", "RoboTwin"}
    assert {row["verdict"] for row in sources} == {
        "native_simulator_failure",
        "native_simulator_success",
        "native_predicate_success",
    }

    task_grid = manifest["task_grid"]
    assert task_grid["layout"] == "3x3"
    assert len(task_grid["pages"]) == 2
    assert all(len(page) == 9 for page in task_grid["pages"])
    assert len(set().union(*map(set, task_grid["pages"]))) == 13
    assert "act-before-corrective" not in set().union(*map(set, task_grid["pages"]))

    assert manifest["renderer"] == {
        "engine": "remotion",
        "version": "4.0.517",
        "entry": "remotion/src/index.ts",
        "composition": "RoborsiDemo",
    }
    assert manifest["duration_s"] == 60.0
    assert sum(scene["duration_s"] for scene in manifest["scenes"]) == 60.0
    assert manifest["master"]["audio"] is True
    assert manifest["voiceover"] == {
        "preferred_provider": "elevenlabs",
        "generated_provider": manifest["voiceover"]["generated_provider"],
        "model_id": "eleven_v3",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "output_format": "mp3_44100_128",
        "segments": [
            "intro",
            "verified_tasks",
            "adaptive_evolution",
            "matched_code",
            "end_slate",
        ],
    }
    assert manifest["voiceover"]["generated_provider"] in {"elevenlabs", "edge"}
    assert manifest["adaptive"] == {
        "coverage": [32, 45, 52, 66, 71, 76, 81, 82, 82, 83],
        "total_tasks": 120,
        "caption": (
            "Cross-release adaptive development coverage; "
            "not fixed-policy Pass@10."
        ),
    }
    assert manifest["before_after"] == {
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
            "Same task and seed; videos use normalized episode progress. "
            "The aggregate coverage curve is a separate cross-release measure."
        ),
    }
    assert manifest["matched_code"] == {
        "episode_success_delta_pp": 7.5,
        "median_token_reduction_pct": 29.4,
        "median_vlm_call_reduction_pct": 27.2,
        "median_wall_reduction_pct": 17.0,
        "caption": (
            "Matched Code-on/off results. "
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
    assert len(audio_streams) == 1
    stream = video_streams[0]
    assert stream["codec_name"] == "h264"
    assert stream["pix_fmt"] == "yuv420p"
    assert (stream["width"], stream["height"]) == (480, 270)
    assert 5.7 <= float(metadata["format"]["duration"]) <= 6.2

    decode = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(output), "-f", "null", "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert decode.returncode == 0, decode.stderr

    capture = cv2.VideoCapture(str(output))
    samples = []
    for timestamp_s in (0.4, 1.5, 3.0, 4.8, 5.7):
        capture.set(cv2.CAP_PROP_POS_MSEC, timestamp_s * 1000)
        ok, frame = capture.read()
        assert ok, timestamp_s
        assert float(frame.std()) > 12.0, timestamp_s
        samples.append(frame.astype(np.float32))
    capture.release()
    for left, right in zip(samples, samples[1:]):
        assert float(np.mean(np.abs(left - right))) > 8.0

    grid_pages = []
    for timestamp_s in (0.8, 1.6):
        capture = cv2.VideoCapture(str(output))
        capture.set(cv2.CAP_PROP_POS_MSEC, timestamp_s * 1000)
        ok, frame = capture.read()
        capture.release()
        assert ok, timestamp_s
        height, width = frame.shape[:2]
        grid = frame[
            round(0.07 * height) : round(0.93 * height),
            round(0.25 * width) : round(0.75 * width),
        ]
        grid_pages.append(grid.astype(np.float32))
    assert float(np.mean(np.abs(grid_pages[0] - grid_pages[1]))) > 12.0

    capture = cv2.VideoCapture(str(output))
    capture.set(cv2.CAP_PROP_POS_MSEC, 3.0 * 1000)
    ok, frame = capture.read()
    capture.release()
    assert ok
    height, width = frame.shape[:2]
    crop_width = round(0.25 * width)
    before_left = round(0.04 * width)
    after_left = round(0.32 * width)
    before = frame[
        round(0.25 * height) : round(0.74 * height),
        before_left : before_left + crop_width,
    ].astype(np.float32)
    after = frame[
        round(0.25 * height) : round(0.74 * height),
        after_left : after_left + crop_width,
    ].astype(np.float32)
    assert float(before.std()) > 20.0
    assert float(after.std()) > 20.0
    assert float(np.mean(np.abs(before - after))) > 8.0

    poster_frame = cv2.imread(str(poster))
    assert poster_frame is not None
    assert poster_frame.shape[:2] == (270, 480)
    assert float(poster_frame.std()) > 12.0


def test_remotion_project_and_voiceover_contract_are_source_controlled() -> None:
    package = json.loads((REMOTION / "package.json").read_text(encoding="utf-8"))
    assert package["scripts"]["render"] == "remotion render src/index.ts RoborsiDemo"
    assert package["dependencies"]["remotion"] == "4.0.517"
    assert package["dependencies"]["@remotion/cli"] == "4.0.517"
    assert package["dependencies"]["@remotion/media"] == "4.0.517"
    assert package["dependencies"]["react"] == "19.2.8"

    source = (REMOTION / "src/RoborsiDemo.tsx").read_text(encoding="utf-8")
    assert "OffthreadVideo" in source
    assert "<Audio" in source
    assert "NarrationCaption" in source
    assert "Cross-release coverage" in source
    assert "Code-on" in source

    voiceover = json.loads((REMOTION / "voiceover.json").read_text(encoding="utf-8"))
    assert voiceover["preferred_provider"] == "elevenlabs"
    assert voiceover["generated_provider"] in {"elevenlabs", "edge"}
    assert voiceover["model_id"] == "eleven_v3"
    assert voiceover["voice_id"] == "JBFqnCBsd6RMkjVDRZzb"
    for language in ("en", "zh"):
        segments = voiceover["languages"][language]
        assert [row["id"] for row in segments] == [
            "intro",
            "verified_tasks",
            "adaptive_evolution",
            "matched_code",
            "end_slate",
        ]
        assert all(row["text"].strip() for row in segments)
        assert all((STATIC / row["audio"]).stat().st_size > 10_000 for row in segments)
        assert all((STATIC / row["captions"]).stat().st_size > 20 for row in segments)


def test_chinese_demo_manifest_and_smoke_render(tmp_path: Path) -> None:
    cv2 = pytest.importorskip("cv2")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg and FFprobe are required for the Chinese demo")

    manifest_result = _run("--language", "zh", "--print-manifest")
    assert manifest_result.returncode == 0, manifest_result.stderr
    manifest = json.loads(manifest_result.stdout)
    assert manifest["language"] == "zh"
    assert manifest["fonts"]["cjk"] == (
        "src/robohermes_libero/static/fonts/wqy-microhei.ttc"
    )
    assert manifest["matched_code"]["caption"] == (
        "Code-on/off 为配对实验；视频仅展示代码技能的执行过程。"
    )

    output = tmp_path / "demo-zh.mp4"
    poster = tmp_path / "demo-zh-poster.jpg"
    result = _run(
        "--language",
        "zh",
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

    capture = cv2.VideoCapture(str(output))
    capture.set(cv2.CAP_PROP_POS_MSEC, 1.8 * 1000)
    ok, frame = capture.read()
    capture.release()
    assert ok
    assert float(frame.std()) > 20.0
