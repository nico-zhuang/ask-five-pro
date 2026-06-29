# Brain Crew 贡献指南

Brain Crew 是 Ask Five Engine 的专家库核心包。所有专家都以独立 skill 形式存在，通过 `expert-registry.json` 注册。

## 目录

- [新增专家流程](#新增专家流程)
- [专家文件结构](#专家文件结构)
- [Pack 分配规则](#pack-分配规则)
- [敏感度标记](#敏感度标记)
- [质量门槛](#质量门槛)
- [审查清单](#审查清单)
- [脚本工具](#脚本工具)

---

## 新增专家流程

1. **确认候选专家符合条件**（详见 [EXPERT_CRITERIA.md](./EXPERT_CRITERIA.md)）。
2. **创建专家目录**：`packs/<pack>/<expert-id>/`
3. **编写 `SKILL.md`**，包含统一 frontmatter 和角色内容。
4. **更新 `expert-registry.json`**，添加新专家条目。
5. **运行质量检查脚本**，确保 Darwin 评分 ≥85。
6. **提交 PR 或补丁**，附带评分输出截图/文本。

---

## 专家文件结构

每个专家是一个独立 skill 目录：

```text
packs/<pack>/<expert-id>/
└── SKILL.md
```

最小 viable 结构：

```markdown
---
id: expert-id                 # 全局唯一，kebab-case
name: 专家姓名                 # 显示名
pack: core                    # core / brand / tech / enterprise / meta
core_domain: ["领域1", "领域2"]  # 2-4 个核心领域
style: ["风格1", "风格2"]       # 2-4 个表达/思维风格
topic_tags: ["标签1", "标签2"]   # 5-8 个触发标签
sensitivity: normal           # normal / sensitive
version: 1.0.0
---

# 专家姓名 · 副标题

> 一句代表性引用

## 触发场景

- 用户问什么问题时激活
- 哪些关键词出现时激活

## 回答工作流（Agentic Protocol）

### Step 1：...
### Step 2：...
### Step 3：...

🔴 **CHECKPOINT**：...

## 核心心智模型

## 失败模式与 Fallback

| 失败场景 | 症状 | 应对措施 |
|---|---|---|

## 反例黑名单

| # | 反模式 | 为什么错 | 正确做法 |
|---|---|---|---|
```

---

## Pack 分配规则

| Pack | 定位 | 示例 |
|------|------|------|
| `core` | 通用思维操作系统，产品/战略/决策/学习/工程 | 乔布斯、张一鸣、芒格、Paul Graham、费曼、马斯克 |
| `brand` | 品牌、传播、内容、增长 | MrBeast、奥格威、GWTB、鲁迅、郭德纲 |
| `tech` | AI、软件、系统、工程 | Karpathy、Ilya、Rob Pike、黄仁勋 |
| `enterprise` | 商业、投资、管理、组织、敏感角色 | 巴菲特、贝佐斯、稻盛和夫、特朗普、张雪峰 |
| `meta` | 关于 AI/skill/agent 本身的工具 | 达尔文、花叔蜂群、花叔女娲 |

**注意**：敏感角色（政治、教育争议等）必须放进 `enterprise` pack 并标记 `sensitivity: sensitive`。

---

## 敏感度标记

- `normal`：默认启用，可被任意查询匹配。
- `sensitive`：默认排除，仅在 `mode=debate` 或显式开启时启用。

当前敏感专家：

- 唐纳德·特朗普（`trump-perspective`）
- 张雪峰（`zhangxuefeng-perspective`）

新增敏感专家需经维护者审核。

---

## 质量门槛

所有专家必须通过：

```bash
bash scripts/check-registry.sh
python3 scripts/test-engine-integration.py
python3 scripts/benchmark.py
python3 scripts/darwin-quick-score.py all
```

**硬性要求**：

- `check-registry.sh`：0 错误、0 警告
- `test-engine-integration.py`：全部通过
- `benchmark.py`：全部性能目标通过
- `darwin-quick-score.py all`：每位专家 ≥85，全量平均 ≥86

---

## 审查清单

提交新专家或修改专家时，请确认：

- [ ] `id` 全局唯一，使用 kebab-case
- [ ] `name` 与显示名一致
- [ ] `pack` 符合分配规则
- [ ] `core_domain`、`style`、`topic_tags` 非空且互不重复
- [ ] `sensitivity` 正确标记
- [ ] 文件路径与 `expert-registry.json` 一致
- [ ] `SKILL.md` 以 `---` frontmatter 开头和结尾
- [ ] 包含明确的 Step 1/2/3 工作流
- [ ] 至少 1 个 CHECKPOINT
- [ ] 失败模式表包含 if-then 分支（如「如果…失败/异常」）
- [ ] 反例黑名单表格完整
- [ ] 无无意义的 AI 软化措辞堆砌
- [ ] Darwin 评分 ≥85

---

## 脚本工具

| 脚本 | 用途 |
|------|------|
| `scripts/check-registry.sh` | 校验 registry JSON 和文件路径 |
| `scripts/test-engine-integration.py` | 测试 Query API 与 Engine 集成 |
| `scripts/benchmark.py` | 性能基准测试 |
| `scripts/darwin-quick-score.py all` | 全量 Darwin 快速评分 |
| `scripts/darwin-quick-score.py <path>` | 单个专家评分 |

---

## 版本号规则

- 新增专家：对应 `version: 1.0.0`
- 小修小补（错别字、格式）：patch +1，如 `1.0.1`
- 结构性优化（新增工作流、失败模式）：minor +1，如 `1.1.0`
- 重大重构或 pack 调整：major +1，如 `2.0.0`
