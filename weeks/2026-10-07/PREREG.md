# 第 2 周事前注册（PREREG）：CheckList 评分合同的反例诊断

- 任务 ID：`RW-W2-CHECKLIST-MEASUREMENT-v1`
- 注册时间：2026-10-01（北京时间），**早于任何评分运行**；本文件与 [`experiments/checklist_measurement_v1/contract.json`](../../experiments/checklist_measurement_v1/contract.json) 在评分运行前提交冻结。
- 任务书：[`weeks/2026-10-07/PLAN.md`](PLAN.md)（本文件按其 §5 T1 登记，不改写任务书定义）。
- 执行仓库输入：`zxqklein/Research-Workbench` `main` @ `5a4a7dd06d37e129f7f866c485b487205090f89a`（含本任务书的交接提交；本地已 `--ff-only` 快进同步，同步前工作区干净，无既有改动需要保留）。
- 执行环境：Linux 6.8.0-40-generic x64；Python 3（仅标准库，版本见 manifest）；纯 CPU，无 GPU。
- 冻结纪律：冻结后如发现真值表、提示语义、分母或字段权限不一致，按任务书 §4 暂停受影响计分、保存失败尝试、记录原因并**重新冻结为新版本**；不隐藏失败运行，不用事后改动冒充原方案。

## 1. 主问题（照抄任务书 §1，不重新表述）

**只检查"换序翻转＋同图判空"的评分门槛，能否误接收不具备正确目标方向判断的策略；加入逐条件正确目标与提示不变性后，能否在这个有限任务域中识别这些失败？**

## 2. AI 事前预测（注册于运行前；不是用户的预测，用户本次未提供预测）

- **P1（任务书 §1 已登记的 AI 预测，逐字）**：至少存在一种仅依赖顺序提示和输入身份的策略，能通过关系门槛（R0）却无法通过完整合同（R1）。
- P2：SLOT_ID 通过 R0（换序关系 16/16、AA/BB 判空 64/64），未通过 R1（预测 MFT 80/128，且版本间 INV 失败）。
- P3：INVERT_TARGET 通过 R0，未通过 R1（预测 MFT 80/128，但 INV 64/64——即 R1 只能靠逐条件 MFT/DIR 正确性捕获它，提示不变性捕获不了）。
- P4：CONST_NULL、CONST_APPEAR、DISTRACTOR 均未通过 R0（前两者在变化组给不出方向回答或关系不反向；DISTRACTOR 在 4 个干扰对象不变的组上给不出方向回答，预测关系 8/16）。
- P5：ORACLE 通过 R1 全部组件（这是实现自检，不是科学发现；不通过即实现错误，按任务书 §6 定位后报告）。
- P6：唯一主读数（见 §6）= **2/5**。

阴性或不同于预测的结果同样完整保留；不为符合预测修改输出、删行或缩小分母。

## 3. 枚举规则（确定性，无随机抽样）

- 组编码：`(t_A, t_B, d_A, d_B) ∈ {0,1}^4`，组号 `g = 8·t_A + 4·t_B + 2·d_A + d_B`，共 **16 组**（g0–g15）。目标实体 `t` 与干扰实体 `d` 身份由生成器固定，语义尺度无歧义。
- 变化组（目标存在性改变）：`t_A ≠ t_B` 即 **g4–g11（8 组）**；其余 8 组目标存在性不变。
- 条件：每组生成 **AB、BA、AA、BB** 四种条件。帧 A 背景标识 `bgA`、帧 B 背景标识 `bgB`（两帧不同）；AA/BB 逐字段复制同一帧（输入身份相同）。
- 提示版本：每条件 2 个版本。版本 0：AB/AA/BB 的顺序标记 `ORIGINAL`，BA 标记 `REVERSED`；版本 1 仅将两标记对调。标记与任务无关：**任务始终按实际输入先后顺序回答目标存在性方向**，标记不改变实体或实际输入顺序。
- 规模：16 组 × 4 条件 × 2 版本 = **128 条受控输入**。这是 16 组的受控展开，**按组汇总，不得称为 128 个独立样本**。
- 输入键：`g<NN>|<条件>|v<版本>`，必须唯一（验收项）。

## 4. 真值表（人工由状态表推导；与 run.py 的真值函数相互独立核对）

方向规则：先帧不存在→后帧存在 = `APPEAR`；先存在→后不存在 = `DISAPPEAR`；同有同无 = `NO_EXISTENCE_CHANGE`（下表缩写 `NC`）。NC 只指**目标存在性不变**，不代表场景无其他变化。

| 组 | t_A,t_B | d_A,d_B | AB 真值 | BA 真值 | AA 真值 | BB 真值 |
|----|---------|---------|---------|---------|---------|---------|
| g0 | 0,0 | 0,0 | NC | NC | NC | NC |
| g1 | 0,0 | 0,1 | NC | NC | NC | NC |
| g2 | 0,0 | 1,0 | NC | NC | NC | NC |
| g3 | 0,0 | 1,1 | NC | NC | NC | NC |
| g4 | 0,1 | 0,0 | APPEAR | DISAPPEAR | NC | NC |
| g5 | 0,1 | 0,1 | APPEAR | DISAPPEAR | NC | NC |
| g6 | 0,1 | 1,0 | APPEAR | DISAPPEAR | NC | NC |
| g7 | 0,1 | 1,1 | APPEAR | DISAPPEAR | NC | NC |
| g8 | 1,0 | 0,0 | DISAPPEAR | APPEAR | NC | NC |
| g9 | 1,0 | 0,1 | DISAPPEAR | APPEAR | NC | NC |
| g10 | 1,0 | 1,0 | DISAPPEAR | APPEAR | NC | NC |
| g11 | 1,0 | 1,1 | DISAPPEAR | APPEAR | NC | NC |
| g12 | 1,1 | 0,0 | NC | NC | NC | NC |
| g13 | 1,1 | 0,1 | NC | NC | NC | NC |
| g14 | 1,1 | 1,0 | NC | NC | NC | NC |
| g15 | 1,1 | 1,1 | NC | NC | NC | NC |

推导说明：AB 按实际顺序读 `(t_A,t_B)`；BA 实际先帧是 B，读 `(t_B,t_A)`；AA/BB 两帧相同，目标存在性必不变。干扰对象状态不影响目标真值。

## 5. 六种固定策略与字段权限（评分目标不传给捷径策略）

`target_exist_first/second` = 目标在实际先帧/后帧的存在性；`distractor_*` 同理；`frame_id_first/second` = 实际先/后帧的帧身份（A 或 B）；`order_mark` = 顺序标记。运行器按本表权限过滤字段后才能传入策略函数——策略函数在结构上拿不到未授权字段。

| 策略 | 允许读取的字段 | 规则 | 用途 |
|---|---|---|---|
| ORACLE | target_exist_first, target_exist_second | 按方向规则返回 | 合成域正确策略，评分核对用；不是实测模型 |
| CONST_NULL | （无） | 恒返回 NO_EXISTENCE_CHANGE | 恒判空与变化样本分母检查 |
| CONST_APPEAR | （无） | 恒返回 APPEAR | 恒报方向与同图条件检查 |
| SLOT_ID | frame_id_first, frame_id_second, order_mark | 同帧返回 NC；否则标记 ORIGINAL 答 APPEAR、REVERSED 答 DISAPPEAR | "输入身份＋提示"能否伪通过关系门槛；禁止读对象状态 |
| INVERT_TARGET | target_exist_first, target_exist_second | 按方向规则计算后互换 APPEAR/DISAPPEAR，NC 保持 | 两次一起答错但保持换序关系 |
| DISTRACTOR | distractor_exist_first, distractor_exist_second | 对干扰对象存在性按方向规则返回 | 关系正确却绑定错对象 |

权限的行为学核对（验收项，能改变科学读数才做）：给定 (条件, 版本) SLOT_ID 输出必须与组无关；给定 (target_exist_first, target_exist_second)，ORACLE/INVERT_TARGET 输出与组及干扰状态无关；给定 (distractor_exist_first, distractor_exist_second)，DISTRACTOR 输出与目标状态无关；CONST_* 全表恒定。违反即权限声明为假，计分暂停。

## 6. 两个评分合同与固定分母

**R0（关系门槛）**，逐策略：

1. 变化组换序关系：8 个变化组 × 2 版本 = **16 个组内配对**（每版本 8 个）。通过条件：AB、BA 均给出方向回答（APPEAR/DISAPPEAR），且 BA 与 AB 反向。UNKNOWN/缺失/非法/NC 一律不通过该格。
2. AA/BB 判空：16 组 × 2 条件 × 2 版本 = **64 条**（每版本 32 条）。通过条件：答案为 NO_EXISTENCE_CHANGE。
3. R0 通过 = 上述 16 配对与 64 条**全部**通过；不以弃答或缺记录缩小分母。

**R1（完整合同）**，逐策略：

- MFT：分母 **128 条**；正确 = 答案与该条件自己的正确目标一致；分解为 类别 × 条件 × 提示版本（24 个单元格）；另报 AB/BA 同时正确的组内配对，分母 **16 组 × 2 版本 = 32**。
- DIR：变化子集上换序关系通过数（分母 16 配对）与答案正确数（分母 8 组 × 2 条件 × 2 版本 = **32 条**）**分列**，另报变化组内 AB/BA 同时正确配对（分母 16）。
- INV（提示不变性）：同组同条件的两个版本应给出相同任务答案，分母 **16 组 × 4 条件 = 64 配对**；通过 = 两版本答案**均为有效答案且相等**；任一版本 UNKNOWN/缺失/非法记该配对不通过并独立记账（不用非答案冒充不变性）。AA/BB 判空单列，分母 **64 条**。
- 全量记账：错误、UNKNOWN、缺失记录、非法输出四类独立计数，分母固定 128；禁止用"解析成功率"替代任务准确率。
- R1 通过 = MFT 128/128 ∧ 联合 32/32 ∧ DIR 关系 16/16 ∧ DIR 变化行正确 32/32 ∧ INV 64/64 ∧ AA/BB 64/64 ∧ unknown=missing=illegal=0。

**唯一主读数**：固定的 5 个非 ORACLE 策略中，**通过 R0 且未通过 R1 的策略个数**，逐策略给反例组与完整输入/输出。该数量只是所列反例策略的描述，不能估计真实模型中捷径的发生率。辅助读数：六策略完整仪表表与 R1 漏检清单。两套合同分别报告，不合成加权总分。

## 7. 成本与停止条件

- 新增训练 0、GPU 0、受测模型/VLM/judge/API 调用 0、付费 0、数据/模型/依赖下载 0。
- CPU ≤ 2 core-hours（本域为毫秒级确定性计算，预期远低于上限）；记录墙钟与 CPU 计时来源；执行助手 token 不可观测，记 UNKNOWN，不填 0。
- 停止条件：首次完整运行 + 反例枚举 + 必要验证通过即收口；不为占满预算追加 seed、策略、模拟或运行次数。复跑仅限实现错误定位（结果另存目录，不覆盖）。
- 需要真实图像、模型调用、标注或扩大预算时，完成本周有限域交付后集中提出，不自动搭车。

## 8. 接口与产物（预注册，供 T2/T3 对账）

- 命令：`python3 experiments/checklist_measurement_v1/run.py --contract experiments/checklist_measurement_v1/contract.json --prereg-commit <PREREG提交SHA> --out <新结果目录>`；结果目录已有内容时拒绝覆盖。
- 产物：`rows.jsonl`（128 行逐条输入+六策略输出）、`summary.json`（逐策略 R0/R1 全分母读数与主读数）、`manifest.json`（源码/合同 SHA-256、预注册提交、命令、环境、实际数量、资源记录）、`counterexamples/`（主读数反例的最少必要证据）。
- 独立核对：`verify_static.py` 用**人工硬编码的真值表**（§4 的独立转录，不是 run.py 真值函数的输出）比对运行结果，并做 §5 权限行为学核对、联合正确性独立重算、UNKNOWN/非法/缺失不缩分母的桩策略测试、输入键唯一性检查。

## 9. 用户作答与个人掌握

本周为作者个人练习设计的判例题（案例 004 附 quiz）在运行后开放；无用户真实作答前，个人掌握维持**未检验**，不影响客观实验结果。
