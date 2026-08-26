import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Loop,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type {
  DemoProps,
  DemoSource,
  VoiceSegment,
} from "./types";

const COLORS = {
  ink: "#171917",
  soft: "#4d514d",
  muted: "#777d77",
  paper: "#ffffff",
  well: "#f3f5f3",
  rule: "#d6dbd6",
  green: "#147d61",
  rust: "#b05031",
  blue: "#356995",
  dark: "#111311",
};

const FONT_SERIF =
  '"Source Serif 4", "Noto Serif", Georgia, "Times New Roman", serif';
const FONT_SANS =
  '"WenQuanYi Micro Hei", "Microsoft YaHei", Inter, Arial, sans-serif';
const FONT_MONO =
  '"JetBrains Mono", "WenQuanYi Micro Hei", ui-monospace, monospace';

const FontStyles: React.FC = () => {
  return (
    <style>
      {`
        @font-face {
          font-family: "Source Serif 4";
          src: url("${staticFile("fonts/source-serif-4-latin.woff2")}") format("woff2");
          font-weight: 400 700;
        }
        @font-face {
          font-family: "JetBrains Mono";
          src: url("${staticFile("fonts/jetbrains-mono-latin.woff2")}") format("woff2");
          font-weight: 400 700;
        }
        @font-face {
          font-family: "WenQuanYi Micro Hei";
          src: url("${staticFile("fonts/wqy-microhei.ttc")}") format("truetype");
          font-weight: 400;
        }
      `}
    </style>
  );
};

const fit = (value: number, scale: number) => Math.round(value * scale);

const sourceUrl = (path: string) => {
  return staticFile(path.replace(/^src\/robohermes_libero\/static\//, ""));
};

const useScaledFrame = (durationScale: number) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return {
    frame,
    seconds: frame / fps / durationScale,
  };
};

const FadeIn: React.FC<{
  children: React.ReactNode;
  start?: number;
  duration?: number;
  y?: number;
}> = ({children, start = 0, duration = 14, y = 16}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const translateY = interpolate(frame, [start, start + duration], [y, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div style={{opacity, transform: `translateY(${translateY}px)`}}>
      {children}
    </div>
  );
};

const EditorialLabel: React.FC<{
  children: React.ReactNode;
  dark?: boolean;
}> = ({children, dark = false}) => {
  return (
    <div
      style={{
        color: dark ? "#c8d0c8" : COLORS.green,
        fontFamily: FONT_MONO,
        fontSize: 21,
        lineHeight: 1,
        textTransform: "uppercase",
        letterSpacing: 0,
      }}
    >
      {children}
    </div>
  );
};

const NarrationCaption: React.FC<{
  segment: VoiceSegment;
  language: "en" | "zh";
  dark?: boolean;
}> = ({segment, language, dark = false}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 10, 9999], [0, 1, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: 150,
        right: 150,
        bottom: 44,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
        opacity,
      }}
    >
      <div
        style={{
          maxWidth: 1320,
          padding: "15px 24px 16px",
          color: dark ? "#f6f8f6" : COLORS.ink,
          background: dark
            ? "rgba(12, 14, 12, 0.86)"
            : "rgba(255, 255, 255, 0.92)",
          border: `1px solid ${
            dark ? "rgba(255,255,255,0.2)" : COLORS.rule
          }`,
          fontFamily: language === "zh" ? FONT_SANS : FONT_SERIF,
          fontSize: language === "zh" ? 30 : 29,
          lineHeight: language === "zh" ? 1.5 : 1.35,
          textAlign: "center",
          boxShadow: "0 8px 32px rgba(0,0,0,0.08)",
        }}
      >
        {segment.text}
      </div>
    </div>
  );
};

const MediaFrame: React.FC<{
  source: DemoSource;
  label?: string;
  verdict?: "success" | "failure";
  scale: number;
  language: "en" | "zh";
}> = ({source, label, verdict = "success", scale, language}) => {
  const {fps} = useVideoConfig();
  const loopDuration = Math.max(
    1,
    Math.floor((source.duration_s - source.offset_s) * fps),
  );
  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        background: "#0b0c0b",
        border: `1px solid ${COLORS.rule}`,
      }}
    >
      <Loop durationInFrames={loopDuration}>
        <OffthreadVideo
          src={sourceUrl(source.path)}
          muted
          trimBefore={Math.round(source.offset_s * fps)}
          style={{width: "100%", height: "100%", objectFit: "cover"}}
        />
      </Loop>
      <div
        style={{
          position: "absolute",
          inset: "auto 0 0",
          padding: `${fit(12, scale)}px ${fit(16, scale)}px`,
          color: "#ffffff",
          background: "rgba(8, 10, 8, 0.78)",
          fontFamily: FONT_MONO,
          fontSize: fit(14, scale),
          lineHeight: 1.35,
        }}
      >
        <div style={{color: verdict === "success" ? "#67d4ab" : "#ff9876"}}>
          {language === "zh"
            ? verdict === "success"
              ? "仿真判定：成功"
              : "仿真判定：失败"
            : verdict === "success"
              ? "SIMULATOR SUCCESS"
              : "SIMULATOR FAILURE"}
        </div>
        <div style={{marginTop: fit(4, scale)}}>
          {label ?? source.label}
        </div>
      </div>
    </div>
  );
};

const IntroScene: React.FC<{
  props: DemoProps;
  segment: VoiceSegment;
}> = ({props, segment}) => {
  const {seconds} = useScaledFrame(props.durationScale);
  const hero =
    props.manifest.sources.find(
      (source) => source.id === "strict-moka-pot-stove",
    ) ?? props.manifest.sources[0];
  const reveal = interpolate(seconds, [0, 1.1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill style={{background: COLORS.dark, color: "#ffffff"}}>
      {hero ? (
        <OffthreadVideo
          src={sourceUrl(hero.path)}
          muted
          trimBefore={Math.round(hero.offset_s * props.fps)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: 0.82,
            transform: `scale(${1.03 + seconds * 0.002})`,
          }}
        />
      ) : null}
      <AbsoluteFill
        style={{
          background: "rgba(8, 10, 8, 0.64)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 116,
          top: 102,
          width: 920,
          opacity: reveal,
          transform: `translateY(${(1 - reveal) * 28}px)`,
        }}
      >
        <EditorialLabel dark>
          {props.language === "zh"
            ? "经仿真验证的机器人自进化"
            : "Simulator-verified robot self-improvement"}
        </EditorialLabel>
        <div
          style={{
            marginTop: 34,
            fontFamily: FONT_SERIF,
            fontSize: 108,
            lineHeight: 0.96,
            letterSpacing: 0,
          }}
        >
          roborsi
        </div>
        <div
          style={{
            marginTop: 26,
            maxWidth: 840,
            color: "#dbe0db",
            fontFamily: props.language === "zh" ? FONT_SANS : FONT_SERIF,
            fontSize: props.language === "zh" ? 43 : 42,
            lineHeight: 1.25,
          }}
        >
          {props.language === "zh"
            ? "将验证经验转化为可检查、可复用的代码技能"
            : "Verified experience, retained as inspectable code"}
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          right: 82,
          top: 74,
          color: "#ffffff",
          fontFamily: FONT_MONO,
          fontSize: 17,
          opacity: 0.74,
        }}
      >
        REMOTION FILM / NARRATED
      </div>
      <NarrationCaption
        segment={segment}
        language={props.language}
        dark
      />
    </AbsoluteFill>
  );
};

const VerifiedTasksScene: React.FC<{
  props: DemoProps;
  segment: VoiceSegment;
}> = ({props, segment}) => {
  const {seconds} = useScaledFrame(props.durationScale);
  const sceneDuration = 15;
  const page = seconds < sceneDuration / 2 ? 0 : 1;
  const ids = props.manifest.task_grid.pages[page] ?? [];
  const sources = ids
    .map((id) => props.manifest.sources.find((source) => source.id === id))
    .filter((source): source is DemoSource => Boolean(source));
  const pageProgress =
    page === 0 ? seconds / (sceneDuration / 2) : (seconds - 7.5) / 7.5;
  return (
    <AbsoluteFill style={{background: COLORS.paper, color: COLORS.ink}}>
      <div
        style={{
          position: "absolute",
          inset: "70px 72px 112px",
          display: "grid",
          gridTemplateColumns: "360px 1fr",
          gap: 48,
        }}
      >
        <div style={{paddingTop: 10}}>
          <FadeIn>
            <EditorialLabel>
              {props.language === "zh"
                ? "01 / 经验证的任务执行"
                : "01 / Verified rollouts"}
            </EditorialLabel>
            <div
              style={{
                marginTop: 28,
                fontFamily: FONT_SERIF,
                fontSize: 62,
                lineHeight: 1.04,
              }}
            >
              {props.language === "zh"
                ? "真实任务执行，不是素材拼贴"
                : "Real robot execution, not illustrative footage"}
            </div>
            <div
              style={{
                marginTop: 30,
                color: COLORS.soft,
                fontFamily: props.language === "zh" ? FONT_SANS : FONT_SERIF,
                fontSize: 27,
                lineHeight: 1.48,
              }}
            >
              {props.language === "zh"
                ? "13 段成功录像覆盖 LIBERO、LIBERO-Plus 与历史 RoboTwin。每段视频都对应明确任务、随机种子和最终判定。"
                : "Thirteen successful recordings span LIBERO, LIBERO-Plus, and historical RoboTwin. Every clip retains its named task, seed, and final outcome."}
            </div>
          </FadeIn>
          <div
            style={{
              position: "absolute",
              left: 0,
              bottom: 8,
              fontFamily: FONT_MONO,
              fontSize: 18,
              color: COLORS.muted,
            }}
          >
            {props.language === "zh" ? "第" : "PAGE"} {page + 1} / 2
            <div
              style={{
                marginTop: 12,
                width: 260,
                height: 3,
                background: COLORS.rule,
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${Math.min(100, pageProgress * 100)}%`,
                  background: COLORS.green,
                }}
              />
            </div>
          </div>
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
            gridTemplateRows: "repeat(3, minmax(0, 1fr))",
            gap: 10,
          }}
        >
          {sources.map((source) => (
            <MediaFrame
              key={`${page}-${source.id}`}
              source={source}
              label={
                props.language === "zh" ? source.label_zh : source.label
              }
              scale={0.72}
              language={props.language}
            />
          ))}
        </div>
      </div>
      <NarrationCaption segment={segment} language={props.language} />
    </AbsoluteFill>
  );
};

const Curve: React.FC<{
  values: number[];
  progress: number;
  total: number;
}> = ({values, progress, total}) => {
  const width = 560;
  const height = 300;
  const left = 42;
  const right = 22;
  const top = 30;
  const bottom = 38;
  const x = (index: number) =>
    left + index * ((width - left - right) / Math.max(1, values.length - 1));
  const y = (value: number) =>
    top + (total - value) * ((height - top - bottom) / total);
  const visible = Math.max(
    1,
    Math.min(values.length, Math.ceil(progress * values.length)),
  );
  const points = values
    .slice(0, visible)
    .map((value, index) => `${x(index)},${y(value)}`)
    .join(" ");
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {[0, 30, 60, 90, 120].map((tick) => (
        <g key={tick}>
          <line
            x1={left}
            y1={y(tick)}
            x2={width - right}
            y2={y(tick)}
            stroke={COLORS.rule}
            strokeWidth={1}
          />
          <text
            x={left - 10}
            y={y(tick) + 5}
            textAnchor="end"
            fill={COLORS.muted}
            fontFamily={FONT_MONO}
            fontSize={14}
          >
            {tick}
          </text>
        </g>
      ))}
      <polyline
        points={points}
        fill="none"
        stroke={COLORS.green}
        strokeWidth={4}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      {values.slice(0, visible).map((value, index) => (
        <circle
          key={`${index}-${value}`}
          cx={x(index)}
          cy={y(value)}
          r={6}
          fill={COLORS.paper}
          stroke={COLORS.green}
          strokeWidth={3}
        />
      ))}
      <text
        x={width - right}
        y={y(values[Math.max(0, visible - 1)]) - 16}
        textAnchor="end"
        fill={COLORS.green}
        fontFamily={FONT_MONO}
        fontSize={22}
      >
        {values[Math.max(0, visible - 1)]}/{total}
      </text>
    </svg>
  );
};

const AdaptiveScene: React.FC<{
  props: DemoProps;
  segment: VoiceSegment;
}> = ({props, segment}) => {
  const {seconds} = useScaledFrame(props.durationScale);
  const progress = interpolate(seconds, [1.5, 14], [0.08, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  const before = props.manifest.sources.find(
    (source) => source.id === props.manifest.before_after.before.id,
  );
  const after = props.manifest.sources.find(
    (source) => source.id === props.manifest.before_after.after.id,
  );
  return (
    <AbsoluteFill style={{background: COLORS.well, color: COLORS.ink}}>
      <div
        style={{
          position: "absolute",
          inset: "58px 68px 112px",
        }}
      >
        <EditorialLabel>
          {props.language === "zh"
            ? "02 / 纠错驱动的自进化"
            : "02 / Corrective self-improvement"}
        </EditorialLabel>
        <div
          style={{
            marginTop: 22,
            display: "grid",
            gridTemplateColumns: "1fr 1fr 0.9fr",
            gap: 22,
            height: 765,
          }}
        >
          {before ? (
            <div style={{display: "grid", gridTemplateRows: "1fr 130px"}}>
              <MediaFrame
                source={before}
                verdict="failure"
                scale={0.86}
                language={props.language}
              />
              <div
                style={{
                  padding: "18px 18px 0",
                  borderLeft: `4px solid ${COLORS.rust}`,
                  background: COLORS.paper,
                }}
              >
                <div
                  style={{
                    color: COLORS.rust,
                    fontFamily: FONT_MONO,
                    fontSize: 18,
                  }}
                >
                  {props.language === "zh"
                    ? "修复前 / 最终失败"
                    : "BEFORE / FINAL FALSE"}
                </div>
                <div
                  style={{
                    marginTop: 12,
                    fontFamily: FONT_SERIF,
                    fontSize: 30,
                  }}
                >
                  {props.language === "zh"
                    ? "120 步 ACT / 放置失败"
                    : "120 ACT steps / placement failed"}
                </div>
              </div>
            </div>
          ) : null}
          {after ? (
            <div style={{display: "grid", gridTemplateRows: "1fr 130px"}}>
              <MediaFrame
                source={after}
                verdict="success"
                scale={0.86}
                language={props.language}
              />
              <div
                style={{
                  padding: "18px 18px 0",
                  borderLeft: `4px solid ${COLORS.green}`,
                  background: COLORS.paper,
                }}
              >
                <div
                  style={{
                    color: COLORS.green,
                    fontFamily: FONT_MONO,
                    fontSize: 18,
                  }}
                >
                  {props.language === "zh"
                    ? "修复后 / 最终成功"
                    : "AFTER / FINAL TRUE"}
                </div>
                <div
                  style={{
                    marginTop: 12,
                    fontFamily: FONT_SERIF,
                    fontSize: 30,
                  }}
                >
                  {props.language === "zh"
                    ? "304 步 ACT / 视觉校验放置"
                    : "304 ACT steps / verified placement"}
                </div>
              </div>
            </div>
          ) : null}
          <div
            style={{
              background: COLORS.paper,
              border: `1px solid ${COLORS.rule}`,
              padding: "28px 26px",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <EditorialLabel>
              {props.language === "zh"
                ? "跨版本任务覆盖率"
                : "Cross-release coverage"}
            </EditorialLabel>
            <div
              style={{
                marginTop: 20,
                fontFamily: FONT_SERIF,
                fontSize: 40,
                lineHeight: 1.12,
              }}
            >
              {props.language === "zh"
                ? "解法覆盖随版本推进"
                : "Solution coverage grows across releases"}
            </div>
            <div style={{marginTop: 40}}>
              <Curve
                values={props.manifest.adaptive.coverage}
                progress={progress}
                total={props.manifest.adaptive.total_tasks}
              />
            </div>
            <div
              style={{
                marginTop: "auto",
                paddingTop: 24,
                borderTop: `1px solid ${COLORS.rule}`,
                color: COLORS.soft,
                fontFamily: FONT_MONO,
                fontSize: 18,
                lineHeight: 1.5,
              }}
            >
              {props.language === "zh"
                ? "同任务同随机种子案例，与跨版本汇总曲线分别报告。"
                : "The matched case and aggregate cross-release curve remain separate evidence."}
            </div>
          </div>
        </div>
      </div>
      <NarrationCaption segment={segment} language={props.language} />
    </AbsoluteFill>
  );
};

const MetricRow: React.FC<{
  label: string;
  value: string;
  delta: string;
  progress: number;
  index: number;
}> = ({label, value, delta, progress, index}) => {
  const reveal = interpolate(progress, [index * 0.12, index * 0.12 + 0.42], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "260px 1fr 130px",
        gap: 24,
        alignItems: "center",
        padding: "19px 0",
        borderTop: "1px solid rgba(255,255,255,0.17)",
        opacity: reveal,
        transform: `translateX(${(1 - reveal) * 22}px)`,
      }}
    >
      <div style={{fontFamily: FONT_MONO, fontSize: 18, color: "#bac2ba"}}>
        {label}
      </div>
      <div>
        <div
          style={{
            height: 9,
            background: "rgba(255,255,255,0.14)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${reveal * 100}%`,
              height: "100%",
              background: COLORS.green,
            }}
          />
        </div>
        <div
          style={{
            marginTop: 10,
            color: "#ffffff",
            fontFamily: FONT_SERIF,
            fontSize: 30,
          }}
        >
          {value}
        </div>
      </div>
      <div
        style={{
          color: COLORS.green,
          fontFamily: FONT_MONO,
          fontSize: 24,
          textAlign: "right",
        }}
      >
        {delta}
      </div>
    </div>
  );
};

const MatchedCodeScene: React.FC<{
  props: DemoProps;
  segment: VoiceSegment;
}> = ({props, segment}) => {
  const {seconds} = useScaledFrame(props.durationScale);
  const progress = Math.min(1, Math.max(0, seconds / 13));
  const example = props.manifest.sources.find(
    (source) => source.id === "adaptive-black-bowl-plate",
  );
  const metrics = [
    {
      label: props.language === "zh" ? "单回合成功率" : "EPISODE SUCCESS",
      value: "29.0% vs 21.5%",
      delta: "+7.5 pp",
    },
    {
      label: props.language === "zh" ? "Token 中位数" : "MEDIAN TOKENS",
      value: "2.58M vs 3.65M",
      delta: "-29.4%",
    },
    {
      label:
        props.language === "zh" ? "VLM 调用中位数" : "MEDIAN VLM CALLS",
      value: "29.5 vs 40.5",
      delta: "-27.2%",
    },
    {
      label: props.language === "zh" ? "实际耗时中位数" : "MEDIAN WALL TIME",
      value: "701s vs 845s",
      delta: "-17.0%",
    },
  ];
  return (
    <AbsoluteFill style={{background: COLORS.dark, color: "#ffffff"}}>
      <div
        style={{
          position: "absolute",
          inset: "70px 76px 112px",
          display: "grid",
          gridTemplateColumns: "0.82fr 1.18fr",
          gap: 54,
        }}
      >
        <div>
          <EditorialLabel dark>
            {props.language === "zh"
              ? "03 / CODE-ON/OFF 配对评测"
              : "03 / Matched Code-on/off"}
          </EditorialLabel>
          <div
            style={{
              marginTop: 24,
              fontFamily: FONT_SERIF,
              fontSize: 58,
              lineHeight: 1.03,
            }}
          >
            {props.language === "zh"
              ? "保留验证技能，提高成功率并降低成本"
              : "Retaining verified skills improves success and cost"}
          </div>
          <div
            style={{
              marginTop: 30,
              color: "#b9c0b9",
              fontFamily: props.language === "zh" ? FONT_SANS : FONT_SERIF,
              fontSize: 26,
              lineHeight: 1.5,
            }}
          >
            {props.language === "zh"
              ? "Code-on 仅增加已经验证的 visual_pick_place 复合技能。模型、任务、随机种子、基础工具和预算保持一致。"
              : "Code-on adds only the verified visual_pick_place compound. Model, tasks, seeds, base tools, and budget remain matched."}
          </div>
          {example ? (
            <div style={{height: 400, marginTop: 34}}>
              <MediaFrame
                source={example}
                scale={0.82}
                language={props.language}
              />
            </div>
          ) : null}
        </div>
        <div
          style={{
            paddingTop: 82,
            display: "flex",
            flexDirection: "column",
          }}
        >
          {metrics.map((metric, index) => (
            <MetricRow
              key={metric.label}
              {...metric}
              progress={progress}
              index={index}
            />
          ))}
          <div
            style={{
              marginTop: 24,
              paddingTop: 22,
              borderTop: "1px solid rgba(255,255,255,0.17)",
              color: "#aab2aa",
              fontFamily: FONT_MONO,
              fontSize: 18,
              lineHeight: 1.5,
            }}
          >
            {props.language === "zh"
              ? "成功率来自 1,200 个配对回合；效率来自独立的 118 任务配对面板。"
              : "Success uses 1,200 paired episodes. Efficiency uses a separate matched panel of 118 tasks."}
          </div>
        </div>
      </div>
      <NarrationCaption
        segment={segment}
        language={props.language}
        dark
      />
    </AbsoluteFill>
  );
};

const EndScene: React.FC<{
  props: DemoProps;
  segment: VoiceSegment;
}> = ({props, segment}) => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 28], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill
      style={{
        background: COLORS.paper,
        color: COLORS.ink,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          bottom: 0,
          width: 18,
          background: COLORS.green,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 86,
          right: 86,
          top: 66,
          display: "flex",
          justifyContent: "space-between",
          color: COLORS.muted,
          fontFamily: FONT_MONO,
          fontSize: 18,
        }}
      >
        <span>
          {props.language === "zh"
            ? "经仿真验证的机器人自进化"
            : "SIMULATOR-VERIFIED SELF-IMPROVEMENT"}
        </span>
        <span>ROBO-RSI.COM</span>
      </div>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 214,
          opacity: reveal,
          transform: `translateY(${(1 - reveal) * 24}px)`,
          textAlign: "center",
        }}
      >
        <EditorialLabel>
          {props.language === "zh"
            ? "经仿真验证的自进化"
            : "Simulator-verified self-improvement"}
        </EditorialLabel>
        <div
          style={{
            marginTop: 36,
            fontFamily: FONT_SERIF,
            fontSize: 132,
            lineHeight: 0.9,
          }}
        >
          roborsi
        </div>
        <div
          style={{
            marginTop: 34,
            color: COLORS.soft,
            fontFamily: props.language === "zh" ? FONT_SANS : FONT_SERIF,
            fontSize: 36,
          }}
        >
          {props.language === "zh"
            ? "验证经验，转化为可复用代码"
            : "Verified experience, retained as reusable code"}
        </div>
        <div
          style={{
            marginTop: 46,
            color: COLORS.green,
            fontFamily: FONT_MONO,
            fontSize: 27,
          }}
        >
          robo-rsi.com
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 86,
          right: 86,
          bottom: 152,
          height: 150,
          display: "grid",
          gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
          gap: 8,
          overflow: "hidden",
          borderTop: `1px solid ${COLORS.rule}`,
          borderBottom: `1px solid ${COLORS.rule}`,
        }}
      >
        {[
          "strict-moka-pot-stove",
          "adaptive-black-bowl-plate",
          "strict-bowl-tray",
        ].map((id) => {
          const source = props.manifest.sources.find((row) => row.id === id);
          if (!source) {
            return <div key={id} style={{background: COLORS.well}} />;
          }
          return (
            <OffthreadVideo
              key={id}
              src={sourceUrl(source.path)}
              muted
              trimBefore={Math.round(source.offset_s * props.fps)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "saturate(0.86) contrast(1.04)",
              }}
            />
          );
        })}
      </div>
      <NarrationCaption segment={segment} language={props.language} />
    </AbsoluteFill>
  );
};

export const RoborsiDemo: React.FC<DemoProps> = (props) => {
  const {fps} = useVideoConfig();
  const sceneStarts = props.manifest.scenes.reduce<number[]>((starts, scene) => {
    const previous = starts.at(-1) ?? 0;
    const previousScene = props.manifest.scenes[starts.length - 1];
    starts.push(
      previous +
        (previousScene
          ? previousScene.duration_s * fps * props.durationScale
          : 0),
    );
    return starts;
  }, []);
  const narrationById = new Map(
    props.narration.map((segment) => [segment.id, segment]),
  );
  const frameForSeconds = (seconds: number) =>
    Math.round(seconds * fps * props.durationScale);
  const durationForScene = (index: number) =>
    frameForSeconds(props.manifest.scenes[index].duration_s);

  return (
    <AbsoluteFill>
      <FontStyles />
      {props.narration.map((segment) => (
        <Sequence
          key={`audio-${segment.id}`}
          from={frameForSeconds(segment.start_s)}
          durationInFrames={frameForSeconds(segment.duration_s)}
          name={`Narration: ${segment.id}`}
        >
          <Audio src={staticFile(segment.audio)} volume={1} />
        </Sequence>
      ))}

      <Sequence
        from={sceneStarts[0]}
        durationInFrames={durationForScene(0)}
        name="Introduction"
      >
        <IntroScene
          props={props}
          segment={narrationById.get("intro")!}
        />
      </Sequence>
      <Sequence
        from={sceneStarts[1]}
        durationInFrames={durationForScene(1)}
        name="Verified tasks"
      >
        <VerifiedTasksScene
          props={props}
          segment={narrationById.get("verified_tasks")!}
        />
      </Sequence>
      <Sequence
        from={sceneStarts[2]}
        durationInFrames={durationForScene(2)}
        name="Corrective self-improvement"
      >
        <AdaptiveScene
          props={props}
          segment={narrationById.get("adaptive_evolution")!}
        />
      </Sequence>
      <Sequence
        from={sceneStarts[3]}
        durationInFrames={durationForScene(3)}
        name="Matched Code-on/off"
      >
        <MatchedCodeScene
          props={props}
          segment={narrationById.get("matched_code")!}
        />
      </Sequence>
      <Sequence
        from={sceneStarts[4]}
        durationInFrames={durationForScene(4)}
        name="End slate"
      >
        <EndScene
          props={props}
          segment={narrationById.get("end_slate")!}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
