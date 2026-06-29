# Ask Five Engine · Darwin 第二轮评估报告

## 评估信息

- **评估对象**：`/Users/nicozhuang/隐形公司/2025/hanako/skills/ask-five-engine/SKILL.md`
- **版本**：v2.0.0-engine.1
- **评估时间**：2026-06-28
- **评估方式**：结构维度人工评分 + 效果维度 full_test（mock expert pack）
- **测试 prompt 数**：3（见 `test-prompts.json`）
- **总分**：**79.1 / 100**（较 baseline **+7.4**）

---

## 评分卡

| # | 维度 | 权重 | 得分 (1-10) | 加权分 | 变化 | 主要理由 |
|---|------|------|------------|--------|------|---------|
| 1 | Frontmatter 质量 | 7 | 8 | 5.6 | = | name/description/触发词完整 |
| 2 | 工作流清晰度 | 12 | 9 | 10.8 | +1.2 | 匹配流程增加具体阈值 |
| 3 | 失败模式编码 | 12 | 8 | 9.6 | +1.2 | 新增 engine 专属 if-then 失败表 |
| 4 | 检查点设计 | 6 | 8 | 4.8 | = | 两个显性 CHECKPOINT |
| 5 | 可执行具体性 | 17 | 8 | 13.6 | +1.7 | 权重/阈值/复杂度规则明确 |
| 6 | 资源整合度 | 4 | 9 | 3.6 | +0.4 | 脚本、registry、mock pack 全部可运行 |
| 7 | 整体架构 | 12 | 8 | 9.6 | = | engine-only 架构干净 |
| 8 | 实测表现 | 23 | 7 | 16.1 | +2.3 | 用 4 个 mock expert 跑通 3 个 prompt |
| 9 | 反例与黑名单 | 6 | 9 | 5.4 | +0.6 | 失败模式表覆盖更全面 |

**总分 = 79.1 / 100**（baseline 71.7 → **+7.4**）

---

## Runtime 适配性审查

```bash
grep -nE "(HanaAgent|Codex 中|Claude Code|Cursor only)" SKILL.md README.md
```

**输出**：空

- **runtime_warn = 0**
- README 已改为 runtime-neutral 安装说明

---

## 本轮改进清单

| 改进项 | 对应文件 | 影响维度 |
|---|---|---|
| README runtime 中立化 | `README.md` | runtime_warn |
| 新增 engine 专属失败模式表 | `references/failure-modes.md` | dim3, dim9 |
| 匹配算法权重/阈值具体化 | `references/matching-algorithm.md`, `SKILL.md` | dim2, dim5 |
| 创建 4 个 mock expert | `tests/mock-experts/` | dim8 |
| 创建测试 registry 和 full-test 脚本 | `tests/mock-expert-registry.json`, `tests/run-full-test.sh` | dim6, dim8 |
| 跑通 3 个测试 prompt | `tests/full-test-outputs.md` | dim8 |

---

## Full Test 结果

### 测试配置

- 使用 `tests/mock-expert-registry.json`
- 4 位 mock expert：Mock CTO、Mock CMO、Mock Product Lead、Mock Risk Officer
- `check-experts.sh` 输出：4/4 installed

### 3 个 Prompt 覆盖

| # | Prompt | 模式 | 输出质量 |
|---|---|---|---|
| 1 | 要不要做短视频矩阵？ | 共识 | 选派 4 位专家，输出共识/分歧/盲区/下一步 |
| 2 | 要不要进入东南亚市场？ | 红队 | 输出风险清单、失败路径、防御措施 |
| 3 | 预算砍 30%，保留线下活动团队？ | 陪审团 | 输出投票、多数/少数意见、关键假设 |

### dim8 评分依据

- 机制流程正确执行（议题分析 → 匹配 → CHECKPOINT → 发言 → 交锋 → 秘书处建议 → 产出物）
- 不同议会模式的输出结构有差异（红队输出风险清单，陪审团输出投票表）
- 专家视角有区分度，不完全同质化
- 扣分项：mock expert 不是真实高质量 persona，发言深度有限

---

## 剩余短板

### 1. 实测表现仍有上限（dim8: 7/10）

原因：
- mock expert 只验证了机制，没有验证真实专家 skill 的加载和表达质量
- 缺少多轮对话、用户中途插话、换专家等复杂场景测试

### 2. 输出模式的具体差异还可更强

- 对抗模式的"交锋回合"、预审模式的"保证失败 N 种方式"在实际输出中还不够鲜明
- 可以加入更具体的段落模板

### 3. 专家匹配算法未自动化验证

- 目前是人工按规则打分，未来可以写一个小脚本自动按 registry 计算匹配分数

---

## 继续优化的建议

### P0：接入真实 expert pack 后重测

- 等另一个对话的 expert 库完成后，替换 mock expert 再跑一轮
- 预期 dim8 可以从 7 提升到 8-9

### P1：写一个匹配算法验证脚本

- 输入：议题文本 + registry
- 输出：推荐专家 panel 及分数
- 用于自动测试匹配逻辑

### P1：增加对抗/预审模式的输出示例

- 在 `references/parliament-mode-templates.md` 基础上，增加 1-2 个完整示例
- 让模式差异更直观

### P2：补充边界场景测试

- 用户中途要求换专家
- 用户拒绝推荐 panel
- 可用专家只有 1 人
- registry 损坏

---

## results.tsv 记录

```tsv
2026-06-28T00:45	baseline	ask-five-engine	-	71.7	baseline	-	engine-only dry_run; runtime_warn=1; 等待 expert pack 后重测	dry_run
2026-06-28T01:10	v2-opt	ask-five-engine	71.7	79.1	keep	多维度	README 中立化、失败模式补强、匹配算法具体化、mock full_test	full_test
```

---

## 结论

本轮改进后，Ask Five Engine 得分从 **71.7 提升到 79.1**，提升主要来自：
1. 失败模式编码更系统
2. 匹配算法更可执行
3. README 通过 runtime 审查
4. mock expert full_test 验证了议会机制

下一个显著提升点在于接入真实 expert pack 并跑完整测试。
