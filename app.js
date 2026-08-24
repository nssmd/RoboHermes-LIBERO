const state = { data: null, filter: "all", query: "", videos: new Map() };

const fmtInt = value => value == null ? "-" : new Intl.NumberFormat("en-US").format(value);
const fmtTime = value => value == null ? "-" : value >= 60 ? `${(value / 60).toFixed(1)}m` : `${Math.round(value)}s`;
const fmtMillion = value => `${(value / 1_000_000).toFixed(2)}M`;
const fmtBillion = value => `${(value / 1_000_000_000).toFixed(3)}B`;
const fmtHours = value => `${(value / 3600).toFixed(2)}h`;
const fmtPercent = value => `${(100 * value).toFixed(1)}%`;
const shortRelease = value => !value ? "-" : value.replace("libero-clean-", "");
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
  element.classList.toggle("strict-curve", strict);
  element.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(label)} ends at ${values.at(-1)} of ${total}">
      ${yTicks.map(value => `<line class="grid-line" x1="${left}" y1="${y(value)}" x2="${width-right}" y2="${y(value)}"></line><text x="${left-11}" y="${y(value)+4}" text-anchor="end">${value}</text>`).join("")}
      <line class="axis-line" x1="${left}" y1="${height-bottom}" x2="${width-right}" y2="${height-bottom}"></line>
      <path class="curve-line" d="${path}"></path>
      ${values.map((value, index) => `<circle class="curve-point" cx="${x(index)}" cy="${y(value)}" r="4"></circle><text x="${x(index)}" y="${height-14}" text-anchor="middle">${index+1}</text>${index === values.length-1 ? `<text class="value-label" x="${x(index)-8}" y="${y(value)-12}" text-anchor="end">${value}</text>` : ""}`).join("")}
      <text x="${(left + width-right)/2}" y="${height-2}" text-anchor="middle">ordered evaluation k</text>
    </svg>`;
}

function videoFigures(videos) {
  return videos.map((video, index) => `
    <figure class="case-figure ${index % 2 ? "case-figure--reverse" : ""}">
      <div class="case-media">
        <video autoplay loop muted playsinline preload="metadata" poster="${escapeHtml(video.poster)}" src="${escapeHtml(video.video)}"></video>
        <button class="trace-open" type="button" data-video-id="${escapeHtml(video.id)}" aria-label="Open evidence for ${escapeHtml(video.title)}">Trace</button>
      </div>
      <figcaption>
        <span>${escapeHtml(video.subtitle)}</span>
        <strong>${escapeHtml(video.title)}</strong>
        <small>${escapeHtml(video.task)} · seed ${video.seed} · ${video.duration_s.toFixed(1)}s</small>
      </figcaption>
    </figure>`).join("");
}

function renderVideos(media, plusMedia, robotwinMedia) {
  const plusVideos = plusMedia?.videos ?? [];
  const robotwinVideos = robotwinMedia?.videos ?? [];
  const videos = [...media.videos, ...plusVideos, ...robotwinVideos];
  state.videos = new Map(videos.map(video => [video.id, video]));
  document.getElementById("video-grid").innerHTML = videoFigures(media.videos);
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
  const traceScope = String(video.trace_scope ?? "trace unavailable").replaceAll("_", " ");
  document.getElementById("dialog-meta").textContent = `${video.task} · seed ${video.seed}${perturbation} · ${traceScope}`;
  document.getElementById("dialog-verdict").textContent = "SIMULATOR SUCCESS";
  document.getElementById("dialog-trace-note").textContent = video.trace_note ?? "";
  document.getElementById("video-tool-chain").innerHTML = video.tool_chain.map(step => {
    const verdict = step.tool === "final_simulator_verdict";
    return `<li class="${step.ok ? "" : "failed"} ${verdict ? "verdict-step" : ""}"><span>${escapeHtml(step.tool)}</span><span>${step.ok ? "PASS" : "RETRY"}</span></li>`;
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
  document.getElementById("plus-uplift-identities").textContent = `+${plus.uplift.successes} solved identities`;

  const efficiency = plus.adaptive.efficiency;
  document.getElementById("plus-token-cost").textContent = fmtBillion(efficiency.total_tokens);
  document.getElementById("plus-active-wall").textContent = fmtHours(efficiency.active_wall_s);
  document.getElementById("plus-attempt-count").textContent = fmtInt(efficiency.valid_attempts);
  document.getElementById("plus-unmetered").textContent = fmtInt(efficiency.unmetered_vlm_calls);

  const names = {
    r160_cluster: "r160 / semantic cluster",
    r160_wave: "r160 / broad residual",
    r164_semantic: "r164 / relational repair",
    r164_canonical_pass2: "r164 / canonical Pass@2",
  };
  document.getElementById("plus-stage-grid").innerHTML = plus.stages.map((stage, index) => `
    <article>
      <span>0${index + 1} / ${escapeHtml(names[stage.stage])}</span>
      <strong>+${stage.new_successes}</strong>
      <p>${stage.cumulative_success}/${total} cumulative</p>
      <dl>
        <div><dt>tokens</dt><dd>${fmtMillion(stage.efficiency.total_tokens)}</dd></div>
        <div><dt>active wall</dt><dd>${fmtHours(stage.efficiency.active_wall_s)}</dd></div>
        <div><dt>attempts</dt><dd>${stage.efficiency.valid_attempts}</dd></div>
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
    {label: "Code-on", rate: onRate, className: ""},
    {label: "Code-off", rate: offRate, className: "off"},
  ].map(row => `
    <div class="bar-row ${row.className}">
      <strong>${row.label}</strong>
      <div class="bar-track"><div class="bar-fill" style="width:${100 * row.rate}%"></div></div>
      <span class="bar-value">${(100 * row.rate).toFixed(1)}%</span>
    </div>`).join("");

  const efficiency = matched.efficiency;
  const rows = [
    {label: "Median episode tokens", value: `${fmtMillion(efficiency.median_total_tokens.code_on)} vs ${fmtMillion(efficiency.median_total_tokens.code_off)}`, reduction: efficiency.median_total_tokens.reduction},
    {label: "Aggregate tokens", value: `${fmtMillion(efficiency.total_tokens.code_on)} vs ${fmtMillion(efficiency.total_tokens.code_off)}`, reduction: efficiency.total_tokens.reduction},
    {label: "Median VLM calls", value: `${efficiency.median_vlm_calls.code_on} vs ${efficiency.median_vlm_calls.code_off}`, reduction: efficiency.median_vlm_calls.reduction},
    {label: "Median wall time", value: `${Math.round(efficiency.median_wall_s.code_on)}s vs ${Math.round(efficiency.median_wall_s.code_off)}s`, reduction: efficiency.median_wall_s.reduction},
  ];
  document.getElementById("efficiency-grid").innerHTML = rows.map(row => `
    <div class="efficiency-item"><span>${row.label}</span><strong>${row.value}</strong><small>${(100 * row.reduction).toFixed(1)}% lower with code</small></div>`).join("");
}

function renderComparison(publication) {
  const sourceById = {
    "roboharness-memory": "https://arxiv.org/abs/2603.24060",
    "roboharness-orchestration": "https://arxiv.org/abs/2607.18060",
    "openeta-codex": "https://arxiv.org/abs/2608.03924",
    "vla-evaluation-harness": "https://github.com/allenai/vla-evaluation-harness",
    "enpire": "https://arxiv.org/abs/2606.19980",
  };
  document.getElementById("comparison-body").innerHTML = publication.comparisons.map(row => `
    <tr>
      <td><a class="comparison-system" href="${sourceById[row.id]}" target="_blank" rel="noreferrer">${escapeHtml(row.system)}</a><span class="comparison-date">${escapeHtml(row.date)}</span></td>
      <td>${escapeHtml(row.evaluation)}</td>
      <td>${escapeHtml(row.reported_result)}</td>
      <td>${escapeBrand(row.policy_dependency)}<br><br><strong>Success feedback:</strong> ${escapeBrand(row.visible_success_checker)}</td>
      <td><span class="not-comparable">Not direct</span><br>${escapeBrand(row.why_not_direct)}</td>
    </tr>`).join("");
  document.getElementById("gap-list").innerHTML = publication.positioning.gaps.map(item => `<li>${escapeBrand(item)}</li>`).join("");
  document.getElementById("advantage-list").innerHTML = publication.positioning.advantages.map(item => `<li>${escapeBrand(item)}</li>`).join("");
}

function renderTasks() {
  const rows = state.data.tasks.filter(row => {
    const filterMatch = state.filter === "all" || (state.filter === "solved" ? row.solved : !row.solved);
    return filterMatch && row.task_key.toLowerCase().includes(state.query);
  });
  document.getElementById("task-body").innerHTML = rows.map(row => `
    <tr>
      <td><strong>${escapeHtml(row.task_key)}</strong></td>
      <td>${escapeHtml(row.suite.replace("libero_", ""))}</td>
      <td><span class="verdict ${row.solved ? "solved" : ""}">${row.solved ? "success" : "open"}</span></td>
      <td>${row.seed ?? "-"}</td>
      <td title="${escapeHtml(row.release_id)}">${escapeHtml(shortRelease(row.release_id))}</td>
      <td>${fmtInt(row.total_tokens)}</td>
      <td>${fmtTime(row.elapsed_s)}</td>
      <td class="evidence-name" title="${escapeHtml(row.video)}">${escapeHtml(row.video || "-")}</td>
    </tr>`).join("");
  document.getElementById("table-count").textContent = `${rows.length} of ${state.data.tasks.length} tasks`;
}

function renderCommands(commands) {
  document.getElementById("command-list").innerHTML = Object.entries(commands).map(([name, command]) => `
    <div class="command-row"><span>${escapeHtml(name)}</span><code>${escapeHtml(command)}</code><button type="button" data-copy="${escapeHtml(command)}" aria-label="Copy ${escapeHtml(name)} command" title="Copy">⧉</button></div>`).join("");
  document.querySelectorAll("[data-copy]").forEach(button => button.addEventListener("click", async () => {
    await navigator.clipboard.writeText(button.dataset.copy);
    button.textContent = "✓";
    setTimeout(() => { button.textContent = "⧉"; }, 1200);
  }));
}

function render(data) {
  state.data = data;
  document.getElementById("data-status").textContent = "";
  const publication = data.publication;
  const experiments = publication.experiments;
  document.getElementById("hero-adaptive").textContent = `${publication.headline.solved_tasks}/${publication.headline.total_tasks}`;
  renderLiberoPlus(experiments.libero_plus);
  renderRobotwin(experiments.robotwin_historical);
  renderVideos(publication.media, experiments.libero_plus.media, experiments.robotwin_historical.media);
  renderLineChart("adaptive-chart", experiments.adaptive_sequential.pass_curve, 120, "Sequential adaptive coverage");
  renderLineChart("strict-chart", experiments.strict_standard130.pass_curve, 130, "Strict Standard-130 Pass at k", true);
  renderCodeExperiment(experiments.matched_code);
  renderComparison(publication);
  renderTasks();
  renderCommands(data.commands);
}

document.querySelectorAll("[data-filter]").forEach(button => button.addEventListener("click", () => {
  state.filter = button.dataset.filter;
  document.querySelectorAll("[data-filter]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
  renderTasks();
}));

document.getElementById("task-search").addEventListener("input", event => {
  state.query = event.target.value.trim().toLowerCase();
  renderTasks();
});

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
    document.getElementById("data-status").textContent = `Evidence data unavailable: ${error.message}`;
  });
