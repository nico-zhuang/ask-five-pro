# Ask Five Engine · Darwin 第三轮评估报告

## 评估信息

- **评估对象**：`/Users/nicozhuang/隐形公司/2025/hanako/skills/ask-five-engine/SKILL.md`
- **版本**：v2.0.0-engine.1
- **评估时间**：2026-06-28
- **评估方式**：结构维度人工评分 + 效果维度 full_test（mock expert pack）
- **测试 prompt 数**：4（见 `test-prompts.json`）
- **总分**：**79.7 / 100**（较 v2 **+0.6**）

---

## 评分卡

| # | 维度 | 权重 | 得分 (1-10) | 加权分 | 变化 | 主要理由 |
|---|------|------|------------|--------|------|---------|
| 1 | Frontmatter 质量 | 7 | 8 | 5.6 | = | 完整，无空话尾巴 |
| 2 | 工作流清晰度 | 12 | 9 | 10.8 | = | Phase 清晰，模式选择表增加可用性 |
| 3 | 失败模式编码 | 12 | 8 | 9.6 | = | 20 条 if-then 失败模式 |
| 4 | 检查点设计 | 6 | 9 | 5.4 | +0.6 | 新增淬火模式 CHECKPOINT |
| 5 | 可执行具体性 | 17 | 8 | 13.6 | = | 模式选择表、淬火模板具体 |
| 6 | 资源整合度 | 4 | 9 | 3.6 | = | 脚本、registry、mock pack 可运行 |
| 7 | 整体架构 | 12 | 8 | 9.6 | = | engine-only 架构稳定 |
| 8 | 实测表现 | 23 | 7 | 16.1 | = | 4 个 prompt 覆盖 6 种模式中的 4 种，仍受限于 mock expert |
| 9 | 反例与黑名单 | 6 | 9 | 5.4 | = | 失败模式 + 反模式完整 |

**总分 = 79.7 / 100**（v2 79.1 → **+0.6**）

---

## 本轮新增内容

| 新增内容 | 文件 | 影响 |
|---|---|---|
| 模式选择速查表 | `SKILL.md` | dim4 / 可用性 |
| 淬火模式完整机制 | `SKILL.md` + `parliament-mode-templates.md` | dim2 / dim4 |
| 淬火模式测试输出 | `tests/full-test-outputs.md` | dim8 覆盖度 |

---

## 测试覆盖

| # | Prompt | 模式 | 状态 |
|---|---|---|---|
| 1 | 要不要做短视频矩阵？ | 共识 | ✅ 跑通 |
| 2 | 要不要进入东南亚市场？ | 红队 | ✅ 跑通 |
| 3 | 预算砍 30% 是否保留线下活动团队？ | 陪审团 | ✅ 跑通 |
| 4 | 要不要 all-in AI 客服？ | 淬火 | ✅ 跑通 |

未覆盖模式：对抗、预审。但模板已定义，机制与已覆盖模式同构。

---

## 主要瓶颈

本轮分数提升有限（+0.6），因为：
1. 大改动在**内容扩展**，但 Darwin 评分更看**结构/实测/失败模式**
2. dim8（实测表现）仍被 mock expert 质量天花板卡住
3. 要继续大幅提升，必须接入真实 expert pack 跑 full_test

---

## 分数上限分析

| 条件 | 预估总分 |
|---|---|
| 当前状态（mock expert） | ~80 |
| 接入真实 expert pack，跑 4-6 个 prompt full_test | 85-88 |
| 接入真实 expert pack + 自动测试脚本 + 优化措辞 | 88-92 |

---

## 结论

Ask Five Engine 当前得分 **79.7 / 100**。引擎本身的结构、流程、失败模式、议会模式设计已经比较完整。

**后续提升的核心路径不是再改 engine，而是接入 brain-crew 的真实 expert pack 并跑实测。**

---

## results.tsv 记录

```tsv
2026-06-28T00:45	baseline	ask-five-engine	-	71.7	baseline	-	engine-only dry_run; runtime_warn=1; 等待 expert pack 后重测	dry_run
2026-06-28T01:10	v2-opt	ask-five-engine	71.7	79.1	keep	多维度	README 中立化、失败模式补强、匹配算法具体化、mock full_test	full_test
2026-06-28T02:30	v3-opt	ask-five-engine	79.1	79.7	keep	模式扩展	增加模式选择速查、淬火模式、淬火测试输出	full_test
```
