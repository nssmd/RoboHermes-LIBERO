#!/usr/bin/env python3
"""Generate the bilingual roborsi narration tracks.

ElevenLabs is the preferred provider. When no key is present, the explicit
``--provider edge`` fallback can generate Microsoft neural narration. Rendered
MP3 files are committed, so normal Remotion rendering does not call either API.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "remotion/voiceover.json"
STATIC = ROOT / "src/robohermes_libero/static"


def _timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def _write_vtt(language: str, segments: list[dict]) -> None:
    path = STATIC / segments[0]["captions"]
    lines = ["WEBVTT", ""]
    for index, segment in enumerate(segments, start=1):
        start = float(segment["start_s"])
        end = start + float(segment["duration_s"])
        lines.extend(
            [
                str(index),
                f"{_timestamp(start)} --> {_timestamp(end)}",
                segment["text"],
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {language} captions: {path.relative_to(ROOT)}")


def _normalize_mp3(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-v",
            "error",
            "-i",
            str(source),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-b:a",
            "128k",
            str(destination),
        ],
        check=True,
    )


def _elevenlabs_segment(
    *,
    text: str,
    voice_id: str,
    model_id: str,
    output_format: str,
    voice_settings: dict,
    destination: Path,
) -> None:
    api_key = os.getenv("ELEVENLABS_API_KEY") or os.getenv("XI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ELEVENLABS_API_KEY is required for --provider elevenlabs"
        )
    query = urllib.parse.urlencode({"output_format": output_format})
    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        f"{urllib.parse.quote(voice_id)}?{query}"
    )
    body = json.dumps(
        {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            audio = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read(500).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc
    if len(audio) < 10_000:
        raise RuntimeError(f"ElevenLabs returned only {len(audio)} bytes")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temporary:
        temporary.write(audio)
        temporary_path = Path(temporary.name)
    try:
        _normalize_mp3(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


async def _edge_segment(
    *,
    text: str,
    voice: str,
    destination: Path,
) -> None:
    try:
        import edge_tts
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "edge-tts is required for --provider edge; install edge-tts==7.2.8"
        ) from exc
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        communicate = edge_tts.Communicate(text, voice, rate="-4%")
        await communicate.save(str(temporary_path))
        _normalize_mp3(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def _probe_audio(path: Path, maximum_duration: float) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    duration = float(result.stdout.strip())
    if duration > maximum_duration:
        raise RuntimeError(
            f"{path.name} is {duration:.2f}s, longer than its "
            f"{maximum_duration:.2f}s scene"
        )
    return duration


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provider",
        choices=("elevenlabs", "edge"),
        default="elevenlabs",
    )
    parser.add_argument(
        "--language",
        choices=("en", "zh", "all"),
        default="all",
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    languages = ("en", "zh") if args.language == "all" else (args.language,)
    if args.provider == "edge" and shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg is required")

    for language in languages:
        segments = config["languages"][language]
        _write_vtt(language, segments)
        for segment in segments:
            destination = STATIC / segment["audio"]
            if destination.is_file() and destination.stat().st_size > 10_000:
                if not args.force:
                    print(f"keep existing: {destination.relative_to(ROOT)}")
                    continue
            print(f"generate {language}/{segment['id']} via {args.provider}")
            if args.provider == "elevenlabs":
                _elevenlabs_segment(
                    text=segment["text"],
                    voice_id=config["voice_id"],
                    model_id=config["model_id"],
                    output_format=config["output_format"],
                    voice_settings=config["voice_settings"],
                    destination=destination,
                )
            else:
                asyncio.run(
                    _edge_segment(
                        text=segment["text"],
                        voice=config["fallback_voices"][language],
                        destination=destination,
                    )
                )
            duration = _probe_audio(
                destination,
                float(segment["duration_s"]) - 0.35,
            )
            print(
                f"wrote {destination.relative_to(ROOT)} "
                f"({duration:.2f}s)"
            )

    config["generated_provider"] = args.provider
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
