# 反例摘录（最多 2 个，按 UID 字典序）

## 关系满足但类别错误 (relation_pass_but_wrong)

- UID: `00034_1_0|r110c224`（组件 `00034_1_0`，R1）
- 参考类别对 (gA,gB): (nvg_surface, low_vegetation)
- 缓存预测对 (pA,pB): (low_vegetation, buildings)
- 派生读数: relation_change_pass=True, pair_correct=False, bucket=OTHER_LEGAL_WRONG_DIFF
- 来源: p2@`9dcd77cc174117551f22b8b694feec00ac985292` 的 `reports/rsicc_evidence_conflict_20260930/run/CACHE_SEAL_report_a_shard*.json` components[`00034_1_0`].C_local[`R1`] 与同 cell 账本记录（`00034_1_0|C_local|A` / `|B`）
- 上游限制: p2 原件为私有仓库；外部读者无法访问。公开代码可在自有同格式缓存或人工 fixtures 上运行，不宣称全部历史数据公开可复现。

## 错误同类 (WRONG_SAME_CLASS)

- UID: `00058_1_0|r021c245`（组件 `00058_1_0`，R1）
- 参考类别对 (gA,gB): (buildings, nvg_surface)
- 缓存预测对 (pA,pB): (buildings, buildings)
- 派生读数: relation_change_pass=False, pair_correct=False, bucket=WRONG_SAME_CLASS
- 来源: p2@`9dcd77cc174117551f22b8b694feec00ac985292` 的 `reports/rsicc_evidence_conflict_20260930/run/CACHE_SEAL_report_a_shard*.json` components[`00058_1_0`].C_local[`R1`] 与同 cell 账本记录（`00058_1_0|C_local|A` / `|B`）
- 上游限制: p2 原件为私有仓库；外部读者无法访问。公开代码可在自有同格式缓存或人工 fixtures 上运行，不宣称全部历史数据公开可复现。
