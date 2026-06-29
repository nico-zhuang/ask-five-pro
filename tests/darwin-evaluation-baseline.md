# Ask Five Engine · Darwin 基线评估报告

## 评估信息

- **评估对象**：`/Users/nicozhuang/隐形公司/2025/hanako/skills/ask-five-engine/SKILL.md`
- **版本**：v2.0.0-engine.1
- **评估时间**：2026-06-28
- **评估方式**：结构维度人工评分 + 效果维度 dry_run 模拟推演
- **测试 prompt 数**：3（见 `test-prompts.json`）
- **总分**：**71.7 / 100**

---

## 评分卡

| # | 维度 | 权重 | 得分 (1-10) | 加权分 | 主要理由 |
|---|------|------|------------|--------|---------|
| 1 | Frontmatter 质量 | 7 | 8 | 5.6 | name/description/触发词完整；description 未超过 1024 字符；无空话尾巴 |
| 2 | 工作流清晰度 | 12 | 8 | 9.6 | Phase 0-7 顺序清晰，输入输出较明确 |
| 3 | 失败模式编码 | 12 | 7 | 8.4 | 有空 registry 处理、fallback 规则、失败模式引用；但 if-then 失败分支可更系统 |
| 4 | 检查点设计 | 6 | 8 | 4.8 | Phase 2 和 Phase 7 有 🔴 CHECKPOINT，显性标记 |
| 5 | 可执行具体性 | 17 | 7 | 11.9 | 有匹配公式和模板；但部分描述仍偏概括，"根据模式不同"等可更硬 |
| 6 | 资源整合度 | 4 | 8 | 3.2 | references/ 路径正确，脚本可运行 |
| 7 | 整体架构 | 12 | 8 | 9.6 | 架构干净，无 AI 腔废话，符合 engine-only 定位 |
| 8 | 实测表现 | 23 | 6 | 13.8 | dry_run：空 registry onboarding 清晰；mock expert 流程可跑通；但缺少真实多专家场景验证 |
| 9 | 反例与黑名单 | 6 | 8 | 4.8 | anti-patterns.md、failure-modes.md、红线声明完整 |

**总分 = 71.7 / 100**

---

## Runtime 适配性审查

```bash
grep -nE "(HanaAgent|Codex 中|Claude Code|Cursor only)" SKILL.md README.md
```

**命中**：`README.md:27:### HanaAgent`

- **runtime_warn = 1**
- 问题：README 安装章节按 runtime 分节（HanaAgent / Codex），属于 runtime-specific 表述
- 建议：合并为「通过本地路径安装」+「自动检测常见 runtime」两层结构

---

## 测试 Prompt 与推演

### Prompt 1：短视频矩阵

> Ask Five，帮我看看要不要做短视频矩阵？

**推演**：
- 空 registry → 输出 onboarding，提示安装 expert pack
- 有 expert-core-pack → 匹配 MrBeast、张一鸣、芒格等
- 预期输出：共识模式会议纪要 + 选题清单/Hook 方案

**dim8 评分依据**：空 registry 路径清晰；有专家时匹配算法可落地

### Prompt 2：红队模式进入东南亚市场

> 红队模式：我们要不要进入东南亚市场？

**推演**：
- 识别 mode=red-team
- 优先选风险、战略、逆向型专家
- 输出风险清单、失败路径、防御措施

**dim8 评分依据**：模式模板已定义，但实际效果依赖外部 expert skill 质量

### Prompt 3：陪审团模式预算决策

> 陪审团模式：今年预算砍 30%，我们要不要保留线下活动团队？

**推演**：
- 识别 mode=jury
- 专家针对二选一问题投票
- 输出投票结果、多数/少数意见、关键假设

**dim8 评分依据**：陪审团模板完整，但未经过真实投票冲突场景验证

---

## 主要短板

### 1. 实测表现弱（dim8: 6/10）

原因：
- engine-only 版本没有内置专家
- 当前缺少真实多专家 pack，无法验证交锋、共识、对抗等核心机制
- 陪审团/红队/预审模式停留在模板层面，未经过实际运行

### 2. 可执行具体性有提升空间（dim5: 7/10）

具体表现：
- "根据模式不同"等措辞可以改为硬性条件分支
- Phase 1 匹配算法中的权重可给出默认值和调参说明
- 资源约束的解析规则未完全明确

### 3. 失败模式编码不够系统（dim3: 7/10）

当前有：
- 空 registry
- expert skill 缺失 fallback

缺少：
- registry JSON 损坏的处理
- 专家 skill frontmatter 不兼容的处理
- 议会模式识别失败的 fallback
- 输出模式参数非法的处理

### 4. Runtime 适配性小红灯（README）

README 按 HanaAgent / Codex 分节，可改为 runtime-neutral 表达。

---

## 改进建议（按优先级）

### P0：补齐真实专家 pack 并跑 full_test

- 等待/接入 `expert-core-pack`
- 用 3 个测试 prompt 做真实多专家会议
- 只有 dim8 有真实验证，总分才可信

### P1：把匹配算法具体化

在 `references/matching-algorithm.md` 基础上，在 SKILL.md 中补充：
- 默认权重表
- 同质化 penalty 的判定阈值（如 domain 重叠 > 50%）
- 复杂度判断的明确规则

### P1：系统化失败模式

增加一个 `references/failure-modes-engine.md` 或扩展现有 `failure-modes.md`：

| 失败场景 | 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|---|
| registry 损坏 | JSON 解析失败 | 提示用户检查 registry | 回退到空 registry onboarding |
| expert skill 不兼容 | frontmatter 缺少必需字段 | 跳过该专家并提示 | 用通用 fallback 画像 |
| 模式识别失败 | 用户指定了无法识别的模式 | 默认共识模式并提示 | 询问用户 |

### P2：README runtime 中立化

把 "HanaAgent / Codex" 分节改为：
- 通用安装（一行命令）
- 手动路径（常见 runtime 表）

---

## 结论

Ask Five Engine 作为 architecture-only 版本，基线得分 **71.7 / 100**，主要失分在**实测表现**（缺少真实专家 pack）和**可执行具体性**。

这个分数是合理的：引擎骨架已经完整，但核心价值需要外部 expert pack 才能释放。下一步最关键的动作是：**接入真实专家库并重新跑一轮 full_test 评估**。

---

## results.tsv 记录

```tsv
2026-06-28T00:45	baseline	ask-five-engine	-	71.7	baseline	-	engine-only dry_run; runtime_warn=1; 等待 expert pack 后重测	dry_run
```
