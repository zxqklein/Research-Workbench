# 第 1 周回传（2026-09-30 — 10-06，北京时间）

> 本文件不含自身提交 SHA（协议约束：提交不能自引）；实际提交 SHA 见回传消息。

## 1. 本周问题与来源提交

- **本周问题**：已有实验究竟形成了哪些有条件的经验？
- **来源仓库**：`zxqklein/p2`，分支 `feat/c1-directional-delta-v1`。
- **来源分支头（本轮固定）**：`160ae515738f58bd06bd011c96ea0391c424b6c7`（与 `origin/feat/c1-directional-delta-v1` 一致）。
- **历史定位候选提交**：`05eb58becb099468691e8115eb311a610123406e`（已验证存在；三个案例文件在该提交与分支头间 `git diff --stat` 为空）。
- 来源工作区已有改动保持原状：`.serena/project.yml` 修改；未跟踪目录 `artifacts/rsicc_{evidence_conflict_20260930,primitives_week_20260930,round5_v1,round7_v1,round8_v1,round8_v1_INVALIDATED_r8_1a,week_20260929}`、`reports/rsicc_primitives_week_20260930`、`tests/rsicc_primitives_week_20260930`、`tools/{artifacts,rsicc_primitives_week_20260930}`、`.zcodeignore`。未清理、未覆盖。

## 2. 实际完成任务和新增产物

经验仓库路径：**`/data/home/ma/zxq/research-workbench`**（建仓前该目录仅含 ZCode 会话工件 `.zcodeignore`，非其他项目，故未启用备用名 `research-workbench-20260930`）。

- 建仓：`README.md`、`AGENTS.md`、`LICENSE`（MIT，暂定主体 zxqklein）、`.gitignore`；`templates/{case,lesson,practice,week-return}.md`。
- 三个案例（原件已读，含引用核对与缺口标注）：`cases/001-threshold-and-comparison/README.md`、`cases/002-metrics-and-visual-facts/README.md`、`cases/003-intervention-and-answer/README.md`。
- 三条经验条目（均**候选**）：`playbook/threshold-and-fair-comparison.md`、`playbook/metrics-and-task-evidence.md`、`playbook/semantic-validity-of-controls.md`；与案例双向链接。
- 两份外部方法迁移（含读取日期/版本、前提、最强竞争解释）：`external_methods/2026-09-30_tuning_playbook.md`、`external_methods/2026-09-30_checklist.md`。
- 练习：`practice/2026-09-30/{questions,feedback}.md`（题目与反馈分开；未作答）。
- 周文件：`weeks/2026-09-30/{PLAN,RETURN}.md`；规划入仓：`docs/superpowers/plans/2026-09-30-research-workbench-weekly-plan.md`（任务书原文）；`docs/superpowers/specs/README.md`（设计文件缺口记录）；`docs/PUBLISHING.md`（发布阻塞说明）。

## 3. 关键证据与来源（≤3 项）

1. **案例 001（R2 回传）**：`reports/rsicc_round2_v1/round2_return.md` @`05eb58be…`——换工作点自身 BA +6.82pp [+0.0270,+0.1088]，对冻结基线 N −2.14pp [−0.0599,+0.0171] 跨零；主策略 D1 内容层净损伤且不优于等量控制；随机对照必须闭式期望（主种子窗口 z=−3.23）。冻结文件 `operating_point_freeze.json`（`frozen_before_any_vdev_look: true`）已抽查。
2. **案例 002（R8-D1 决定）**：`docs/decisions/2026-09-25_R8_D1.md` @`05eb58be…`，证据提交 `dfab9e63…`——P−S CIDEr +0.0769 [0.0521,0.1022]（`reports/rsicc_round8_v1/eval/TEXT_READING.json` 已抽查验算一致）；120 对盲视卡 1 例方向事件 → 方向不可识别；机制四类竞争解释未决。注意：决定中 `eval/…`、`data/…` 为简写，实际路径在 `reports/rsicc_round8_v1/` 下（案例文件已说明）。
3. **案例 003（X1-48H V3/V4 决定）**：两决定 @`05eb58be…`，证据提交 `225ab19e…`/`16063c14…`——AB−BB 主差值 +33.33pp（未加权）由 BB 忠实判空驱动（干预改变正确答案而原目标表未跟着改）；AB 33.33% 未超 SINGLE_B 35.90%；anchor 类别构成 34 APPEAR/5 DISAPPEAR（本项目解析 `FROZEN_ANCHORS.json` @`225ab19e…` 独立核对一致）→ 恒答基线 87.18%，"高于抛硬币"失效。

## 4. 结论、竞争解释和限制

- **结论（有条件）**：三个候选案例均已处理且有处理记录；它们共同支持的**有条件经验**是：在开发集合上，"自身改善"与"相对优势"必须分开归因（001）；指标增益与任务能力、机制解释必须分层（002）；干预型对照必须先固定干预后的正确答案关系与参考分布基线（003）。
- **竞争解释保留**：001——种子依赖（D2/D3 正、主种子 G1 负）与"候选内容本身是主要限制"并行成立；002——文本增益的来源（可核实事件内容/拍摄渲染差异/来源标注规律/组合）四类全部未决；003——图像线索、时相身份提示、对象/答案先验、真实两帧比较未分离。
- **限制**：全部结论限于对应原件的开发集合、既定尺度与 checkpoint；视觉读数无跨模型独立通道；三条经验均来自单案例，**不得**当作已验证方法外推。

## 5. 可复用经验及其证据程度

| 条目 | 状态 | 证据程度 |
|---|---|---|
| [阈值与公平比较](../../playbook/threshold-and-fair-comparison.md) | 候选 | 单案例（R2），关键统计点经来源主控复现 |
| [指标与任务证据](../../playbook/metrics-and-task-evidence.md) | 候选 | 单案例（R8-D1），数字经本项目抽查一致 |
| [控制的语义效度](../../playbook/semantic-validity-of-controls.md) | 候选 | 单案例（X1-48H），类别构成经本项目独立核对 |

README 的"已支持经验索引"按规则**保持为空**，直至第 3 周独立确认或复用。

## 6. 作者真实预测、作答和掌握状态

- 作者未参与本轮历史案例的作答；本仓库**未补写任何用户事前预测**（案例中"显式数值预测"均为"未找到"，并写明检索范围）。
- 练习 `practice/2026-09-30/`：题目已交付，**未作答／未检验**；反馈要点已先行固定并与题目分开存放，作者作答前不得阅读。
- 个人掌握程度与案例证据程度分开报告：本周个人掌握结论 = **未检验**。

## 7. 实际 CPU/GPU 消耗与维护时间

- GPU：**0**（未运行任何训练/推理）。
- CPU：仅文件读取、git 对象核对与一次 JSON 解析计数（<0.05 core-hour 量级）；未复算任何读数（三个案例抽查均与原件一致，未触发"读数冲突"复算条件）。
- 网络读取：Tuning Playbook（raw README + GitHub API）、CheckList（ACL Anthology 页 + ar5iv 全文）。
- Token 用量：UNKNOWN（执行环境未提供会话级精确用量面板）；维护时间：单会话（2026-09-30）内完成。

## 8. 下周候选、排序和推荐

按任务书 §3 规则（默认优先**评估/公平比较做法**；排序键：当前决策影响 > 可识别性 > 少量交互可完成 > 成本），只推荐一个：

| 排序 | 候选 | 内容 | 关键读数 | 成本 | 排序理由 |
|---|---|---|---|---|---|
| **1（推荐）** | **CheckList 型方向预期测试**（新 dev 组、冻结 checkpoint、推理-only） | 对未进入 P60 60 组的新 dev 组构建小型 DIR/INV 测试集：换序→方向翻转、同图→判空、错配→不进方向读数；分类别×顺序分解，同表报告恒答基线与弃答率（骨架见 `external_methods/2026-09-30_checklist.md`；PLAN 内嵌 Tuning Playbook 变量契约章节） | 方向一致率、判空正确率（按预期关系可核对的子集） | 推理前向，先小试吞吐再固定样本量；无训练 | 直接作用于当前真实问题（方向机制不可识别）；读数可识别（预期关系预先定义）；对论文方向问题有决策影响 |
| 2 | 闭式对照复核（PB-001 检验点） | 新种子集上并行计算闭式期望与经验均值对照 | 两对照差值的种子依赖 | CPU 级模拟 | 可识别、极低成本，但决策影响低于 1（旧路由策略已收口） |
| 3 | 来源可证性前置检查 | 为候选 1 预先核对拟用 dev 组的配准/标签可用性 | 可用组数、失败清单 | CPU | 不是独立实验，是候选 1 的前置依赖 |

**不合格候选记录**：直接在 P60 已用 60 组上重算——**不合格**，违反探索污染边界（已用于筛选的信息不得充当确认依据）；扩大同质盲视面板——不合格，来源决定 §2 已判边际信息有限。

## 9. 未完成事项和具体原因

1. **配套设计文件缺失**：`2026-09-30-research-workbench-design.md` 未随交接提供，本地与附件目录检索未获；已记缺口（`docs/superpowers/specs/README.md`），第 1 周按任务书 §1 复述的边界执行。**影响**：设计级 review 无法进行，连带发布阻塞。
2. **发布阻塞**：无远端仓库/发布凭据；设计 review 与用户开源意图确认未完成。按任务书条款保留完整本地提交与发布说明（`docs/PUBLISHING.md`），其他交付照常；本地提交**不**表述为已公开上线。
   - **交付后更新（2026-09-30）**：用户随即明确指令推送至 `zxqklein/Research-Workbench`，阻塞解除——`main` 已推送，首发提交 `a0c8d0e923beba38767f016bc9452cbe40041573`；设计文件缺失与 review 未做仍是遗留事项，见 `docs/PUBLISHING.md` 遗留清单。
3. **练习未作答**：作者截至交付未作答；掌握程度保持"未检验"，不阻塞客观整理（任务书允许）。
4. **执行技能缺失**：`superpowers:executing-plans` 在当前环境不可用；按任务书逐任务手动执行，已记录于 AGENTS.md。
5. **核对深度限制（非缺口）**：案例 002 的视觉引用文件、案例 001 的 02_routing 产物为 ls-tree/目录级核对，未逐字段读取；来源侧工程回执按协议复用，未重复审计。
