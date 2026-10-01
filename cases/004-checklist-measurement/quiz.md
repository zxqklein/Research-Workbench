# 作者判例题 004：一个新策略能否骗过评分合同？

- 开放时间：2026-10-01（results_v1 冻结之后）
- 建议用时：10–15 分钟
- **建议顺序：先在本文件上作答（写在纸面或本地，不写进仓库），再打开 [`results_v1/summary.json`](../../experiments/checklist_measurement_v1/results_v1/summary.json)、[`ANALYSIS.md`](../../experiments/checklist_measurement_v1/ANALYSIS.md) 和答案卷。** 无真实作答时个人掌握维持"未检验"，不影响客观实验。

## 背景回顾（只给定义，不给结果）

第 2 周冻结合同（`contract.json` v1.0.0）中：

- R0（关系门槛）＝ 8 个变化组上 AB/BA 都给方向回答且 BA 与 AB 反向（16 配对）＋ AA/BB 全部判空（64 条）。
- R1（完整合同）＝ 逐条件 MFT 128 条全对 ＋ AB/BA 联合 32 配对 ＋ DIR 关系 16/16 与变化行正确 32/32 分列 ＋ 提示不变性 64 配对 ＋ AA/BB 判空 64 条 ＋ 无 UNKNOWN/缺失/非法。

## 新策略：PHASE_CONFUSER

- 允许读取的字段：`frame_id_first`、`frame_id_second`（**不给顺序标记，不给任何对象状态**）。
- 规则：先帧是 A、后帧是 B → 答 `APPEAR`；先帧是 B、后帧是 A → 答 `DISAPPEAR`；两帧同 ID → 答 `NO_EXISTENCE_CHANGE`。
- 与本周 SLOT_ID 的差别：**完全忽略顺序标记**（SLOT_ID 按标记在 ORIGINAL→APPEAR / REVERSED→DISAPPEAR 之间切换）。

## 请判断并说明理由

1. PHASE_CONFUSER 能否通过 R0？逐格说明（变化组换序关系在两个提示版本下分别如何；AA/BB 判空格如何）。
2. 若它通过 R0：R1 的哪个组件会捕获它、为什么？哪个组件**不会**捕获它、为什么？
3. 它与本周某个真实运行过的反例行为最接近——是哪一个？两者在 R1 各组件上的差别是什么？
4. （开放）如果让 PHASE_CONFUSER 再读一个字段，它最少还需要什么信息才能通过 R1？这提示真实方向实验的读数合同里哪个组件最不可删？

答案卷：[`quiz_answer_key.md`](quiz_answer_key.md)（作答后再打开）。
