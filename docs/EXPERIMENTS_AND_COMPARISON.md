# RoboHermes 实验盘点与竞品对比

更新日期：2026-08-20
检索窗口：2026-07-20 至 2026-08-20；为解释方法脉络，另纳入 2026 年 3 月的第一篇 RoboHarness 和 2026 年 6 月的 ENPIRE。

## 结论摘要

RoboHermes 当前最扎实的结论不是“在同一榜单上超过 RoboHarness 或 OpenETA”，而是下面四点：

1. 在 840 个分层 LIBERO-Plus identity 上，fixed single-attempt 为 `261/840`，adaptive Pass@2 为 `398/840`，增加 137 个成功 identity，即 `+16.3` 个百分点。七类扰动与三套 short suite 均有完整 final simulator verdict。
2. 在覆盖全部 120 个 LIBERO short tasks 的持续开发过程中，Native simulator success 覆盖从顺序实验的 Pass@1 `32/120` 增长到 Pass@10 `83/120`，后续 residual releases 将跨版本累计覆盖锁定为 `95/120`。
3. 在 120 个任务、5 个匹配 seed、每组 600 个 task-seed episode 的 Code-on/off 实验中，固化后的代码技能把 episode success 从 `129/600` 提高到 `174/600`，提升 `7.5` 个百分点。McNemar 精确检验 `p=8.06e-5`，task-cluster bootstrap 95% CI 为 `+3.7` 至 `+11.5` 个百分点。
4. 在独立的 118-task 匹配效率面板中，Code-on 的中位 episode token 为 `2.58M`，Code-off 为 `3.65M`，降低 `29.4%`；中位 wall time 从 `845s` 降至 `701s`。这支持“成功经验转成代码后，可减少重复 VLM 推理”的机制结论。
5. 历史 RoboTwin campaign 在 50 个任务上记录了 pure Engineer `9/50` 与三角色 task-level pass@k `36/50`，严格 episode 为 `104/422 = 24.6%`。该 campaign 的 87% 相邻 attempt 重叠，因此只支持并行 solution-discovery coverage，不支持顺序学习或 72% 单次成功率。

当前最大的缺口同样明确：没有正式 real-robot task-rate，没有预注册 adaptive train/holdout promotion，也没有异构 policy handoff 实验。LIBERO-Plus `398/840` 与 short `95/120` 都是跨 release 的 adaptive development coverage，而不是单一固定 release 的常规成功率。

These protocols are not a shared leaderboard.

## 1. 目前跑了哪些实验

### 1.1 LIBERO-Plus 分层扰动面板

该面板包含 840 个 identity：七类官方扰动各 120 个，Spatial、Object、Goal 三套 short suite 各 280 个。每个 identity 使用 seed 0；fixed arm 只有一次尝试，adaptive arm 只对选定 fixed failures 启用后续审核 release。成功仅取最终 simulator verdict。

| 指标 | Fixed | Adaptive |
|---|---:|---:|
| Success | `261/840 = 31.1%` | `398/840 = 47.4%` |
| Failure | `579` | `442` |
| 增益 | - | `+137 identities / +16.3 pp` |
| Agent-visible checker/latch | 否 | 否 |

四个 adaptive stage 分别新增 `15, 104, 6, 12` 个成功 identity。所有 adaptive 有效尝试累计 `1,473,552,635` metered tokens，active wall time `16.35h`，unmetered VLM calls 为 0。最大类别增益来自 Language Instructions（`+21.7 pp`），最小来自 Sensor Noise（`+5.8 pp`）。这说明自适应 release 在完整扰动面板上带来广泛增益，但不等价于固定 policy 或 held-out generalization。

### 1.2 Adaptive task-level Pass@10

| 项目 | 数值 | 能说明什么 | 不能说明什么 |
|---|---:|---|---|
| 最终累计覆盖 | `95/120 = 79.2%` | 持续迭代后，系统曾在 95 个不同任务上取得 simulator-confirmed success | 不是单一 release、固定方法或冻结 policy 的 Pass@10 |
| Spatial | `9/10` | 空间关系任务覆盖较高 | 不代表每个 seed 都稳定成功 |
| Object | `10/10` | Object 子集所有任务至少有一个 native success | 不等于 100% episode success |
| Goal | `9/10` | Goal 子集覆盖 9 个任务 | `libero_goal/5` 的 seed 0-9 均无 native success |
| LIBERO-90 | `67/90` | 长尾任务仍取得 67 个不同任务成功 | 剩余 23 个任务尚未解决 |

这 95 个任务由 67 个 strict Standard-130 short successes 和 28 个不重叠的 adaptive residual successes 构成。公开 evidence bundle 每个成功任务保留一条 canonical native-success row，可以精确 replay `95/120`，但不包含所有失败和基础设施记录，因此不能用它估算完整 campaign 成本。

### 1.3 十轮顺序自进化实验

顺序曲线为：

```text
Pass@1  32/120
Pass@2  45/120
Pass@3  52/120
Pass@4  66/120
Pass@5  71/120
Pass@6  76/120
Pass@7  81/120
Pass@8  82/120
Pass@9  82/120
Pass@10 83/120
```

该实验累计计量 `2,342,408,295` tokens，10 轮 active wall time 为 `39,922.42s`，即 `11.09h`。release 会随诊断和通过 harness 的代码变化而更新，所以它测的是 adaptive development process，而非固定模型的随机重试曲线。

这条曲线支持“覆盖任务数随持续试验和代码固化增加”。它没有证明每一轮单位 token 的边际收益单调增加，也没有把后续 12 个 residual successes 伪接到原来的十轮横轴上。

### 1.4 Strict Standard-130 Pass@10

该协议覆盖 130 个任务，包括 Spatial、Object、Goal、LIBERO-10 和 LIBERO-90。Agent 看不到 `check_task`、success latch、object pose 或 policy checkpoint；成功只来自工具循环结束后的 final simulator verdict。

| 指标 | 数值 |
|---|---:|
| Task-level Pass@10 | `67/130 = 51.5%` |
| Pass curve | `23, 35, 43, 49, 56, 60, 61, 63, 64, 67` |
| 最终 task-seed verdicts | `846` |
| 成功 / 失败 | `67 / 779` |
| Metered tokens | `2,882,111,476` |
| VLM calls | `43,076` |
| Campaign wall time | `20.13h` |

Suite 结果为 Spatial `9/10`、Object `10/10`、Goal `7/10`、LIBERO-10 `0/10`、LIBERO-90 `41/90`。LIBERO-10 的 `0/10` 是当前系统的硬缺口，不能被 adaptive headline 遮住。

这条 Pass@k 曲线不是进化曲线。前五轮与后五轮的逐轮中位数相比，token 下降 `13.6%`、VLM calls 下降 `3.1%`，但 wall time 反而增加 `8.0%`；而且 residual task set 与 release 都在变化。因此不能据此宣称模型“越做越快”。更快的因果证据来自 matched Code-on/off 面板。

### 1.5 Matched Code-on/off

“Code”在这里不是笼统的视觉固化。Code-on 暴露由 Round 1 成功轨迹固化并通过 canary 的 `visual_pick_place` compound；Code-off 保留相同的 base tools，但不暴露该 compound。两组使用相同 release、模型、medium reasoning、任务、seed 和预算。

五个 seed 的正式配对结果：

| 指标 | Code-on | Code-off |
|---|---:|---:|
| Episode success | `174/600 = 29.0%` | `129/600 = 21.5%` |
| Task-level Pass@5 | `71/120` | `58/120` |
| Infrastructure rows excluded | `29` | `32` |

配对表为 both-success `88`、Code-on-only `86`、Code-off-only `41`、both-failure `385`。每个 seed 的 Code-on 增益均为正，分别增加 `7, 10, 9, 7, 12` 个成功 episode。

独立 seed-21 效率面板覆盖 118 个严格匹配任务：

| 指标 | Code-on | Code-off | 降幅 |
|---|---:|---:|---:|
| Median total tokens | `2.58M` | `3.65M` | `29.4%` |
| Aggregate tokens | `366.34M` | `459.73M` | `20.3%` |
| Median VLM calls | `29.5` | `40.5` | `27.2%` |
| Median wall time | `701s` | `845s` | `17.0%` |

成功显著性和效率不是同一个样本面板，网页和文稿均分开标注。

### 1.6 ACT 数据飞轮

ACT 当前有一个完整 matched case：`libero_spatial_swap/0 seed3`。流程是 code-backed grasp、ACT corrective transport `304` steps、code-backed placement，最终 native simulator verdict 为 success。

它证明成功轨迹转数据、纠错采集、训练和 hybrid execution 可以闭环。它只有 `1/1` 个 matched trial，且不是 held-out，所以不能写成 ACT 的总体成功率或泛化指标。

### 1.7 未纳入公开 headline 的实验

- ASPIRE targeted development 属于诊断和定点修复，不是完整 benchmark 结果。
- 早期 RoboTwin 结果属于另一个平台；新项目页将其作为 historical cross-platform evidence 单列，不混入 LIBERO 排名。当前公开仓库没有完整 RoboTwin episode ledger，只有摘要与 3 个 predicate-confirmed 视频。
- Long-horizon 工作当前由外部 owner 管理，不在本次 LIBERO short 公开仓库和评测盘点范围内。
- 历史失败、损坏视频和 preflight 仍被保留，但不会进入成功画廊或 headline denominator。

## 2. 最近一个月的 RoboHarness 相关工作

检索 GitHub、arXiv、Semantic Scholar 和 OpenAlex 后，必须先区分同名项目。

### 2.1 RoboHarness：异构策略编排

论文：[RoboHarness: Memory-Driven Orchestration of Heterogeneous Robot Policies for Long-Horizon Planning](https://arxiv.org/abs/2607.18060)，2026-07-20 发布，2026-07-28 更新。

这是最近一个月最直接的研究竞品。它把 `pi0.5`、RL-post-trained OpenVLA-OFT 和 TAMP 包装成 agentic skills，通过 Understanding Skills、execution memory、Evolution Skills 和 Memory Bridge 做 capability-aware routing 与 policy handoff。

论文报告：

- Original LIBERO `98.7%`；
- LIBERO-Plus 七类扰动平均 `93.2%`；
- LIBERO-LoHo 平均 progress `97.5%`、success `95.2%`；
- 500 个 custom long-horizon simulations；
- 135 个 real-robot trials。

这些结果依赖训练好的 specialist policies 和预定义对象集的 TAMP。real-robot 系统还使用 ArUco pose pipeline，并对 drawer opening/closing 分别用 50 条 human demonstrations 微调 `pi0.5`。截至 2026-08-18，其[公开仓库](https://github.com/markli1hoshipu/RoboHarness)包含项目网页、图和视频，但没有论文方法代码，因此当前无法按一键脚本独立复现其主表。

### 2.2 RoboHarness：VLA 记忆增强

论文：[RoboHarness: A Memory-Augmented Policy Harness for Vision-Language-Action Model Robustness via In-Context Adaptation](https://arxiv.org/abs/2603.24060)，2026-03-25 发布。

这是另一组作者的同名工作，不是 7 月异构策略论文的早期版本。它在 frozen `pi0`、`pi0.5`、SmolVLA 上加入 Dual-Memory RAG、failure attribution 和 MCP interventions。测试使用自建 LIBERO-RoboHarness OOD tasks 和 LIBERO-PRO 子集，每个 task 约 200 次 rollout，paper 报告 LIBERO-PRO Pos 平均 `57.2%`、Task 平均 `55.2%`，以及 long-horizon task chaining 的大幅提升。

它的[公开仓库](https://github.com/LZY-1021/RoboHarness)包含修改后的任务和核心实现。与 RoboHermes 的 120-task Pass@k 仍不是相同 catalog、policy 或统计单元。

### 2.3 OpenETA for Codex

论文：[ETA: A New Agentic Paradigm for Embodied Tasks](https://arxiv.org/abs/2608.03924)。OpenETA 于 2026-08-03 发布 Codex 版本。

OpenETA 给 Codex 三个 manipulation capabilities：`observe`、`mark_point`、`move_to`，另有 `report_issue`、`check_task`、`finish_episode` 三个 lifecycle calls。它使用 512×512 multi-view/orthographic feedback、5000-step simulator horizon 和最长 5400 秒 attempt timeout。GPT-5.6 Sol medium 在 130 tasks 上报告 Pass@1 `92/130`、Pass@5 `117/130`。

这个分数很强，但 Agent 可以主动调用 native `check_task`，Gateway 还会 latch terminal success。RoboHermes strict 明确禁止这两项。OpenETA 的 Cartesian pose contract、多视角和长预算也更强，所以两者不能只按模型名相同就直接比较。

[OpenETA 代码](https://github.com/OpenMOSS/OpenETA)公开了 branch、versioned operator contract 和 launcher，这是 RoboHermes 需要对齐的工程标准。

### 2.4 AllenAI vla-evaluation-harness

[vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness)是评测基础设施，不是 self-evolving agent 方法。它把 benchmark Docker、model server、episode sharding、batch inference、SQLite recording 和 reproduction reports 统一起来。截至 2026-08，它列出 18 个 benchmark，并持续接入 LIBERO-Plus、RoboTwin、RoboCasa365 等环境。

它对 RoboHermes 的压力不在方法分数，而在可复现性和 benchmark breadth：公开 Docker、统一 schema、shard resume 和独立 reproduction reports 都比当前 RoboHermes 的单仓库 setup 更完整。

### 2.5 ENPIRE

论文：[ENPIRE: Agentic Robot Policy Self-Improvement in the Real World](https://arxiv.org/abs/2606.19980)，项目页：[NVIDIA GEAR ENPIRE](https://research.nvidia.com/labs/gear/enpire/)。

ENPIRE 让 coding agents 管理真实机器人上的 reset、verification、rollout 和 policy improvement，使用最多 8 个 YAM stations 做 physical autoresearch。它报告 showcased tasks 上最高 `99% pass@8`，其中 pass@8 是单个 long rollout 内每个 subtask 最多 8 次基于前次失败的 in-context retries，不是 8 个 i.i.d. samples。论文还提出 MRU 和 MTU 衡量 robot/token utilization，并在 RoboCasa 做固定 40-episode simulation panels。

ENPIRE 与 RoboHermes 的直接任务不同，但它提供了更成熟的“时间轴 + token + 资源利用率 + idea tree”评测范式，也提供了本次项目页的信息设计参考。

### 2.6 同名但不应混入方法对比的项目

- [MiaoDX/roboharness](https://github.com/MiaoDX/roboharness)是机器人代码修改的视觉 regression/proof-pack 工具，不是 VLA memory 或 policy orchestration 方法。
- [Staaaaaaaaar/robo-harness](https://github.com/Staaaaaaaaar/robo-harness)于 2026-08-16 创建，是 Isaac Sim + Unitree Go2 + PointNav 的 ROS 2 MVP，目前只有 CPU mock chain，没有可与 LIBERO 方法比较的正式指标。

## 3. 协议差异

| 系统 | 核心执行能力 | 成功反馈是否给 Agent | 主要评测 | Real robot | 公开复现状态 |
|---|---|---|---|---|---|
| RoboHermes Plus adaptive | RGB-D code skills，审核 release，adaptive Pass@2 | 否；仅 episode 结束后 host verdict | LIBERO-Plus `398/840`，fixed `261/840` | 无正式指标 | final aggregate、分层、成本和 4 个 trace 视频公开 |
| RoboHermes strict | RGB-D code skills，IK/joint trajectory，无 policy checkpoint | 否；仅 episode 结束后 host verdict | Standard-130 Pass@10 `67/130` | 无正式指标 | 代码、setup、compact evidence 已公开；完整 raw campaign 未公开 |
| RoboHermes adaptive | 同上，可在 campaign overlay 中进化 | 否 | LIBERO short cross-release `95/120` | 不在本次 scope | compact replay 可复现；95 不是单 release rerun |
| OpenETA for Codex | Multi-view point marking + Cartesian `move_to` | 是；`check_task` + terminal latch | 130-task Pass@5 `117/130` | interface-level only | 代码和 launcher 已公开 |
| RoboHarness 2026-07 | `pi0.5` + RL OpenVLA-OFT + TAMP + Memory Bridge | 论文未给出同类公开 contract | LIBERO、Plus、LoHo、custom、135 real | 有 | 项目页和视频公开；方法代码未公开 |
| RoboHarness 2026-03 | Frozen VLA + Dual-Memory RAG + MCP interventions | 论文未给出同类公开 contract | custom OOD + LIBERO-PRO | 无正式指标 | 部分方法代码和任务公开 |
| ENPIRE | Coding-agent-driven policy training and physical autoresearch | Task-specific verifier 是 environment API | Real tasks + RoboCasa panels | 8-station fleet | paper/page 公开；官方完整方法仓库未列出 |

## 4. 相较 RoboHarness，我们差在哪里

### 4.1 评测宽度

7 月 RoboHarness 同时给出 original、七类 LIBERO-Plus perturbations、LoHo、500 custom tasks 和 135 real trials。RoboHermes 现在有 840-identity LIBERO-Plus 分层矩阵，但仍缺 LoHo 系统面板、custom-task 泛化和固定 denominator 的 real-robot trials。

### 4.2 Policy 组合与 handoff

RoboHarness 的核心 claim 是异构策略 capability boundary 和 Memory Bridge。RoboHermes 目前主要组合代码技能，ACT 只有一个 hybrid case。我们还没有多 policy routing、handoff state distribution、bridge ablation 或 policy-usage correlation。

### 4.3 Real robot

RoboHarness 有 135 trials，ENPIRE 有 robot fleet。RoboHermes 没有 formal real-robot denominator。公开视频只能证明 simulator execution，不能外推部署安全或现实成功率。

### 4.4 单版本复现

RoboHermes 的 `95/120` 来自多个 release。别人可以 replay evidence，也可以重新启动 adaptive campaign，但不能用 latest release 一次性复现同一个 `95/120`。开源前必须把这条边界放在 headline 附近。

### 4.5 完整公开证据

当前仓库公开 95 条 short success evidence rows、10 个精选视频和 LIBERO-Plus final aggregate/token ledger，仍未公开全部失败视频、全部基础设施记录和每个 raw prompt。内部证据比公开 bundle 完整，第三方仍不能独立审计所有 failure taxonomy。

### 4.6 标准评测基础设施

AllenAI harness 已经把 benchmark/model containers、sharding、recording 和 reproduction reports 产品化。RoboHermes 的 setup 已一键化，但还没有同等广度的 adapter matrix、Docker pinning 和 external reproduction report。

## 5. RoboHermes 的现有优势

### 5.1 代码技能本身可检查

RoboHermes 的技能、Planner/Engineer/Reviewer runtime、evolution overlay 和 release checks 已公开。7 月 RoboHarness 当前只有页面资产，无法直接查看论文所述 orchestration 实现。

### 5.2 Hidden ground truth 隔离更严格

RoboHermes strict 不给 Agent `check_task`、reward、object pose 或 success latch。最终 simulator predicate 只在 episode 结束后由 host 调用。这使 `67/130` 数值偏低，但其“仅凭可见证据行动”的解释边界清楚。

### 5.3 有匹配的代码因果证据

Code-on/off 不只是开发曲线。它在 1,200 个有效 task-seed episodes 上固定模型、release、任务、seed 和预算，只改变 compound code 是否可用，并报告 paired tests 和 cluster uncertainty。

### 5.4 成功和效率一起计量

RoboHermes 记录 prompt/completion/total tokens、VLM calls、wall time 和分阶段时间。当前 matched panel 支持“代码固化降低重复推理”这一机制，而不是只展示更高 success。

### 5.5 不依赖 VLA checkpoint 的独立路线

Strict track 的核心任务执行不需要 `pi0.5`、OpenVLA-OFT 或专用 policy checkpoint。它与异构 policy orchestration 不是互斥路线：未来可以把 policy adapter 当作新 skill，但当前结果能单独衡量 code-first agent 的能力边界。

## 6. 下一步最值得补的实验

按论文价值和可执行性排序：

1. **Adaptive holdout protocol。** 不关闭自进化，而是预注册 train tasks、candidate canary 和 held-out tasks；每次 overlay promotion 必须同时过 source success reproduction 和 held-out non-regression。
2. **固定 release Plus 对照。** 在不继续改代码的条件下，对最终 release 跑一个完整 held-out Plus 面板，区分跨 release discovery coverage 与单版本 generalization。
3. **完整 artifact release。** 发布 95 个 canonical success videos、全部失败/infra rows 的 sanitized index、完整 token/time totals 和 failure taxonomy。大文件可放 GitHub Release，不必塞进 wheel。
4. **Policy-as-skill ablation。** 在不改现有 code-first baseline 的前提下，加入一个 VLA 和一个 TAMP adapter，做 code-only、single-policy、naive routing、capability-aware routing、handoff bridge 五组匹配实验。
5. **Real-robot bounded panel。** 从 2 至 3 个可自动 reset 和自动判定的 pick/place tasks 开始，先报告固定 denominator、连续视频、安全停止和人工介入次数，不直接追求大而全。
6. **第三方复现。** 用 AllenAI harness 或独立机器跑一个固定子集，发布环境镜像、commit、每 episode 记录和与本地结果的差异。

## 7. 可公开使用的表述

可以说：

- 在 840 个分层 LIBERO-Plus identity 上，adaptive Pass@2 从 fixed `261/840` 提高到 `398/840`，增加 `16.3` 个百分点；这是跨 release development result。
- RoboHermes 在持续迭代中取得 95/120 个 LIBERO short tasks 的跨 release native-success coverage。
- 在 matched five-seed Code-on/off 实验中，固化代码技能把 episode success 提高 7.5 个百分点，并降低匹配面板的 token 和 wall time。
- Strict Standard-130 在禁止 Agent-visible checker、success latch、hidden pose 和 policy checkpoint 的协议下取得 67/130 Pass@10。
- ACT 已有一个 simulator-confirmed matched success case。

不能说：

- RoboHermes 以 `95/120` 击败 OpenETA 或 RoboHarness。
- RoboHermes 的 `398/840` 与 RoboHarness 的 `93.2%` 是同协议直接排名。
- `95/120` 是最新单一 release 的常规 Pass@10。
- `398/840` 是最终固定 release 的 held-out success rate。
- ACT 已具备 held-out generalization。
- 仿真结果证明 real-world deployment readiness 或 safety。

## Sources

- [RoboHarness, memory-augmented VLA, arXiv:2603.24060](https://arxiv.org/abs/2603.24060)
- [RoboHarness, heterogeneous policy orchestration, arXiv:2607.18060](https://arxiv.org/abs/2607.18060)
- [OpenETA, arXiv:2608.03924](https://arxiv.org/abs/2608.03924)
- [OpenETA GitHub](https://github.com/OpenMOSS/OpenETA)
- [ENPIRE, arXiv:2606.19980](https://arxiv.org/abs/2606.19980)
- [ENPIRE project page](https://research.nvidia.com/labs/gear/enpire/)
- [AllenAI vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness)
- [RoboHarness 2026-03 GitHub](https://github.com/LZY-1021/RoboHarness)
- [RoboHarness 2026-07 project repository](https://github.com/markli1hoshipu/RoboHarness)
