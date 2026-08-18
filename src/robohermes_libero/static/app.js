const state = { data: null, filter: "all", query: "" };

const fmtInt = value => value == null ? "-" : new Intl.NumberFormat("en-US").format(value);
const fmtTime = value => value == null ? "-" : `${Math.round(value)}s`;
const shortRelease = value => !value ? "-" : value.replace("libero-clean-", "");
const escapeHtml = value => String(value ?? "").replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);

function renderCurve(values, total) {
  const width = 760, height = 278, left = 52, right = 24, top = 24, bottom = 40;
  const x = index => left + index * ((width - left - right) / Math.max(1, values.length - 1));
  const y = value => top + (total - value) * ((height - top - bottom) / total);
  const path = values.map((value, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(value).toFixed(1)}`).join(" ");
  const yTicks = [0, 30, 60, 90, 120];
  document.getElementById("curve-chart").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Coverage rises to ${values.at(-1)} of ${total} tasks">
      ${yTicks.map(value => `<line class="grid-line" x1="${left}" y1="${y(value)}" x2="${width-right}" y2="${y(value)}"></line><text x="${left-12}" y="${y(value)+4}" text-anchor="end">${value}</text>`).join("")}
      <line class="axis-line" x1="${left}" y1="${height-bottom}" x2="${width-right}" y2="${height-bottom}"></line>
      <path class="curve-line" d="${path}"></path>
      ${values.map((value, index) => `<circle class="curve-point" cx="${x(index)}" cy="${y(value)}" r="4"></circle><text x="${x(index)}" y="${height-15}" text-anchor="middle">${index+1}</text>${index === values.length-1 ? `<text class="value" x="${x(index)-7}" y="${y(value)-13}" text-anchor="end">${value}</text>` : ""}`).join("")}
      <text x="${(left + width-right)/2}" y="${height-2}" text-anchor="middle">ordered seed k</text>
    </svg>`;
}

function renderSuites(suites) {
  const order = ["libero_spatial", "libero_object", "libero_goal", "libero_90"];
  document.getElementById("suite-chart").innerHTML = order.map(name => {
    const row = suites[name];
    const percent = 100 * row.rate;
    return `<div class="suite-row"><span>${escapeHtml(name.replace("libero_", ""))}</span><div class="suite-track"><div class="suite-fill" style="width:${percent}%"></div></div><span class="suite-value">${row.solved_tasks}/${row.total_tasks}</span></div>`;
  }).join("");
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
    <div class="command-row"><span>${escapeHtml(name)}</span><code>${escapeHtml(command)}</code><button type="button" data-copy="${escapeHtml(command)}">Copy</button></div>`).join("");
  document.querySelectorAll("[data-copy]").forEach(button => button.addEventListener("click", async () => {
    await navigator.clipboard.writeText(button.dataset.copy);
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = "Copy"; }, 1200);
  }));
}

function render(data) {
  state.data = data;
  const result = data.result;
  document.getElementById("claim-boundary").textContent = result.claim_boundary;
  document.getElementById("headline-score").textContent = `${result.solved_tasks}/${result.total_tasks}`;
  document.getElementById("headline-rate").textContent = `${(100 * result.rate).toFixed(1)}% task coverage`;
  document.getElementById("metric-solved").textContent = `${result.solved_tasks} / ${result.total_tasks}`;
  document.getElementById("metric-rounds").textContent = result.k ?? result.pass_curve.length;
  document.getElementById("metric-success").textContent = result.task_success_records ?? result.verdicts?.task_success ?? "-";
  document.getElementById("usage-scope").textContent = result.usage_scope;
  renderCurve(result.pass_curve, result.total_tasks);
  renderSuites(result.by_suite);
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

fetch("data.json")
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(render)
  .catch(error => {
    document.getElementById("claim-boundary").textContent = `Dashboard data failed to load: ${error.message}`;
  });
