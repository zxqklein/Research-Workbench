# 案例 005 证据（EVIDENCE）

## 证据类型与分级

本次交付的证据类型是**真实历史模型输出上的程序验证**，介于第 2 周的"合成逻辑反例"与未来"真实任务新实验"之间：

| 项 | 分级 | 说明 |
|---|---|---|
| 图像类别预测（pA,pB） | **真实历史输出** | 2026-09-30 EC report_a 原始 run 的 C_local 臂，Qwen 真实推理产物，封存于 CACHE_SEAL 且带 prompt/raw SHA-256；本周零推理，只读取 |
| 参考类别 (gA,gB) | **来源相对参考，非独立 gold** | 官方语义点标签经冻结目标构造（units_snapshot）；未独立认定为实例/事件 gold；位置给定、变化存在性由参考选择决定 |
| 派生行 AB/BA/AA/BB | **机械构造（DERIVED_FROM_SINGLE_SIDE_CACHE）** | 每目标 4 行由同一单侧缓存重排而来；不增加独立样本；关系成立仅认证组合实现 |
| 主读数 K=36/116 | **本固定缓存的诊断频数** | 真实输出上的可重放计数；不是模型策略误放行率、不是发生率估计、不是独立确认 |
| 映射校核 | **对已验收读数的精确复现** | 单侧 110/232 与类别对父组件等权 0.1746031746031746 逐位复现（作为中止条件内置） |

## 核对链（全部在 run.py 中程序化执行，任一失败即中止不写结果）

1. **输入身份**：8 个输入文件经 `git show 9dcd77cc…:<path>` 提取，SHA-256 与冻结合同及 p2 `RESULT_MANIFEST.json` 回执**双重**比对一致（execution_log 逐文件记录）。
2. **三方吻合**：126/126 个 `cid|C_local|side` cell 唯一存在、status=ok；`raw_sha = SHA256(raw_output UTF-8)` 与 seal 一致；`prompt_sha` 与 seal 一致；按合同解析规则重解析的标签与 seal `C_local[rid][side]` 一致；0 个未消解 cell。
3. **单位完整**：63 组件（分片 21/21/21）、116 目标（R1×63+R2×53）、全部 gA≠gB；R2 从不被 R1 代替（逐 rid 独立解析；R1/R2 标签不同的 cell 实际存在并被分别计分）。
4. **映射校核**：单侧 110/232、类别对等权 0.1746031746031746 精确复现，与 EC 独立验收已发布读数一致。
5. **实现回归**：`verify_fixtures.py` 9 组人工 fixtures（明确标 artificial，不进真实 K）全部通过：合法不同类但错误、双类准确倒置、错误同类、UNKNOWN/缺失计 0 不缩分母、R2 不被 R1 代替、逐 rid 解析含尾随句点规则、多目标父组件等权与微平均区分、五桶互斥+和守恒、AA/BB=对应单侧正确性。
6. **确定性**：同输入重放公开输出逐字节一致（summary.json、counterexamples.md cmp 通过）。

## 失败尝试披露（不隐藏）

- 正式运行前有 1 次失败尝试（attempt 1）：summary 构建阶段 KeyError（consistency 字典键名不一致），**公开输出目录未写入任何文件**，local_only 日志与派生表保留于 `experiments/real_cache_relation_v1/local_only/run_v1_failed_attempt1/`（git 忽略）。修复后正式运行一次成功。
- 第 2 周 REVIEW 对字段命名（E1）的教训已吸收：本次公开 summary 的键名与文字说明逐一对应（`pair_correct`、`relation_pass_but_wrong`、五桶名）。

## 固定指针

| 项 | 值 |
|---|---|
| 冻结合同提交 | `688d2f6d456ae83f9435effa46a8bb474ae9078f`（早于新增统计计算） |
| 交付提交 | 见 `weeks/2026-10-14/RETURN.md`（提交后回执，不在本文件自引用） |
| 来源历史数据提交 | `zxqklein/p2` @ `9dcd77cc174117551f22b8b694feec00ac985292` |
| 来源现行解释提交 | `a0ddc50c2194bf74d60c9faf6d8a706d17b1440b` |
| 输入文件 SHA-256 | `experiments/real_cache_relation_v1/results_v1/manifest.json`（8 项，与 p2 RESULT_MANIFEST 回执一致） |
| 工具文件哈希 | manifest.json `tool_sha256`（run.py 文件级 SHA-256） |
| 重放命令 | manifest.json `replay_command`（路径以 `<path-to-p2-checkout>` 占位）；实际机器路径仅在 git 忽略的 local manifest |

## 结论边界（照任务书 §3.3 与 PREREG §7）

- REUSE_OBSERVED_IN_SCOPE 支持的窄主张：**在本冻结真实缓存中，存在关系成立（合法变化形态）而两侧类别错误的目标（K=36/116），因此关系满足与类别正确需要分列评价**。
- 不支持/不认证：真实方向机制、对象绑定、事件 gold、地理泛化（GROUPING_UNKNOWN 保留）、任何新方法性能；第 2 周 R1 的"全真值 100% 正确"不搬作真实模型接收条件；作为回顾性复用**不记为独立确认**。
- 公开范围：完整原始账本、图像、逐目标预测、参考标签表与机器绝对路径均在私有 p2 或 git 忽略的 local_only 中；公开文件仅含计数、比例、类型与来源指针。
