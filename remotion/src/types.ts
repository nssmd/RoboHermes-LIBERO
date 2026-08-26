export type Language = "en" | "zh";

export type DemoSource = {
  id: string;
  label: string;
  label_zh: string;
  platform: string;
  task: string;
  seed: number;
  path: string;
  duration_s: number;
  offset_s: number;
  verdict: string;
};

export type DemoScene = {
  id: string;
  duration_s: number;
};

export type VoiceSegment = {
  id: string;
  start_s: number;
  duration_s: number;
  text: string;
  audio: string;
  captions: string;
};

export type DemoManifest = {
  schema: string;
  language: Language;
  duration_s: number;
  master: {
    width: number;
    height: number;
    fps: number;
    audio: boolean;
  };
  scenes: DemoScene[];
  sources: DemoSource[];
  task_grid: {
    layout: string;
    pages: string[][];
    unique_success_sources: number;
  };
  adaptive: {
    coverage: number[];
    total_tasks: number;
    caption: string;
  };
  before_after: {
    task: string;
    seed: number;
    time_alignment: string;
    before: {
      id: string;
      transport_steps: number;
      verdict: string;
    };
    after: {
      id: string;
      transport_steps: number;
      verdict: string;
    };
    caption: string;
  };
  matched_code: {
    episode_success_delta_pp: number;
    median_token_reduction_pct: number;
    median_vlm_call_reduction_pct: number;
    median_wall_reduction_pct: number;
    caption: string;
  };
  voiceover: {
    preferred_provider: string;
    generated_provider: string;
    model_id: string;
    voice_id: string;
    output_format: string;
    segments: string[];
  };
};

export type DemoProps = {
  language: Language;
  width: number;
  height: number;
  fps: number;
  durationScale: number;
  manifest: DemoManifest;
  narration: VoiceSegment[];
};
