# 机器人成功一次之后，能不能把经验留下来？RoboHermes 选择把它写成代码

## 导语

过去一个月，机器人 Agent 方向一下子热闹起来。OpenETA 让 Codex 通过少量几何工具直接操作 LIBERO；RoboHarness 把 VLA、RL policy 和 TAMP 组织成可切换的能力；ENPIRE 则把 coding agent 放进真实机器人训练循环，让它自己改算法、跑实验、看结果。

RoboHermes 走的是另一条路线：机器人完成任务后，不只把过程记成一段文本，而是尝试把反复有效的操作固化为可检查的代码技能。新代码不能直接进入系统。它要先经过静态隔离、测试和 changed-path simulator harness，只有 native simulator verdict 为成功，才会进入当前 campaign 的 skill overlay。

项目现已开源 LIBERO short runtime、配置、技能、评测协议和精简证据包：

- GitHub: https://github.com/nssmd/RoboHermes-LIBERO
- Project page: https://nssmd.github.io/RoboHermes-LIBERO/

## 三个角色，一条物理执行边界

RoboHermes 把一次任务拆成三个可见角色。Planner 根据指令和技能目录提出计划；Engineer 读取 RGB-D 观测并组合工具；Reviewer 查看同一条可见 trace，诊断失败并提出修改。

这三个角色都拿不到 simulator predicate、reward、object pose 或 success latch。它们只能看到相机、机器人 proprioception 和已注册工具的返回。等工具循环结束后，host 才调用一次 simulator predicate，把最终结果写入 append-only journal。

这个限制会让数字变低，却让结果更容易解释。一个动作函数返回 `ok`，只说明动作执行完了；夹爪看起来抓住物体，只说明当前证据支持继续；只有最后的 simulator verdict 才算任务成功。

## 从 32 个任务到 95 个任务

RoboHermes 的 headline 是 Adaptive task-level Pass@10 `95/120`，其中 Spatial 为 `9/10`、Object 为 `10/10`、Goal 为 `9/10`、LIBERO-90 为 `67/90`。

这不是一个固定模型在十个 seed 上跑出来的常规 Pass@10。它是多个 release 持续开发后的跨版本累计覆盖：系统在 95 个不同任务上至少取得过一次 native success。公开 evidence bundle 为每个成功任务保留一条 canonical row，可以重算这 95 个任务，但不能拿来统计整个 campaign 的总成本。

真正按顺序记录的十轮 adaptive campaign 从 `32/120` 开始，曲线依次为 `32, 45, 52, 66, 71, 76, 81, 82, 82, 83`。这十轮消耗 `2.342B` metered tokens，active round wall time 为 `11.09` 小时。后续 residual releases 又补上 12 个不同任务，因此最终 headline 到了 95，而不是把新结果硬接到原来的十轮曲线上。

## 代码固化有没有用？1200 个 episode 做了一次配对实验

自进化项目最容易被质疑的一点是：分数上涨究竟来自新代码，还是来自多试了几次。

RoboHermes 为此做了 Code-on/off 实验。两组使用同一个 release、GPT-5.6 Sol、medium reasoning、相同的 120 个任务、5 个 seed 和 tool budget。Code-off 只能逐步调用 base tools；Code-on 额外获得一个由先前成功轨迹固化并通过 canary 的 `visual_pick_place` compound。

结果是 Code-on 成功 `174/600`，Code-off 成功 `129/600`，相差 45 个 episode，也就是 `+7.5` 个百分点。配对 McNemar 检验为 `p=8.06e-5`，按 task cluster bootstrap 得到的 95% 区间是 `+3.7` 到 `+11.5` 个百分点。任务级 Pass@5 则是 `71/120` 对 `58/120`。

另一个 118-task matched panel 只看效率。Code-on 的中位 token 从 `3.65M` 降到 `2.58M`，减少 `29.4%`；中位 VLM calls 从 `40.5` 降到 `29.5`；中位 wall time 从 `845s` 降到 `701s`。这组结果支持一个具体机制：已经固化的复合技能减少了重复观察、定位和规划，不只是换了一种提示词。

## 为什么严格分数只有 67/130

RoboHermes 还跑了一条 Strict Standard-130 track。130 个任务各有最多十个 ordered seeds，成功任务不重跑，基础设施记录与任务失败分开。最终 task-level Pass@10 为 `67/130`，共 `846` 个有效 task-seed verdicts、`2.882B` tokens、`43,076` 次 VLM calls，campaign wall time `20.13h`。

这个数字明显低于 OpenETA for Codex 报告的 `117/130 Pass@5`。差距不能回避，也不能简单归因于模型。OpenETA 使用 512×512 multi-view 和 orthographic views、5000-step horizon、最长 5400 秒，并允许 Agent 调用 native `check_task`，Gateway 会锁存 terminal success。RoboHermes strict 禁止 checker 和 latch 对 Agent 可见，控制和视觉能力也更弱。

所以 `67/130` 和 `117/130` 不是同一个 protocol 的榜单结果。它仍然暴露了 RoboHermes 的实际短板：LIBERO-10 是 `0/10`，剩余失败集中在 perception、grasp、placement 和 JOINT_POSITION motion recovery。

## ACT 已经走通，但只有一个 case

项目还完成了一个 ACT hybrid case：在 `libero_spatial_swap/0 seed3` 上，code-backed grasp 取得物体，ACT 执行 304 个 corrective transport steps，最后由 code-backed placement 完成任务，native simulator verdict 为成功。

这个 case 说明成功轨迹可以进入“采集、训练、再执行”的数据飞轮。它只有一次 matched success，不是 held-out，也不能写成 ACT 的总体成功率。项目页把它单列为 case，而没有混进主指标。

## 和 RoboHarness 相比，优势和缺口都很具体

2026 年 7 月的 RoboHarness 在 original LIBERO 报告 `98.7%`，LIBERO-Plus 平均 `93.2%`，LIBERO-LoHo success `95.2%`，并做了 500 个 custom simulations 和 135 个 real-robot trials。它拥有 RoboHermes 目前没有的三样东西：异构 policy routing、Memory Bridge handoff 和正式 real-robot denominator。

RoboHermes 当前更强的是另一组证据。代码技能、三角色 runtime 和 evolution gate 已经公开；strict track 明确隔离 hidden ground truth；Code-on/off 有 1200 个有效 episode 的配对统计；token、VLM calls 和 wall time 都按匹配面板计量。

下一步最值得补的不是继续在同一任务上刷 seed，而是对齐 LIBERO-Plus 扰动、建立 adaptive train/holdout promotion protocol、公开完整失败与 token ledger，并加入 policy-as-skill 和真实机器人小规模固定面板。

## 开源内容

仓库提供：

- 一条命令完成 core setup 和 evidence replay；
- GPT Responses `gpt-5.6-sol`、medium reasoning 的统一 YAML 配置；
- 35 个 LIBERO base tools 和一个公开 compound skill；
- adaptive 与 fixed 两种 campaign 入口；
- 95-task compact evidence bundle；
- 6 个可解码成功视频，每个视频附工具调用链；
- 120-task dashboard、实验矩阵和竞品协议对比。

最短复现路径：

```bash
git clone https://github.com/nssmd/RoboHermes-LIBERO.git
cd RoboHermes-LIBERO
./setup.sh --core-only
./robohermes results replay \
  --manifest evidence/adaptive-pass10-v1/manifest.json
./robohermes dashboard --no-browser
```

## 可引用数字

| 结论 | 数值 | 必须附带的边界 |
|---|---:|---|
| Adaptive development coverage | `95/120` | 跨 release，不是 fixed-method Pass@10 |
| Sequential adaptive campaign | `32/120 -> 83/120` | 十轮 evolving-release experiment |
| Strict Standard-130 | `67/130 Pass@10` | Agent 看不到 checker、latch、hidden pose 或 policy checkpoint |
| Matched Code-on/off | `29.0% vs 21.5%` | 每组 600 episodes，5 个 matched seeds |
| Median token efficiency | `2.58M vs 3.65M` | 独立 118-task matched panel |
| ACT | `1/1` matched success | 单 case，不是 held-out generalization |

完整协议和竞品来源见 [docs/EXPERIMENTS_AND_COMPARISON.md](docs/EXPERIMENTS_AND_COMPARISON.md)。
