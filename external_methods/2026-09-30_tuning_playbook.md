# 外部方法迁移说明：Google Deep Learning Tuning Playbook

- 读取日期：2026-09-30
- 来源与版本：`google-research/tuning_playbook`，`main` 分支，最新提交 `7554a51f5d3002ba90308d39701b586f5a9b962e`（2024-06-13，GitHub API 查询）；仓库 41 commits、约 30.3k stars；作者声明"非 Google 官方支持产品"、自称 living document。正文经 `raw.githubusercontent.com/.../main/README.md` 全文读取。
- 性质：**借鉴建议**，不是已验证经验；与 playbook/ 三条候选条目分开。
- 术语对应：任务书所称"研究变量／配套调优变量／固定变量"，playbook 实际术语为 **scientific hyperparameters**（要测量其效应的变量）、**nuisance hyperparameters**（为公平比较 scientific 值而必须对其优化/控制的变量）、**fixed hyperparameters**（本轮固定、但"为结论制造 caveat"的变量），另有 conditional hyperparameters。

## 原方法解决什么问题

把调优从"试配方"变成可积累的实验序列：每轮实验只回答一个窄问题；识别 scientific/nuisance/fixed 超参数；从结果中提取洞察（搜索空间边界检查、欠采样、不可行 trial、训练曲线问题、isolation plots 做 apples-to-apples 比较）；采用变更前用 study variance 与多次重跑判断，"只采纳有强证据支持的改动，不采纳运气"。

## p2 哪个已观察问题与之对应

1. **公平比较的变量结构**：R2 的"工作点先冻结 + 闭式随机对照"（案例 001）已经是 fixed/nuisance 处理的良好实例；但 R8 之后的下一轮比较（primitives week 的 2×2 策略×条件实验）尚未成文"哪臂的 nuisance 参数分别调优、哪些全程 fixed"。playbook 的警示"改 batch size 必须重调优化器/正则"对应到本环境即"换来源/分辨率/通道数后，学习率等不能直接沿用"。
2. **insight 与 gain 的分离**：p2 的多次收口决定（R5–R8）反复出现"本轮不授权追分，只授权可识别性诊断"——与 playbook 的 exploration vs exploitation 一致，可作为既有实践的文献支撑，也可帮下一轮写清"本轮要的是洞察还是收益"。
3. **采用规则**：playbook "trial variance vs study variance、重跑 N 次再采纳"对应 R8 的三 seed 规则；差异在 p2 每轮预算极小，只能以"种子方向一致 + 区间"代替大 N 重跑。

## 哪些前提不成立

- playbook 假设可以反复跑大量 trial 做 nuisance 重调优；p2 每周 GPU 预算以 GPU-hours 计（上周 22 GPU-h 上限量级），大网格不可行——只能显式声明 nuisance 处理方式（固定并记 caveat，或最小重调）。
- playbook 的步骤数/训练时长建议假设 compute-bound 情形可估；p2 需先按实际吞吐小试。
- playbook 面向"提升单一模型性能"；p2 当前瓶颈更多在**测量可识别性**（案例 002/003），变量契约解决不了测量对象本身的问题。

## 最强竞争解释（本周预定义补充）

下一轮比较若失败，最强竞争解释不是"变量契约没写好"，而是**数据/配准可证性不足**（R8-D2：65 对中 29 配准通过、36 未通过；事实尺度下可确认变化极少）。变量契约是必要的设计卫生，不是充分条件；不能指望它把不可识别的读数变成可识别。

## 最低成本的验证

文档级、0 GPU：为下一轮已授权比较写一页**变量契约**——列出 scientific（1 个）、nuisance（各臂处理方式：固定值 + caveat 或分别调优）、fixed（分辨率 256×256、事实尺度、参考版本）三类，并用既有回执核对是否满足。这可作为第 2 周首选实验 PLAN 的固定章节，不需要独立实验。

## 对第 2 周候选排序的输入

本方法单独作为"实验"不可测（产物是文档），但作为首选实验的**设计约束**并入；排序见 `weeks/2026-09-30/RETURN.md` 第 8 项。

## 许可核对与本地使用更新（2026-09-30）

已读取固定版本 7554a51f5d3002ba90308d39701b586f5a9b962e 的 README 署名及 LICENSE：上游为 CC BY 4.0，LICENSE blob 为 90074ad90b1c37004db242af0258fb1f8c0e16c0。署名、来源及许可链接见 [SOURCES_AND_LICENSES.md](../docs/SOURCES_AND_LICENSES.md)。本笔记为本项目中文阅读与适配意见，不是完整翻译；本仓库 MIT 不替代上游许可。

第二周仅将科学变量／干扰因素／固定因素的区分用于一份评分诊断合同；不据此宣称完成训练方法验证，或授权 p2 新模型实验。

