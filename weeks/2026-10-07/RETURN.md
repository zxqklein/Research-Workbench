# 第 2 周回传（2026-10-07—10-13；实际于 2026-10-01 提前完成）

- 任务 ID：`RW-W2-CHECKLIST-MEASUREMENT-v1`（[任务书](PLAN.md)）
- 完成状态：**T1–T5 全部完成；无未完成事项。** 本回传自身提交的 SHA 由推送回执报告，不写入本文件（避免自引用）。

1. **本周问题与来源提交**：只检查"换序翻转＋同图判空"的关系门槛（R0）能否误接收不具备正确目标方向判断的策略；加入逐条件正确目标与提示不变性后（R1），能否在这个有限任务域中识别这些失败。执行输入：本仓库 `main` @ `5a4a7dd06d37e129f7f866c485b487205090f89a`（任务书所在交接提交，本地 `--ff-only` 同步，无既有改动）。不涉及 p2 的图像、标签、权重或预测，p2 只读未写。

2. **实际完成任务和新增产物**（提交链按时间序）：
   - T1 冻结（`56bed4ba9a7186fc3392a695358a5d41f806902c`）：[PREREG.md](PREREG.md)（主问题、AI 预测 P1–P6、枚举规则、人工真值表、六策略字段权限、两合同与分母、成本与停止条件）＋ [contract.json](../experiments/checklist_measurement_v1/contract.json) v1.0.0，**先于任何评分运行提交**。
   - T2 实现（`a9d952e15fe55502412de58d20e430a967838315`）：[run.py](../experiments/checklist_measurement_v1/run.py)（纯标准库、无随机；128 条确定性枚举、六策略仅读权限过滤后的视图、R0/R1 计分、分母对合同校验、ORACLE 自检不过即中止不写结果、拒绝覆盖已有结果目录、manifest 含 SHA-256/预注册提交/环境/资源）；[verify_static.py](../experiments/checklist_measurement_v1/verify_static.py)（人工真值表与标记映射独立比对、键唯一、权限行为学、联合正确性独立重算、桩策略分母测试）。
   - T3 结果（`f7d20d4b6857b8cd1d748d837913a1b648af40b8`）：[results_v1/](../experiments/checklist_measurement_v1/results_v1/)（rows.jsonl 128 行、summary.json、manifest.json、counterexamples/ 两个反例）＋ [ANALYSIS.md](../experiments/checklist_measurement_v1/ANALYSIS.md)。
   - T4 反馈（`1433e44cbb363deaefb63a0c5c244cb29a808014`）：[案例 004](../cases/004-checklist-measurement/README.md)、[判例题](../cases/004-checklist-measurement/quiz.md)与分开存放的[答案卷](../cases/004-checklist-measurement/quiz_answer_key.md)、PB-003 使用记录、README 索引更新。
   - T5：本回传＋README 阅读入口更新（提交 SHA 见推送回执）。

3. **三项以内关键证据与来源**：
   - **唯一主读数：5 个非 ORACLE 策略中 2 个通过 R0 却未通过 R1（SLOT_ID、INVERT_TARGET）。** 来源：`experiments/checklist_measurement_v1/results_v1/summary.json` @T3 提交；反例全量输入/输出：`results_v1/counterexamples/{SLOT_ID,INVERT_TARGET}.json`。
   - 六策略完整仪表表（分母全部固定）：R0 通过者仅 ORACLE/SLOT_ID/INVERT_TARGET；R1 通过者仅 ORACLE；R1 漏检清单为空。来源：summary.json＋[ANALYSIS.md](../experiments/checklist_measurement_v1/ANALYSIS.md) §2–§4。
   - 程序验证：verify_static 18/18 通过；两次独立运行 rows.jsonl 与 summary.json 逐字节一致；真实运行中 UNKNOWN/缺失/非法为 0，其分母保护由桩策略测试单独验证（全 UNKNOWN 策略仍占满 128/16/64 分母并失败）。

4. **结论、竞争解释和限制**：
   - 支持的窄结论：**(a)** "换序翻转＋同图判空"不足以认证正确方向判断——两个可重放的构造性反例存在；**(b)** 完整合同在本有限域捕获全部 5 个错误策略（逐条件 MFT 捕获方向互换与错对象绑定，INV 捕获标记依赖，AA/BB 判空捕获恒报方向）；**(c)** INV 不是 MFT 的替代（INVERT_TARGET 的 INV 64/64 满分但方向全错）。
   - 事前预测对账：P1/P2/P4/P5/P6 证实；**P3 数字细节证伪**（预测 INVERT_TARGET MFT 80/128，实际 96/128；定性部分一致），已注册文本未改动，偏差记录于 ANALYSIS §5。
   - 竞争解释与限制：R1 零漏检可能是策略清单小且解析可分析的结果，非策略空间抽样；策略为全函数，真实弃答/UNKNOWN 路径只经桩测试；合成域真值由生成规则给出，不涉及真实遥感对象身份/尺度/参考效度。本结果是**逻辑反例＋程序验证**，不是真实任务证据；不能认证 p2 checkpoint、遥感视觉准确率或机制，也不估计真实模型中捷径发生率。

5. **可复用经验及其证据程度**：[PB-003 控制的语义效度](../playbook/semantic-validity-of-controls.md)新增使用记录——"预期答案关系表可冻结为可执行合同；仅按关系接收会放过可构造反例"这一方法论窄主张在合成域获得程序化演示；**条目维持候选**，未升格（AGENTS：合成诊断不升格真实任务经验）。对后续真实方向实验的设计含义已写入使用记录：关系测试只能当必要行为证据，接收判据须含逐条件正确目标分＋版本不变性＋全量记账（R1 型合同）＋恒答基线。

6. **作者真实预测、作答和掌握状态**：用户本次未提供预测；判例题 004（PHASE_CONFUSER）已出题、答案卷分开存放，**无真实作答，个人掌握维持未检验**，不影响客观实验。

7. **实际 CPU/GPU 消耗与维护时间**：评分运行墙钟 0.0123 s、CPU 0.0123 s ≈ 3.4e-6 core-hours（远低于 2 core-hours 上限；来源：run.py 内 time.perf_counter/process_time，见 results_v1/manifest.json）；新增训练 0、GPU 0、模型/VLM/judge/API 调用 0、付费 0、下载 0。执行助手 token **UNKNOWN**（不可观测，不填 0）。整理与实现墙钟未精确计量，执行会话于 2026-10-01 单日内完成（执行端估计 <2 小时）。

8. **下周候选、排序和推荐**：推荐——(1) **真实读数合同复用**：若 p2 侧当时有已授权的推理-only 任务，用 R1 型合同（逐条件正确目标＋提示不变性＋AA/BB 判空分列＋全量记账＋恒答基线）作为其评分合同的最低要求模板，先在极小样本上测"预期关系可核对"的通过率（PB-003 的第一次真实使用）；(2) 备选——把本周合同的弃答/UNKNOWN 路径在真实模型输出上做记账演练（无新训练）。两者均需回传后由用户/当周任务书裁决预算与样本，不自动搭车，不提前承诺"独立确认"。

9. **未完成事项和具体原因**：无。判例题未作答属个人练习状态，不是实验未完成项。

## 网页验收与更正入口（2026-10-01）

本回传按 b26f30002943245cd1a938f76d6c200e7a491b97 验收：执行接收，2/5 主读数通过；原版字段解释与相对链接有更正，详见 [REVIEW.md](REVIEW.md) 与 [REVIEW_DATA.json](REVIEW_DATA.json)。

- 原文引用的 r1_misses 并非空列表，实际是五个被拒绝策略；真正的 R1 错误策略误放行集合为空，派生字段已在 REVIEW_DATA 中分开提供。原始结果、代码与事前预测不改写。
- 原文跨目录链接少一级父目录。正确入口：[合同](../../experiments/checklist_measurement_v1/contract.json)、[实现](../../experiments/checklist_measurement_v1/run.py)、[验证脚本](../../experiments/checklist_measurement_v1/verify_static.py)、[结果目录](../../experiments/checklist_measurement_v1/results_v1/)、[分析](../../experiments/checklist_measurement_v1/ANALYSIS.md)、[案例 004](../../cases/004-checklist-measurement/README.md)、[判例题](../../cases/004-checklist-measurement/quiz.md)、[答案卷](../../cases/004-checklist-measurement/quiz_answer_key.md)、[PB-003](../../playbook/semantic-validity-of-controls.md)。
- 0.0123 s 是一次评分的 CPU 计时，不是全周累计耗时；真实遥感科研结论与个人掌握均没有因本次诊断升级。第二周收口，第三周新实验未由本次验收自动启动。

