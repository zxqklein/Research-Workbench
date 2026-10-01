# 第 2 周验收：执行接收，核心结果通过，交付说明追加更正

- 日期：2026-10-01（北京时间）；审查角色：网页 AI / Codex。
- 仓库：`zxqklein/Research-Workbench`，`main`。
- 固定验收提交：`b26f30002943245cd1a938f76d6c200e7a491b97`。
- 任务：`RW-W2-CHECKLIST-MEASUREMENT-v1`。
- 决定：**执行接收，核心读数 PASS；原版字段解释与引用 PARTIAL，本次追加更正后第 2 周可以收口。** 原始代码、预注册、contract 和 results_v1 全部保留。经验条目仍为候选，个人掌握仍未检验。

## 1. 核对范围与执行合同

已读取 AGENTS、周 PLAN/PREREG/RETURN、contract、run.py、verify_static.py、全量 rows/summary/manifest、两个反例、ANALYSIS、案例 004、练习与答案、PB-003 和 README。

本次从原始 rows 独立核对 16 组、128 条输入、768 个策略答案：用实际先后帧的目标存在性之差判方向，不导入原 scorer；检查组编码、实际输入、提示映射、六策略输出、固定分母，并独立重算 MFT、DIR、INV、联合正确和 AA/BB。目的为解决字段与说明冲突，不重复本地整套工程审计、不启动模型或新的合成实验。

| 检查 | 结果 |
|---|---|
| 预注册与合同 | `56bed4ba…` 在实现 `a9d952e…` 和结果 `f7d20d4…` 之前；完整父子链与提交时间一致。当前 PREREG/contract blob 与冻结提交一致。Git 记录证明提交顺序，评分前冻结的本地执行过程同时依赖执行端记录。 |
| 源码与产物身份 | run.py 与 T2 版本一致；manifest 的三项输入和两项输出 SHA-256 共 5/5 匹配。results_v1 五个文件与 T3 版本一致。 |
| 数据与读数 | 全部输入与答案符合任务书；独立计数与 summary 各关键读数一致；两份反例与原 rows 对齐。 |
| 事前预测 | P3 数值预测 80/128 不成立，实测 96/128；偏差已主动披露，冻结预测未改写。 |
| 科学边界与个人掌握 | 没有把合成诊断当作真实遥感能力或新增独立确认；无用户实际作答，未检验状态正确。 |

本地 `verify_static` 的 18 项通过与两次 byte-identical 回放为执行端回执。本次核对了相关实现及原始读数，未将其写成本次重新运行的测试成绩。字段权限的证据来自过滤后的视图与策略源码；输出不变性本身不能证明一个任意程序没有读取其他字段。

## 2. 独立确认的结果

| 策略 | R0 | R1 | MFT /128 | 换序关系 /16 | 变化行正确 /32 | 提示 INV /64 |
|---|---|---|---:|---:|---:|---:|
| ORACLE | 通过 | 通过 | 128 | 16 | 32 | 64 |
| CONST_NULL | 未通过 | 未通过 | 96 | 0 | 0 | 64 |
| CONST_APPEAR | 未通过 | 未通过 | 16 | 0 | 16 | 64 |
| SLOT_ID | 通过 | 未通过 | 80 | 16 | 16 | 32 |
| INVERT_TARGET | 通过 | 未通过 | 96 | 16 | 0 | 64 |
| DISTRACTOR | 未通过 | 未通过 | 88 | 8 | 8 | 64 |

唯一主读数为 **2/5**：SLOT_ID、INVERT_TARGET 均通过关系门槛却含错误方向输出。分母是固定五个非 ORACLE 策略，不是随机样本，也不是发生率估计。完整数据、明确区分拒绝与漏检的派生字段见 [`REVIEW_DATA.json`](REVIEW_DATA.json)。

尤其要保留：CONST_NULL 的 96/128 总正确率来自判空行较多；INVERT_TARGET 也有 96/128，但变化行 0/32。整体分数与目标能力分开陈述的做法在这里有具体反例。

## 3. 两项交付更正

**E1：`auxiliary.r1_misses` 的命名与文字解释不一致。** run.py 的 build_summary 在 `not r1.pass` 时向此列表追加策略，因此它实际保存五个被拒绝的非 ORACLE 策略，不是漏检/误放行策略。ANALYSIS §4、案例 004 主张 2 等把该字段引用为 `[]` 不符合原 JSON。

独立派生的正确集合是：`r1_rejected_non_oracle_strategies` 为五个策略；`r1_false_accepts` 为 `[]`。因此“这五个错误策略没有被 R1 放行”的窄结论成立，原字段不能作为空列表证据。原 summary 和生成代码不改写，本次以 REVIEW_DATA 给出正确解释；将来复用接口时采用清楚的字段名并另记版本，不能继续将旧键当作 false accepts。

**E2：RETURN 的仓库跨目录链接少一个 `..`。** 共 10 个失效链接出现位置、9 个不同目标。它位于 `weeks/2026-10-07/`，指向仓库根的 experiments/cases/playbook 应使用 `../../`。原回传保留，本次在其末尾追加正确入口，并在本文件提供产物导航。

上述更正不需要重训、重推理或重做 128 条枚举，也没有改变 2/5 主读数。

## 4. 设计价值与结论上限

本周产出是可重放的 **R0 反例和评分规范资产**，有明确但有限的用途。它没有提供新的真实遥感能力、参考效度、视觉机制或论文方法效果证据。

R1 包含“已知真值的 128 条输出全部正确”，因此在这个定义下，存在错误输出的策略必然不通过。这里的零误放行主要是全真值计分定义的性质，不是统计检验得到的真实模型判别力。案例 004 主张 2 中提出的“通过 R1 全部组件却方向错误”在真值、输入映射与程序正确的前提下不可能；有意义的复用检验应检查真实参考、映射和实现是否可靠，以及读数是否改变实际研究决策。

DIR/INV 可提供受控行为证据；是否纳入真实任务、如何定义阈值和分母，取决于其任务语义。当前 R1 是本有限域的诊断合同，不是所有真实实验必须 100% 正确或必须逐项采用的通用门槛。既有对象身份和参考供给问题仍未解决。

该信息上限来自本周计划的范围，不能归因于执行方没有完成任务。后续重点应是一次真实评价合同的复用反馈；无需通过扩大同类合成策略清单维持任务运行。本次不自动启动第 3 周新样本、模型调用、标注或采购。

## 5. 成本与收口

原 manifest 记录一次评分 CPU 0.012288 s、墙钟 0.012294 s。它不是实现、验证、回放与文档维护的累计成本；后者未完整计量。执行助手 token UNKNOWN 的记录正确。纯标准库脚本中无训练、GPU 或实验模型服务调用；执行端另声明无 p2 写入或真实研究数据访问，本次未另对 p2 做工程审计。

第二周按约定收口；原始结果保留，本次只新增验收与字段解释、追加文档修正入口。PB-003 不升格，用户掌握不升格。输出提交 SHA 由写回回执提供，不在本文件自引用。

## 6. 正确产物入口

- [事前注册](PREREG.md)；[执行任务书](PLAN.md)；[原始回传与追加更正](RETURN.md)。
- [合同](../../experiments/checklist_measurement_v1/contract.json)；[实现](../../experiments/checklist_measurement_v1/run.py)；[本地验证脚本](../../experiments/checklist_measurement_v1/verify_static.py)。
- [原始逐行记录](../../experiments/checklist_measurement_v1/results_v1/rows.jsonl)；[原 summary](../../experiments/checklist_measurement_v1/results_v1/summary.json)；[manifest](../../experiments/checklist_measurement_v1/results_v1/manifest.json)；[分析与更正](../../experiments/checklist_measurement_v1/ANALYSIS.md)。
- [案例 004](../../cases/004-checklist-measurement/README.md)；[PB-003](../../playbook/semantic-validity-of-controls.md)。
