# RoboHermes social copy

All posts should link to the public project page and use only the media shipped
in this repository. Do not crop out the simulator UI context or describe a
matched case as a benchmark aggregate.

Project page: https://nssmd.github.io/RoboHermes-LIBERO/

GitHub: https://github.com/nssmd/RoboHermes-LIBERO

## X single post, Chinese

RoboHermes LIBERO 已开源：让 GPT 组合可检查的机器人代码技能，并由仿真器决定经验能否进入下一轮。跨 release 覆盖 95/120；matched Code-on/off 为 29.0% vs 21.5%，中位 token 降低 29.4%。严格结果、视频 trace 和局限都在项目页。https://nssmd.github.io/RoboHermes-LIBERO/

## X single post, English

RoboHermes LIBERO is open: inspectable robot code skills, GPT composition, and simulator-gated evolution. Adaptive coverage reaches 95/120; matched Code-on/off is 29.0% vs 21.5% with 29.4% lower median tokens. Protocols and limits: https://nssmd.github.io/RoboHermes-LIBERO/

## X thread, Chinese

### 1/7

机器人成功一次之后，经验应该留下来。但一段“下次注意”的文字不够。RoboHermes 尝试把成功操作固化成代码技能，再用 changed-path simulator harness 决定它能不能进入下一轮。代码、配置、证据回放和项目页现已公开。

配图：`media/hero-libero-short.mp4`

### 2/7

系统有三个可见角色：Planner 做计划，Engineer 根据 RGB-D 调工具，Reviewer 看 trace 提修改。它们都拿不到 reward、object pose、`check_task` 或 success latch。只有工具循环结束后，host 才读取 native simulator verdict。

配图：项目页 Architecture section。

### 3/7

Adaptive headline 是 95/120，但必须说清楚：这是多个 release 的累计 development coverage，不是固定方法 Pass@10。可完整计量的十轮顺序实验是 32 -> 45 -> 52 -> 66 -> 71 -> 76 -> 81 -> 82 -> 82 -> 83，消耗 2.342B tokens、11.09h active wall time。

配图：Adaptive development coverage chart。

### 4/7

代码固化是否真的有用？我们做了 120 tasks × 5 seeds 的 matched Code-on/off。Code-on 成功 174/600，Code-off 129/600，差 7.5 pp；McNemar p=8.06e-5。独立 118-task 效率面板里，中位 token 从 3.65M 降到 2.58M。

配图：Code-on/off success + efficiency section。

### 5/7

另一条严格协议覆盖 130 tasks，Agent 看不到 checker、latch、hidden pose 或 policy checkpoint。结果是 67/130 Pass@10，明显低于 OpenETA 的 117/130 Pass@5。两者的多视角、horizon、timeout 和 success feedback 都不同，所以不画成同一榜单。

配图：Strict Standard-130 section。

### 6/7

ACT 目前只有一个完整 matched case：code-backed grasp -> 304-step ACT corrective transport -> code-backed placement，最后 simulator success。它证明数据飞轮能闭环，但不是 held-out generalization。项目页把 ACT 单独标为 case。

配图：`media/videos/act-corrective-transport.mp4`

### 7/7

接下来缺的东西很具体：LIBERO-Plus 扰动矩阵、adaptive holdout promotion、完整失败/token ledger、policy-as-skill ablation，以及有固定 denominator 的 real-robot panel。当前版本不宣称超过 RoboHarness 或 OpenETA，只公开已经有证据支持的部分。

项目页：https://nssmd.github.io/RoboHermes-LIBERO/

GitHub：https://github.com/nssmd/RoboHermes-LIBERO

## X thread, English

### 1/6

RoboHermes turns verified robot experience into inspectable code skills. A candidate change is isolated, tested, and run through a changed-path simulator harness before it can enter the campaign overlay. The LIBERO release is now open source.

### 2/6

Planner, Engineer, and Reviewer see RGB-D, proprioception, tools, and visible traces. They do not see reward, object poses, a task checker, or a success latch. Native task truth is read by the host after the tool loop.

### 3/6

Adaptive development coverage is 95/120 across evolving releases. The measured 10-round sequence is 32 -> 83 tasks, using 2.342B metered tokens and 11.09 active hours. The headline is cumulative coverage, not fixed-method Pass@10.

### 4/6

Matched Code-on/off uses 120 tasks and five seeds per arm: 174/600 vs 129/600 successes, +7.5 pp, McNemar p=8.06e-5. In a separate 118-task panel, median tokens fall 29.4% and median wall time falls 17.0% with solidified code.

### 5/6

The strict no-checker/no-latch Standard-130 result is 67/130 Pass@10. ACT has one matched simulator success, not held-out generalization. We keep these tracks separate from the adaptive headline.

### 6/6

The release includes one-command setup, 120-task replay, six decoded success videos with tool chains, protocol-aware RoboHarness/OpenETA context, and explicit gaps. Project: https://nssmd.github.io/RoboHermes-LIBERO/

## Video captions and alt text

### Strict moka pot to stove

Caption: RoboHermes moves the right moka pot onto the stove in `libero_90/38`, seed 9. The full trace includes failed compound attempts, posture recovery, grasp verification, placement recovery, and the final native simulator verdict.

Alt text: A four-panel LIBERO simulator view shows a Franka robot approaching two silver moka pots, lifting the right pot, moving it over a red stove burner, and releasing it onto the stove.

### Strict black bowl into tray

Caption: A strict Standard-130 success on `libero_90/60`, seed 9. The first placement misses; RoboHermes re-localizes, re-grasps, and places the black bowl inside the wooden tray.

Alt text: A LIBERO tabletop scene shows a robot grasping a black bowl among several bowls and transporting it into a rectangular wooden tray on the right.

### Strict chocolate pudding into basket

Caption: A strict Standard-130 success on `libero_object/8`, seed 7. The trace retains failed placement attempts and posture recovery before the final basket relation is accepted by the simulator.

Alt text: A Franka robot in LIBERO lifts a small chocolate pudding package from a tiled floor scene and places it into a woven basket beside several grocery items.

### Strict ketchup into basket

Caption: A 512x512 strict success on `libero_90/48`, seed 8. Visual pointing, grasp verification, basket placement, and the post-hoc simulator verdict remain separate trace steps.

Alt text: A LIBERO robot reaches toward a red-orange ketchup bottle on the floor and transports it into a square woven basket.

### Adaptive black bowl placement

Caption: An adaptive round-4 success on `libero_spatial_swap/1`, seed 14. The exact episode uses the solidified compound plus base-tool recovery before the host records simulator success.

Alt text: A tabletop LIBERO rollout shows a Franka gripper lifting an Akita black bowl and setting it on a white plate among several bowls.

### ACT corrective transport

Caption: The matched ACT seed-3 case on `libero_spatial_swap/0`: code-backed grasp, 304 ACT corrective transport steps, code-backed placement, and one native simulator success.

Alt text: A short LIBERO simulation video shows a robot carrying a black bowl across a tabletop during the ACT-controlled transport phase and completing the placement.

## Suggested publication order

1. Post the single English or Chinese announcement with the four-panel hero.
2. Publish the thread with architecture, adaptive curve, matched Code-on/off, strict result, and ACT video in that order.
3. Pin a reply containing the GitHub reproduction command and the experiment-comparison report.
4. Use “adaptive development coverage” wherever `95/120` appears.
5. Use “matched case” wherever the ACT success appears.
