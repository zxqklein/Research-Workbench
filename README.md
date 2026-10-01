# Research Workbench

把一个真实研究项目（来源：`zxqklein/p2`，分支 `feat/c1-directional-delta-v1`）的历史实验整理成**可追溯的经验仓库**：每个案例只下其证据能支持的结论，每条可迁移经验标明证据程度，个人掌握程度与案例证据分开记录。

四周试运行安排（2026-09-30 至 2026-10-27）见 `docs/superpowers/plans/2026-09-30-research-workbench-weekly-plan.md`。

## 当前执行状态（2026-09-30 验收后）

第 1 周经验整理已验收；三条经验仍为候选，个人掌握仍未检验。验收入口：[weeks/2026-09-30/REVIEW.md](weeks/2026-09-30/REVIEW.md)。

第 2 周任务：[weeks/2026-10-07/PLAN.md](weeks/2026-10-07/PLAN.md)，CheckList 评分合同反例诊断，**已于 2026-10-01 执行完毕**（PREREG/合同冻结于运行前，结果见 `experiments/checklist_measurement_v1/`，回传见第 2 周 RETURN）。主读数：5 个非 ORACLE 策略中 2 个通过关系门槛 R0 却未通过完整合同 R1（SLOT_ID、INVERT_TARGET）；新增训练、GPU 与模型调用均为 0，CPU ≤2 core-hours。

后续计划、回传与修正以本仓库为交互入口。下方第一周索引和原回传保留为历史；当前投入范围以新的周任务书为准。

## 阅读入口

1. 最新周回传：[`weeks/2026-10-07/RETURN.md`](weeks/2026-10-07/RETURN.md)
2. 案例目录：`cases/00*/README.md`（原件定位、核对的主张、缺口）
3. 经验条目：`playbook/*.md`（每条标注 候选／已支持／被修正）
4. 外部方法迁移：`external_methods/*.md`
5. 个人练习：`practice/<日期>/{questions,feedback}.md`

## 当前索引（2026-10-01，第 2 周后更新；第 1 周行保留为历史）

| 类型 | 条目 | 状态 |
|---|---|---|
| 案例 | [001 阈值与比较](cases/001-threshold-and-comparison/README.md) | 已核对（原件已读，缺口已标注） |
| 案例 | [002 指标与事实](cases/002-metrics-and-visual-facts/README.md) | 已核对（原件已读，缺口已标注） |
| 案例 | [003 干预与答案](cases/003-intervention-and-answer/README.md) | 已核对（原件已读，缺口已标注） |
| 案例 | [004 CheckList 评分合同反例诊断](cases/004-checklist-measurement/README.md) | 本周原创实验（冻结合同＋结果＋程序验证，逻辑反例非真实任务证据） |
| 经验 | [阈值与公平比较](playbook/threshold-and-fair-comparison.md) | **候选**（单案例支持） |
| 经验 | [指标与任务证据](playbook/metrics-and-task-evidence.md) | **候选**（单案例支持） |
| 经验 | [控制的语义效度](playbook/semantic-validity-of-controls.md) | **候选**（2026-10-01 增加合成域使用记录） |
| 外部方法 | [Deep Learning Tuning Playbook](external_methods/2026-09-30_tuning_playbook.md) | 已读，迁移前提成文 |
| 外部方法 | [CheckList](external_methods/2026-09-30_checklist.md) | 已读，迁移前提成文；第 2 周已做有限域实例化 |
| 练习 | [2026-09-30](practice/2026-09-30/questions.md) | 题目已出，**未作答／未检验** |
| 练习 | [判例题 004](cases/004-checklist-measurement/quiz.md) | 题目已出（附分开存放的答案卷），**未作答／未检验** |

**已支持经验索引：目前为空。** 三条经验条目各自只来自一个历史案例，属于候选，须在第 3 周独立确认或复用后才可升格。

## 证据可达性

- 本仓库**不保存**来源项目的实验产物；只保存指向版本化原件的引用（仓库相对路径 + 固定 40 位提交 SHA）与少量为说明判断而逐字摘录的读数。
- 来源仓库本地路径：`/data/home/ma/zxq/p2`（只读）。远端 `zxqklein/p2`，分支 `feat/c1-directional-delta-v1`。
- 第 1 周固定提交：来源分支头 `160ae515738f58bd06bd011c96ea0391c424b6c7`；历史定位候选提交 `05eb58becb099468691e8115eb311a610123406e`（已验证存在；三个案例文件在该提交与分支头之间无差异）。
- 各案例证据提交：001→`05eb58be…`；002→决定文件所在提交 `05eb58be…`，其审查证据提交 `dfab9e63beaf3d5a1c5560691d8fec3721ed07b9`；003→决定文件所在提交 `05eb58be…`，V3 审查证据 `225ab19e7b6cd0af15618f379dbd515671d9a23a`，V4 审查证据 `16063c14636b8c7eb6044d8cc950eeabf48789dd`。
- 引用路径一律为来源仓库相对路径；本仓库标注的实际检出路径若与来源文档中的简写不同，以本仓库核对记录为准（见案例 002 的路径差异说明）。

## 个人掌握的记录方式

- 每次练习一个目录 `practice/<日期>/`：`questions.md`（题目）与 `feedback.md`（反馈要点＋作答状态）**分开存放**，作者先独立作答再看反馈。
- 作答只能来自用户真实输入；未作答时 feedback 记"未作答／未检验"，不代写。
- 掌握状态与案例证据程度**分别报告**：案例的证据分级不因任何人答对题目而升级，练习作答也不作为案例结论的证据。

## 边界与修正

- 全局边界见 [`AGENTS.md`](AGENTS.md)：来源仓库只读、不访问锁定 test、不重开冻结阶段、按周预算执行。
- 修正一律追加记录（案例与条目内的"修正历史"小节），不改写已交付内容。
- 本仓库原创内容采用 MIT 许可（`LICENSE`，版权主体为暂定的仓库账号，发布前可调整）；上游材料保留其来源与许可，不整体复制后改署名。发布前置检查见 [`docs/PUBLISHING.md`](docs/PUBLISHING.md)。

## 证据与许可补充（2026-09-30）

已通过 GitHub 仓库元数据确认：本仓库公开，来源 zxqklein/p2 **为私有仓库**。案例中的路径与 SHA 是内部版本定位，外部读者目前不能直接获取这些原件；不将这些案例标为已公开独立复现。后续第二周生成器与有限域结果在本仓库交付时，可按其自身版本重放，但不能替代私有来源的真实任务证据。

原设计已补齐：[docs/superpowers/specs/2026-09-30-research-workbench-design.md](docs/superpowers/specs/2026-09-30-research-workbench-design.md)。当前发布遗留项处置见 [docs/PUBLISHING.md](docs/PUBLISHING.md) 的收口记录；上游署名、来源与许可见 [docs/SOURCES_AND_LICENSES.md](docs/SOURCES_AND_LICENSES.md)。


## 第 2 周验收状态（2026-10-01）

[验收决定](weeks/2026-10-07/REVIEW.md)：执行接收、核心读数通过；[派生核对与字段解释](weeks/2026-10-07/REVIEW_DATA.json) 确认两个 R0 伪通过反例。原回传与案例中 r1_misses 的误引用及 RETURN 的相对链接以追加说明更正，原始代码与 results_v1 保留。

第二周可以收口。产出为评分规范与逻辑反例，未形成新的真实遥感实验结论；经验条目保持候选，个人掌握保持未检验。第三周新样本、模型调用或采购不由本次验收自动启动。


## 第 3 周任务入口（2026-10-01 下达，可提前执行）

[第 3 周 PLAN](weeks/2026-10-14/PLAN.md) 与[可直接转发的启动指令](weeks/2026-10-14/KICKOFF.md)：`RW-W3-REAL-CACHE-REUSE-v1`，在已验收的真实 C_local 类别预测缓存上复用“关系与正确性分列”的做法。当前为 **PLANNED / NOT_EXECUTED**；回顾性的新条件复用，独立数据确认尚未完成。

本周交付窄评分工具、聚合诊断及实际使用记录；CPU 上限 4 core-hours，新增 GPU、训练与实验模型调用为 0。p2 的新 primitives 实验按其原任务书独立执行，本经验任务不复制其队列或借用预算。个人练习缺席时，掌握状态继续保持未检验。

