# roborsi Remotion Film

The public evidence film is a 60-second bilingual Remotion composition. The
English and Chinese renders use the same source rollouts, scene timing, metrics,
and evidence boundaries. Each language has its own narration and captions.

## Install

```bash
cd remotion
npm ci
```

## Render

Use the repository wrapper so evidence values and narration assets are passed
to Remotion consistently:

```bash
python scripts/build_demo_video.py --language en
python scripts/build_demo_video.py --language zh
```

The wrapper renders with Remotion, then normalizes the release file to H.264,
`yuv420p`, BT.709, AAC stereo, and fast-start MP4.

## Narration

Committed MP3 files make normal rendering offline and reproducible.
ElevenLabs `eleven_v3` is the preferred synthesis provider:

```bash
export ELEVENLABS_API_KEY=...
python scripts/generate_voiceover.py \
  --provider elevenlabs \
  --language all \
  --force
```

The voice, model, scripts, timing, and output format are pinned in
`voiceover.json`. The repository never stores the API key.

When no ElevenLabs key is available, a Microsoft Neural fallback can generate
audition-ready tracks:

```bash
python -m pip install edge-tts==7.2.8
python scripts/generate_voiceover.py \
  --provider edge \
  --language all \
  --force
```

`generated_provider` in `voiceover.json` records which provider produced the
committed MP3 files. `preferred_provider` remains `elevenlabs`.

## Studio

The Studio is useful for layout and timing changes:

```bash
cd remotion
npm run studio
```

Production values should still be rendered through
`scripts/build_demo_video.py`.
