const state = { videos: new Map() };
const language = document.documentElement.lang.startsWith("zh") ? "zh" : "en";
const isZh = language === "zh";
const numberLocale = isZh ? "zh-CN" : "en-US";

const COPY = {
  orderedEvaluation: {en: "ordered evaluation k", zh: "有序评测轮次 k"},
  openEvidence: {en: "Open evidence for", zh: "查看证据："},
  traceUnavailable: {en: "trace unavailable", zh: "调用链不可用"},
  cumulative: {en: "cumulative", zh: "累计成功"},
  tokens: {en: "tokens", zh: "Token"},
  activeWall: {en: "active wall time", zh: "有效执行时间"},
  attempts: {en: "attempts", zh: "尝试次数"},
  codeOn: {en: "Code-on", zh: "Code-on"},
  codeOff: {en: "Code-off", zh: "Code-off"},
  medianEpisodeTokens: {en: "Median episode tokens", zh: "单回合总 Token 中位数"},
  aggregateTokens: {en: "Aggregate tokens", zh: "总 Token"},
  medianVlmCalls: {en: "Median VLM calls", zh: "VLM 调用次数中位数"},
  medianWallTime: {en: "Median wall-clock time", zh: "实际耗时中位数"},
  lowerWithCode: {en: "lower with code", zh: "Code-on 降幅"},
  successFeedback: {en: "Success feedback:", zh: "成功判定反馈："},
  notDirect: {en: "Not direct", zh: "不可直接比较"},
  sequentialAdaptive: {en: "Sequential adaptive coverage", zh: "顺序自适应覆盖率"},
  strictPass: {en: "Strict Standard-130 Pass at k", zh: "Strict Standard-130 Pass@k"},
  dataUnavailable: {en: "Evidence data unavailable", zh: "证据数据暂不可用"},
};
const t = key => COPY[key]?.[language] ?? key;

const STATUS_ZH = {
  "SIMULATOR SUCCESS": "仿真判定：成功",
  "SIMULATOR FAILURE": "仿真判定：失败",
  PASS: "通过",
  RETRY: "重试",
  FAIL: "失败",
};

const VIDEO_ZH = {
  "strict-moka-pot-stove": {title: "将摩卡壶放到炉灶上", subtitle: "Strict Standard-130 Pass@10 成功回合"},
  "strict-bowl-tray": {title: "将黑碗放入托盘", subtitle: "Strict Standard-130 Pass@10 成功回合"},
  "strict-pudding-basket": {title: "将巧克力布丁放入篮筐", subtitle: "Strict Standard-130 Pass@10 成功回合"},
  "strict-ketchup-basket": {title: "将番茄酱放入篮筐", subtitle: "Strict Standard-130 Pass@10 成功回合"},
  "adaptive-black-bowl-plate": {title: "将黑碗放到盘子上", subtitle: "自适应第 4 轮成功回合"},
  "act-corrective-transport": {title: "ACT 纠错搬运", subtitle: "混合执行的仿真器成功回合"},
  "act-before-corrective": {title: "纠错数据引入前", subtitle: "ACT 搬运不足，放置阶段失败"},
  "plus-camera-black-bowl-plate": {title: "相机视角扰动：将黑碗放到盘子上", subtitle: "Adaptive Pass@2 · 相机视角"},
  "plus-light-ketchup-basket": {title: "低照度扰动：番茄酱放入篮筐", subtitle: "Adaptive Pass@2 · 光照条件"},
  "plus-layout-black-bowl-plate": {title: "布局扰动：将黑碗放到盘子上", subtitle: "Adaptive Pass@2 · 物体布局"},
  "plus-init-black-bowl-plate": {title: "初始状态扰动：将黑碗放到盘子上", subtitle: "Adaptive Pass@2 · 机器人初始状态"},
  "robotwin-grab-roller-seed22": {title: "抓取滚筒", subtitle: "经任务谓词确认的历史回合"},
  "robotwin-place-container-plate-seed21": {title: "将容器放到盘子上", subtitle: "经任务谓词确认的历史回合"},
  "robotwin-turn-switch-seed23": {title: "拨动开关", subtitle: "经任务谓词确认的历史回合"},
};

const TEXT_ZH = {
  "Camera Viewpoints": "相机视角",
  "Light Conditions": "光照条件",
  "Objects Layout": "物体布局",
  "Robot Initial States": "机器人初始状态",
  exact_episode: "完整单回合调用链",
  exact_episode_plus_posthoc_verdict: "完整单回合调用链与事后判定",
  hybrid_stage_trace: "混合执行阶段调用链",
  final_verdict_only: "仅保留最终判定",
  "120/120 learned transport steps": "完成 120/120 步学习策略搬运",
  "hold lost during hover approach": "悬停接近过程中失去夹持",
  "final verdict=false": "最终判定=false",
  "304/304 learned transport steps": "完成 304/304 步学习策略搬运",
  "final verdict=true": "最终判定=true",
  "Ordered evaluator stages from the archived r2 episode record; no per-stage video timestamps were logged.": "调用阶段来自归档的 r2 回合记录；原始记录未包含逐阶段视频时间戳。",
  "Ordered evaluator stages from the protected success record; no per-stage video timestamps were logged.": "调用阶段来自归档的成功回合记录；原始记录未包含逐阶段视频时间戳。",
  "The archived video and final predicate are exact. The original per-episode call log is not retained in the current public bundle.": "归档视频与最终任务谓词判定均为原始证据；当前公开包未保留该回合的逐调用日志。",
};

const COMPARISON_ZH = {
  "roboharness-memory": {
    system: "RoboHarness（记忆增强 VLA）",
    evaluation: "在 pi0、pi0.5 与 SmolVLA 上评测 LIBERO-RoboHarness 及部分 LIBERO-PRO 任务",
    reported_result: "LIBERO-PRO Pos 平均 57.2%；Task 平均 55.2%；论文报告长程任务提升 89.1 个百分点",
    policy_dependency: "冻结的 VLA 策略检查点，并使用 Dual-Memory RAG 与 MCP 视觉及提示干预",
    visible_success_checker: "论文未说明其作为智能体可调用工具暴露",
    why_not_direct: "自定义 OOD 套件、VLA 主干和每项任务约 200 个回合，与 roborsi 的 LIBERO 短程任务级 Pass@k 协议不同。",
  },
  "roboharness-orchestration": {
    system: "RoboHarness（异构策略编排）",
    evaluation: "LIBERO、LIBERO-Plus、LIBERO-LoHo、500 次自定义仿真与 135 次真实机器人试验",
    reported_result: "原始 LIBERO 98.7%；LIBERO-Plus 平均 93.2%；LIBERO-LoHo 成功率 95.2%",
    policy_dependency: "pi0.5、经 RL 后训练的 OpenVLA-OFT 与预定义物体 TAMP 规划器",
    visible_success_checker: "论文未说明其作为智能体可调用工具暴露",
    why_not_direct: "该系统组合已训练的专用策略与 TAMP；roborsi 严格评测使用 RGB-D 代码技能，且不加载策略检查点。",
  },
  "openeta-codex": {
    system: "OpenETA for Codex",
    evaluation: "130 个 LIBERO 任务，按顺序使用 seed 0-4，报告任务级 Pass@5",
    reported_result: "GPT-5.6 Sol：Pass@1 为 92/130，Pass@5 为 117/130",
    policy_dependency: "不使用 VLA 或任务专用策略；提供 observe、mark_point 与 move_to 几何/控制工具",
    visible_success_checker: "是：智能体可调用 check_task，终局成功会被锁存",
    why_not_direct: "OpenETA 使用 512x512 多视角/正交反馈、5000 步时域、最长 5400 秒，并允许智能体访问原生检查器；roborsi 禁止暴露检查器和成功锁存。",
  },
  "vla-evaluation-harness": {
    system: "AllenAI vla-evaluation-harness",
    evaluation: "覆盖 18 个机器人基准与多种策略服务器的统一评测基础设施",
    reported_result: "属于评测基础设施而非智能体方法分数；公开报告复现了若干 LIBERO 策略结果",
    policy_dependency: "由评测器选择模型服务器",
    visible_success_checker: "由基准实现负责评测",
    why_not_direct: "该项目是基准执行层，不是自进化具身智能体。",
  },
  enpire: {
    system: "ENPIRE",
    evaluation: "灵巧操作的真实世界自动研究，以及配对的 40 回合 RoboCasa 仿真面板",
    reported_result: "展示的真实任务在上下文重试下最高达到 99% Pass@8",
    policy_dependency: "通过启发式方法、行为克隆和离线/在线 RL 进行编码智能体驱动的策略改进",
    visible_success_checker: "任务专用自动验证是环境核心 API",
    why_not_direct: "ENPIRE 在任务专用真实环境中优化学习策略；roborsi 在 LIBERO 中评测在线技能组合。",
  },
};

const POSITIONING_ZH = {
  gaps: [
    "当前公开版本尚未报告经独立核验的真实机器人任务成功率。",
    "尚无与 RoboHarness 当前策略基线严格匹配的固定版本或 LIBERO-Plus 留出集面板；840 实例结果属于跨版本自适应评测。",
    "尚未实现与 2026 年 7 月 RoboHarness 相当的异构训练策略路由或学习式交接模块。",
    "95/120 是跨版本自适应开发覆盖率，不是可由单一版本一次命令复现的仿真分数。",
    "精简公开包尚未包含全部失败回合或全部 95 段规范成功视频。",
  ],
  advantages: [
    "代码技能与由仿真器门控的在线进化实现均已公开，而非只提供项目页面。",
    "完整的 840 实例 LIBERO-Plus 面板报告固定与自适应结果、全部 7 类扰动、Token、有效执行时间与最终仿真器判定。",
    "严格评测不使用 VLA 或策略检查点，并将任务判定信息隔离在 Planner、Engineer、Reviewer、技能和提示词之外。",
    "五随机种子配对实验隔离了已保留代码复合技能的作用，并报告配对不确定性。",
    "Token、VLM 调用和实际耗时均在配对面板上实测，而非由成功率间接推断。",
    "所有短程任务结论均以原生仿真器最终判定为准，并将基础设施记录与任务结果分离。",
  ],
};

function localizeVideo(video) {
  if (!isZh) return video;
  const localized = VIDEO_ZH[video.id] ?? {};
  return {
    ...video,
    ...localized,
    perturbation: TEXT_ZH[video.perturbation] ?? video.perturbation,
    trace_scope: TEXT_ZH[video.trace_scope] ?? video.trace_scope,
    trace_note: TEXT_ZH[video.trace_note] ?? video.trace_note,
    tool_chain: video.tool_chain.map(step => ({
      ...step,
      detail: TEXT_ZH[step.detail] ?? step.detail,
    })),
  };
}

const fmtInt = value => value == null ? "-" : new Intl.NumberFormat(numberLocale).format(value);
const fmtMillion = value => `${(value / 1_000_000).toFixed(2)}M`;
const fmtBillion = value => `${(value / 1_000_000_000).toFixed(3)}B`;
const fmtHours = value => isZh ? `${(value / 3600).toFixed(2)} 小时` : `${(value / 3600).toFixed(2)}h`;
const fmtPercent = value => `${(100 * value).toFixed(1)}%`;
const fmtSeconds = value => isZh ? `${value.toFixed(1)} 秒` : `${value.toFixed(1)}s`;
const fmtWholeSeconds = value => isZh ? `${Math.round(value)} 秒` : `${Math.round(value)}s`;
const escapeHtml = value => String(value ?? "").replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);
const brandText = value => String(value ?? "").replaceAll("RoboHermes", "roborsi");
const escapeBrand = value => escapeHtml(brandText(value));

function renderLineChart(elementId, values, total, label, strict = false) {
  const element = document.getElementById(elementId);
  const width = 720, height = 278, left = 50, right = 23, top = 23, bottom = 40;
  const x = index => left + index * ((width - left - right) / Math.max(1, values.length - 1));
  const y = value => top + (total - value) * ((height - top - bottom) / total);
  const path = values.map((value, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(value).toFixed(1)}`).join(" ");
  const yTicks = [0, Math.round(total / 4), Math.round(total / 2), Math.round(3 * total / 4), total];
  const ariaLabel = isZh ? `${label}，终点为 ${values.at(-1)}/${total}` : `${label} ends at ${values.at(-1)} of ${total}`;
  element.classList.toggle("strict-curve", strict);
  element.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(ariaLabel)}">
      ${yTicks.map(value => `<line class="grid-line" x1="${left}" y1="${y(value)}" x2="${width-right}" y2="${y(value)}"></line><text x="${left-11}" y="${y(value)+4}" text-anchor="end">${value}</text>`).join("")}
      <line class="axis-line" x1="${left}" y1="${height-bottom}" x2="${width-right}" y2="${height-bottom}"></line>
      <path class="curve-line" d="${path}"></path>
      ${values.map((value, index) => `<circle class="curve-point" cx="${x(index)}" cy="${y(value)}" r="4"></circle><text x="${x(index)}" y="${height-14}" text-anchor="middle">${index+1}</text>${index === values.length-1 ? `<text class="value-label" x="${x(index)-8}" y="${y(value)-12}" text-anchor="end">${value}</text>` : ""}`).join("")}
      <text x="${(left + width-right)/2}" y="${height-2}" text-anchor="middle">${t("orderedEvaluation")}</text>
    </svg>`;
}

function videoFigures(videos, {controls = false} = {}) {
  const playback = controls ? "controls" : "autoplay";
  return videos.map((video, index) => `
    <figure class="case-figure ${index % 2 ? "case-figure--reverse" : ""} ${video.verdict.includes("failure") ? "case-figure--failure" : ""}">
      <div class="case-media">
        <video ${playback} loop muted playsinline preload="metadata" poster="${escapeHtml(video.poster)}" src="${escapeHtml(video.video)}"></video>
        <button class="trace-open" type="button" data-video-id="${escapeHtml(video.id)}" aria-label="${t("openEvidence")} ${escapeHtml(video.title)}">${isZh ? "调用链" : "Trace"}</button>
      </div>
      <figcaption>
        <span>${escapeHtml(video.subtitle)}</span>
        <strong>${escapeHtml(video.title)}</strong>
        <small>${escapeHtml(video.task)} · seed ${video.seed} · ${fmtSeconds(video.duration_s)}</small>
      </figcaption>
    </figure>`).join("");
}

function renderVideos(media, plusMedia, robotwinMedia, actComparison) {
  const primaryVideos = media.videos.map(localizeVideo);
  const plusVideos = (plusMedia?.videos ?? []).map(localizeVideo);
  const robotwinVideos = (robotwinMedia?.videos ?? []).map(localizeVideo);
  const beforeVideo = actComparison?.before ? localizeVideo(actComparison.before) : null;
  const diagnosticVideos = beforeVideo ? [beforeVideo] : [];
  const videos = [...primaryVideos, ...plusVideos, ...robotwinVideos, ...diagnosticVideos];
  state.videos = new Map(videos.map(video => [video.id, video]));
  document.getElementById("demo-video-grid").innerHTML = videoFigures(videos, {controls: true});
  const afterVideo = state.videos.get(actComparison?.after_id);
  document.getElementById("act-before-after-grid").innerHTML = videoFigures(
    [beforeVideo, afterVideo].filter(Boolean),
    {controls: true},
  );
  document.getElementById("video-grid").innerHTML = videoFigures(primaryVideos);
  document.getElementById("plus-video-grid").innerHTML = videoFigures(plusVideos);
  document.getElementById("robotwin-video-grid").innerHTML = videoFigures(robotwinVideos);
  document.querySelectorAll("[data-video-id]").forEach(button => {
    button.addEventListener("click", () => openVideo(state.videos.get(button.dataset.videoId)));
  });
}

function openVideo(video) {
  if (!video) return;
  const dialog = document.getElementById("video-dialog");
  const player = document.getElementById("dialog-video");
  document.getElementById("dialog-scope").textContent = video.subtitle;
  document.getElementById("dialog-title").textContent = video.title;
  const perturbation = video.perturbation ? ` · ${video.perturbation}` : "";
  const traceScope = String(video.trace_scope ?? t("traceUnavailable")).replaceAll("_", " ");
  document.getElementById("dialog-meta").textContent = `${video.task} · seed ${video.seed}${perturbation} · ${traceScope}`;
  const succeeded = !String(video.verdict).includes("failure");
  const rawVerdictLabel = succeeded ? "SIMULATOR SUCCESS" : "SIMULATOR FAILURE";
  const verdictLabel = isZh ? STATUS_ZH[rawVerdictLabel] : rawVerdictLabel;
  const verdictElement = document.getElementById("dialog-verdict");
  document.getElementById("dialog-verdict").textContent = verdictLabel;
  verdictElement.classList.toggle("failed", !succeeded);
  document.getElementById("dialog-trace-note").textContent = video.trace_note ?? "";
  document.getElementById("video-tool-chain").innerHTML = video.tool_chain.map(step => {
    const verdict = step.tool === "final_simulator_verdict";
    const rawStatus = step.ok ? "PASS" : verdict ? "FAIL" : "RETRY";
    const status = isZh ? STATUS_ZH[rawStatus] : rawStatus;
    const detail = step.detail ? `<small>${escapeHtml(step.detail)}</small>` : "";
    return `<li class="${step.ok ? "" : "failed"} ${verdict ? "verdict-step" : ""}"><span class="trace-call">${escapeHtml(step.tool)}${detail}</span><span>${status}</span></li>`;
  }).join("");
  player.src = video.video;
  player.poster = video.poster;
  player.load();
  dialog.showModal();
  player.play().catch(() => {});
}

function renderRobotwin(robotwin) {
  document.getElementById("robotwin-pure").textContent = `${robotwin.pure_engineer_solved}/${robotwin.tasks}`;
  document.getElementById("robotwin-three-role").textContent = `${robotwin.three_role_solved}/${robotwin.tasks}`;
  document.getElementById("robotwin-episode").textContent = `${robotwin.successful_episodes}/${robotwin.verdict_episodes} (${fmtPercent(robotwin.per_episode_success_rate)})`;
  document.getElementById("robotwin-window").textContent = `${robotwin.elapsed_hours.at(-1).toFixed(2)} h`;
}

function renderLiberoPlus(plus) {
  const total = plus.panel.identities;
  document.getElementById("hero-plus-score").textContent = `${plus.adaptive.success}/${total}`;
  document.getElementById("hero-plus-uplift").textContent = `+${plus.uplift.percentage_points.toFixed(1)} pp`;
  document.getElementById("plus-fixed-score").textContent = `${plus.fixed.success}/${total}`;
  document.getElementById("plus-fixed-rate").textContent = fmtPercent(plus.fixed.rate);
  document.getElementById("plus-adaptive-score").textContent = `${plus.adaptive.success}/${total}`;
  document.getElementById("plus-adaptive-rate").textContent = fmtPercent(plus.adaptive.rate);
  document.getElementById("plus-uplift-score").textContent = `+${plus.uplift.percentage_points.toFixed(1)} pp`;
  document.getElementById("plus-uplift-identities").textContent = isZh
    ? `新增 ${plus.uplift.successes} 个成功实例`
    : `+${plus.uplift.successes} solved identities`;

  const efficiency = plus.adaptive.efficiency;
  document.getElementById("plus-token-cost").textContent = fmtBillion(efficiency.total_tokens);
  document.getElementById("plus-active-wall").textContent = fmtHours(efficiency.active_wall_s);
  document.getElementById("plus-attempt-count").textContent = fmtInt(efficiency.valid_attempts);
  document.getElementById("plus-unmetered").textContent = fmtInt(efficiency.unmetered_vlm_calls);

  const names = {
    r160_cluster: isZh ? "r160 / 语义聚类" : "r160 / semantic cluster",
    r160_wave: isZh ? "r160 / 广覆盖残差" : "r160 / broad residual",
    r164_semantic: isZh ? "r164 / 关系修复" : "r164 / relational repair",
    r164_canonical_pass2: isZh ? "r164 / 规范 Pass@2" : "r164 / canonical Pass@2",
  };
  document.getElementById("plus-stage-grid").innerHTML = plus.stages.map((stage, index) => `
    <article>
      <span>0${index + 1} / ${escapeHtml(names[stage.stage])}</span>
      <strong>+${stage.new_successes}</strong>
      <p>${stage.cumulative_success}/${total} ${t("cumulative")}</p>
      <dl>
        <div><dt>${t("tokens")}</dt><dd>${fmtMillion(stage.efficiency.total_tokens)}</dd></div>
        <div><dt>${t("activeWall")}</dt><dd>${fmtHours(stage.efficiency.active_wall_s)}</dd></div>
        <div><dt>${t("attempts")}</dt><dd>${stage.efficiency.valid_attempts}</dd></div>
      </dl>
    </article>`).join("");
}

function closeVideo() {
  const dialog = document.getElementById("video-dialog");
  const player = document.getElementById("dialog-video");
  player.pause();
  player.removeAttribute("src");
  player.load();
  dialog.close();
}

function renderCodeExperiment(matched) {
  const onRate = matched.success.code_on.success / matched.success.code_on.episodes;
  const offRate = matched.success.code_off.success / matched.success.code_off.episodes;
  document.getElementById("code-chart").innerHTML = [
    {label: t("codeOn"), rate: onRate, className: ""},
    {label: t("codeOff"), rate: offRate, className: "off"},
  ].map(row => `
    <div class="bar-row ${row.className}">
      <strong>${row.label}</strong>
      <div class="bar-track"><div class="bar-fill" style="width:${100 * row.rate}%"></div></div>
      <span class="bar-value">${(100 * row.rate).toFixed(1)}%</span>
    </div>`).join("");

  const efficiency = matched.efficiency;
  const rows = [
    {label: t("medianEpisodeTokens"), value: `${fmtMillion(efficiency.median_total_tokens.code_on)} vs ${fmtMillion(efficiency.median_total_tokens.code_off)}`, reduction: efficiency.median_total_tokens.reduction},
    {label: t("aggregateTokens"), value: `${fmtMillion(efficiency.total_tokens.code_on)} vs ${fmtMillion(efficiency.total_tokens.code_off)}`, reduction: efficiency.total_tokens.reduction},
    {label: t("medianVlmCalls"), value: `${efficiency.median_vlm_calls.code_on} vs ${efficiency.median_vlm_calls.code_off}`, reduction: efficiency.median_vlm_calls.reduction},
    {label: t("medianWallTime"), value: `${fmtWholeSeconds(efficiency.median_wall_s.code_on)} vs ${fmtWholeSeconds(efficiency.median_wall_s.code_off)}`, reduction: efficiency.median_wall_s.reduction},
  ];
  document.getElementById("efficiency-grid").innerHTML = rows.map(row => `
    <div class="efficiency-item"><span>${row.label}</span><strong>${row.value}</strong><small>${(100 * row.reduction).toFixed(1)}% ${t("lowerWithCode")}</small></div>`).join("");
}

function renderComparison(publication) {
  const sourceById = {
    "roboharness-memory": "https://arxiv.org/abs/2603.24060",
    "roboharness-orchestration": "https://arxiv.org/abs/2607.18060",
    "openeta-codex": "https://arxiv.org/abs/2608.03924",
    "vla-evaluation-harness": "https://github.com/allenai/vla-evaluation-harness",
    "enpire": "https://arxiv.org/abs/2606.19980",
  };
  document.getElementById("comparison-body").innerHTML = publication.comparisons.map(row => {
    const display = isZh ? {...row, ...(COMPARISON_ZH[row.id] ?? {})} : row;
    return `
    <tr>
      <td><a class="comparison-system" href="${sourceById[row.id]}" target="_blank" rel="noreferrer">${escapeHtml(display.system)}</a><span class="comparison-date">${escapeHtml(row.date)}</span></td>
      <td>${escapeHtml(display.evaluation)}</td>
      <td>${escapeHtml(display.reported_result)}</td>
      <td>${escapeBrand(display.policy_dependency)}<br><br><strong>${t("successFeedback")}</strong> ${escapeBrand(display.visible_success_checker)}</td>
      <td><span class="not-comparable">${t("notDirect")}</span><br>${escapeBrand(display.why_not_direct)}</td>
    </tr>`;
  }).join("");
  const gaps = isZh ? POSITIONING_ZH.gaps : publication.positioning.gaps;
  const advantages = isZh ? POSITIONING_ZH.advantages : publication.positioning.advantages;
  document.getElementById("gap-list").innerHTML = gaps.map(item => `<li>${escapeBrand(item)}</li>`).join("");
  document.getElementById("advantage-list").innerHTML = advantages.map(item => `<li>${escapeBrand(item)}</li>`).join("");
}

function render(data) {
  document.getElementById("data-status").textContent = "";
  const publication = data.publication;
  const experiments = publication.experiments;
  document.getElementById("hero-adaptive").textContent = `${publication.headline.solved_tasks}/${publication.headline.total_tasks}`;
  renderLiberoPlus(experiments.libero_plus);
  renderRobotwin(experiments.robotwin_historical);
  renderVideos(
    publication.media,
    experiments.libero_plus.media,
    experiments.robotwin_historical.media,
    experiments.act.before_after,
  );
  renderLineChart("adaptive-chart", experiments.adaptive_sequential.pass_curve, 120, t("sequentialAdaptive"));
  renderLineChart("strict-chart", experiments.strict_standard130.pass_curve, 130, t("strictPass"), true);
  renderCodeExperiment(experiments.matched_code);
  renderComparison(publication);
}

document.getElementById("video-close").addEventListener("click", closeVideo);
document.getElementById("video-dialog").addEventListener("click", event => {
  if (event.target === event.currentTarget) closeVideo();
});
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && document.getElementById("video-dialog").open) closeVideo();
});

const outlineLinks = new Map([...document.querySelectorAll(".article-outline a")].map(link => [link.getAttribute("href").slice(1), link]));
const observer = new IntersectionObserver(entries => {
  entries.filter(entry => entry.isIntersecting).forEach(entry => {
    outlineLinks.forEach(link => link.removeAttribute("aria-current"));
    outlineLinks.get(entry.target.id)?.setAttribute("aria-current", "true");
  });
}, {rootMargin: "-20% 0px -70% 0px"});
outlineLinks.forEach((_link, id) => {
  const section = document.getElementById(id);
  if (section) observer.observe(section);
});

fetch("data.json")
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(render)
  .catch(error => {
    document.getElementById("data-status").textContent = `${t("dataUnavailable")}: ${error.message}`;
  });
