# 案例 004：CheckList 评分合同的反例诊断（RW-W2-CHECKLIST-MEASUREMENT-v1，2026-10-01）

- 处理日期：2026-10-01
- 处理人：本地主控会话（Research Workbench 第 2 周，任务书 [`RW-W2-CHECKLIST-MEASUREMENT-v1`](../../weeks/2026-10-07/PLAN.md)）
- 本周主问题：只检查"换序翻转＋同图判空"的评分门槛（R0），能否误接收不具备正确目标方向判断的策略；加入逐条件正确目标与提示不变性后（R1），能否在这个有限任务域中识别这些失败？

## 产物定位（全部在本仓库内）

| 项 | 值 |
|---|---|
| 事前注册 | [`weeks/2026-10-07/PREREG.md`](../../weeks/2026-10-07/PREREG.md)（含人工真值表 §4、AI 预测 §2、两合同与分母 §6）@提交 `56bed4ba9a7186fc3392a695358a5d41f806902c` |
| 机器可读合同 | [`experiments/checklist_measurement_v1/contract.json`](../../experiments/checklist_measurement_v1/contract.json) v1.0.0（同一冻结提交） |
| 实现 | [`run.py`](../../experiments/checklist_measurement_v1/run.py)（枚举+六策略+计分）、[`verify_static.py`](../../experiments/checklist_measurement_v1/verify_static.py)（独立核对）@提交 `a9d952e15fe55502412de58d20e430a967838315` |
| 冻结结果 | [`results_v1/`](../../experiments/checklist_measurement_v1/results_v1/)：rows.jsonl 128 行、summary.json、manifest.json、counterexamples/ @提交 `f7d20d4b6857b8cd1d748d837913a1b648af40b8` |
| 结果分析 | [`ANALYSIS.md`](../../experiments/checklist_measurement_v1/ANALYSIS.md)（逐策略行为归因、预测对账、边界） |
| 输入提交 | 任务书所在 `main` @ `5a4a7dd06d37e129f7f866c485b487205090f89a` |

## 事前预测（AI，注册于运行前；用户本次未提供预测）

PREREG §2 注册 P1–P6。对账结果：P1、P2、P4、P5、P6 证实；**P3 的数字细节被证伪**（预测 INVERT_TARGET MFT 80/128，实际 96/128——注册时少算了真值为判空的 AB/BA 行数），定性部分（R0 通过、只能靠逐条件正确性捕获、INV 满分）与预测一致。已注册文本保留原样，偏差在 ANALYSIS §5 如实记录。

## 核对的主张

| # | 主张 | 支持什么 | 仍不能支持什么 | 什么结果会改变结论 | 证据位置 |
|---|---|---|---|---|---|
| 1 | **关系门槛可被伪通过**：SLOT_ID（只读帧身份+顺序标记）与 INVERT_TARGET（读目标状态但方向互换）均通过 R0（换序关系 16/16＋AA/BB 判空 64/64）却均未通过 R1 | "换序翻转＋同图判空不足以认证正确目标方向判断"——在本合成域内的存在性证明（逻辑反例+可重放程序输出） | 真实模型中捷径的发生率；任何真实遥感任务上的表现 | 真实数据上按 R0 接收的策略被独立的方向读数证伪/证实的行为差异 | results_v1/summary.json；counterexamples/SLOT_ID.json、INVERT_TARGET.json |
| 2 | **完整合同在本域零漏检**：R1（逐条件 MFT＋DIR 关系/正确分列＋提示 INV＋AA/BB 判空＋全量记账）捕获全部 5 个错误策略 | 该有限域内 R1 对这 6 个固定策略的辨别能力 | R1 对真实模型、其他策略空间或弃答路径的充分性（真实 UNKNOWN/弃答只经桩测试 exercised） | 在本域构造出通过 R1 全部组件却方向错误的策略 | summary.json auxiliary.r1_misses=[]；verify_static 18/18 |
| 3 | **同图判空单独不排除捷径**：CONST_NULL 的 AA/BB 判空 64/64 满分、INV 64/64 满分，但变化行 0/32 全错 | 案例 003"判空是双刃证据"教训在可重放形式下的再现；判空只能排除恒报方向 | 任何真实模型的判空行为含义 | — | summary.json strategies.CONST_NULL |
| 4 | **INV 不是 MFT 的替代**：INVERT_TARGET 的提示不变性 64/64 满分但方向全错；SLOT_ID 则被 INV 捕获（32/64） | 不变性/关系类读数与逐条件正确性读数互补，缺一不可（CheckList MFT/INV/DIR 互补的本地实例化） | 真实模型上三种读数的充分组合 | — | ANALYSIS.md §3–§4 |

## 证据分级声明

- 主张 1 是**逻辑反例＋程序验证**：策略由规则定义，输出由确定性代码生成，真值由生成规则给出——不是真实任务的观测。
- 主张 2 是**本域程序性质**：6 策略固定清单、128 条完全枚举、分母冻结；不是对策略空间的抽样。
- 均不构成真实遥感参考、p2 checkpoint 能力、视觉机制或跨分布泛化的证据；个人掌握见 [`quiz.md`](quiz.md)（无真实作答，未检验）。

## 适用前提与竞争解释

- 前提：对象身份/语义尺度由生成器固定；策略全函数（无真实弃答）；提示版本只改一个任务无关标记。
- 未排除的竞争解释（对"R1 足够好"这一延伸主张）：真实模型的输出分布含 UNKNOWN/部分解析，桩测试只验证了记账不缩分母，未验证真实弃答下的判别力；真实域的"正确目标"需要参考效度建设（案例 003 的未解决问题原样保留）。

## 限制与下一次行动

- 限制：有限域诊断；128 条按 16 组汇总，不是独立样本；单次冻结运行（复跑逐字节一致已验证）。
- 下一次行动：第 3 周候选见 RETURN §8——把 R1 型读数合同（逐条件正确目标＋版本不变性＋全量记账）作为未来真实方向实验的合同模板；是否进入真实任务复用按 p2 当时已授权任务决定。

## 修正历史

- 无（首次交付）。

## 关联条目

- [`playbook/semantic-validity-of-controls.md`](../../playbook/semantic-validity-of-controls.md)（PB-003，候选；本次为其 §"使用记录 2026-10-01"）
- [`external_methods/2026-09-30_checklist.md`](../../external_methods/2026-09-30_checklist.md)（CheckList MFT/INV/DIR 来源与适配边界）
