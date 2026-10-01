# 案例 005：真实缓存复用——关系成立与类别正确分列（RW-W3-REAL-CACHE-REUSE-v1，2026-10-01）

- 处理日期：2026-10-01（名义周窗口 2026-10-14—10-20，按任务书允许提前启动）
- 处理人：本地主控会话（Research Workbench 第 3 周，任务书 [`RW-W3-REAL-CACHE-REUSE-v1`](../../weeks/2026-10-14/PLAN.md)）
- 性质：**RETROSPECTIVE_REUSE**——把第 2 周"输出关系与绝对正确性分开评价"的做法，复用到已验收的真实 C_local 单侧类别预测缓存上。图像输出是真实历史输出；不新增样本、不构成独立确认、不测试模型重新接收换序图像后的表现。
- 本周主问题（照任务书）：**在冻结的真实缓存上，有多少目标满足预期的变化／换序关系，却没有给出正确的两侧类别？**

## 产物定位

| 项 | 值 |
|---|---|
| 事前注册 | [`weeks/2026-10-14/PREREG.md`](../../weeks/2026-10-14/PREREG.md)（AI 预期 §3、已知信息 §5、读数与五桶 §6）@冻结提交 `688d2f6d456ae83f9435effa46a8bb474ae9078f` |
| 机器可读合同 | [`experiments/real_cache_relation_v1/contract.json`](../../experiments/real_cache_relation_v1/contract.json) v1.0.0（同一冻结提交） |
| 实现 | [`run.py`](../../experiments/real_cache_relation_v1/run.py)（只读 git show 提取+三方核对+派生+计分）、[`verify_fixtures.py`](../../experiments/real_cache_relation_v1/verify_fixtures.py)（9 组人工 fixtures 回归）@提交 `2f433ee`（见本案例 EVIDENCE） |
| 公开聚合结果 | [`experiments/real_cache_relation_v1/results_v1/`](../../experiments/real_cache_relation_v1/results_v1/)：summary.json、manifest.json、counterexamples.md |
| 逐目标派生表 | `experiments/real_cache_relation_v1/local_only/`（**git 忽略，仅本地**：116 目标行+464 派生行，含 UID） |
| 来源固定提交 | `zxqklein/p2` `feat/c1-directional-delta-v1` @历史数据 `9dcd77cc174117551f22b8b694feec00ac985292`、现行解释 `a0ddc50c2194bf74d60c9faf6d8a706d17b1440b`（只读，git show 访问，未切换/清理/重置 p2 工作区） |
| 结果读数 | 见 [RESULTS.md](RESULTS.md)；证据分级见 [EVIDENCE.md](EVIDENCE.md) |

## 一句话结论

在 116 个冻结真实目标中，**36 个（31.03% 微平均，父组件等权 0.3016）满足变化关系（两侧类别不同、互为交换）却未给出正确的两侧类别**；状态 **REUSE_OBSERVED_IN_SCOPE**。这是本固定缓存的诊断频数，不外推发生率，不是独立确认。

## 与第 2 周的关系

第 2 周在合成域证明了"关系满足仍可全错"（策略级反例，2/5）。第 3 周把同一评价方式用于**真实模型历史输出**：不再构造策略，而是把已封存的 C_local 单侧缓存机械派生为 AB/BA/AA/BB，统计关系×正确性的交叉计数。关系本身由同一缓存构造（成立仅认证组合实现），本周的新增信息是**该缓存中关系与类别错误的共存频数**。
