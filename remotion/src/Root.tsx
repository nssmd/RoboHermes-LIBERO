import React from "react";
import {
  CalculateMetadataFunction,
  Composition,
} from "remotion";
import {RoborsiDemo} from "./RoborsiDemo";
import type {DemoProps} from "./types";

const placeholderManifest: DemoProps["manifest"] = {
  schema: "roborsi.evidence_demo.v2",
  language: "en",
  duration_s: 60,
  master: {width: 1920, height: 1080, fps: 30, audio: true},
  scenes: [
    {id: "intro", duration_s: 7},
    {id: "verified_tasks", duration_s: 15},
    {id: "adaptive_evolution", duration_s: 16},
    {id: "matched_code", duration_s: 16},
    {id: "end_slate", duration_s: 6},
  ],
  sources: [],
  task_grid: {layout: "3x3", pages: [[], []], unique_success_sources: 0},
  adaptive: {coverage: [32, 83], total_tasks: 120, caption: ""},
  before_after: {
    task: "libero_spatial_swap/0",
    seed: 3,
    time_alignment: "normalized_episode_progress",
    before: {id: "", transport_steps: 120, verdict: ""},
    after: {id: "", transport_steps: 304, verdict: ""},
    caption: "",
  },
  matched_code: {
    episode_success_delta_pp: 7.5,
    median_token_reduction_pct: 29.4,
    median_vlm_call_reduction_pct: 27.2,
    median_wall_reduction_pct: 17,
    caption: "",
  },
  voiceover: {
    preferred_provider: "elevenlabs",
    generated_provider: "edge",
    model_id: "eleven_v3",
    voice_id: "JBFqnCBsd6RMkjVDRZzb",
    output_format: "mp3_44100_128",
    segments: [],
  },
};

const defaultProps: DemoProps = {
  language: "en",
  width: 1920,
  height: 1080,
  fps: 30,
  durationScale: 1,
  manifest: placeholderManifest,
  narration: placeholderManifest.scenes.map((scene, index) => ({
    id: scene.id,
    start_s: placeholderManifest.scenes
      .slice(0, index)
      .reduce((sum, row) => sum + row.duration_s, 0),
    duration_s: scene.duration_s,
    text: scene.id.replaceAll("_", " "),
    audio: `media/demo/voiceover/en/${scene.id.replaceAll("_", "-")}.mp3`,
    captions: "media/demo/roborsi-demo-en.vtt",
  })),
};

const calculateMetadata: CalculateMetadataFunction<DemoProps> = ({
  props,
}) => {
  return {
    durationInFrames: Math.round(
      props.manifest.duration_s * props.fps * props.durationScale,
    ),
    fps: props.fps,
    width: props.width,
    height: props.height,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="RoborsiDemo"
      component={RoborsiDemo}
      durationInFrames={1800}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={defaultProps}
      calculateMetadata={calculateMetadata}
    />
  );
};
