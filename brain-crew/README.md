# Brain Crew｜Ask Five 核心专家包

- Folder Name: `brain-crew`
- Category: `05_thinking-tools`
- Version: `v1.0.0`
- Owner: `XMADE`
- Status: `testing`
- Last Updated: `2026-06-28`
- Purpose: 为 Ask Five 引擎提供一组跨领域、已按统一契约格式化的专家 skill。

---

## 一句话定义

Brain Crew 不是专家名人堂，而是 Ask Five 引擎的**核心专家包**——它把一组经过筛选的专家，以统一格式打包好，让引擎能根据议题按需调用。

---

## 包含哪些专家

Brain Crew 目前包含 **30 位专家**，分为 5 个 pack：

### Core Pack（6 人）

默认启用，覆盖大多数常见议题：

| 专家 | 核心领域 | 典型议题 |
|---|---|---|
| 史蒂夫·乔布斯 | 产品、设计、战略 | 产品战略、功能取舍、用户体验 |
| 张一鸣 | 系统、组织、产品 | 系统设计、组织管理、信息分发 |
| 查理·芒格 | 决策、投资、风控 | 投资决策、认知偏误、风险控制 |
| Paul Graham | 创业、产品、写作 | 初创判断、产品早期、写作表达 |
| 理查德·费曼 | 学习、验证、解释 | 概念验证、反自欺、第一性原理 |
| 埃隆·马斯克 | 工程、成本、迭代 | 成本拆解、垂直整合、快速迭代 |

### Brand Crew（7 人）

品牌、内容、传播类议题：

MrBeast、大卫·奥格威、BBDO GWTB 策略官、鲁迅、郭德纲、X 导师、Naval Ravikant

### Tech Crew（4 人）

AI、工程、技术决策、平台战略类议题：

Andrej Karpathy、Ilya Sutskever、Rob Pike、黄仁勋

### Enterprise Crew（10 人）

企业、组织、管理、投资、东方哲学类议题：

沃伦·巴菲特、弗洛伊德、求是、纳西姆·塔勒布、唐纳德·特朗普（sensitive）、张雪峰（sensitive）、杰夫·贝佐斯、稻盛和夫、王阳明、段永平

### Meta Crew（3 人）

Skill / Agent 工程类议题：

达尔文 Skill、花叔蜂群、花叔女娲

---

## 目录结构

```
brain-crew/
├── SKILL.md                 # 给 Agent 看的执行规则
├── README.md                # 本文件
├── expert-registry.json     # 专家注册表（元数据索引）
├── packs/                   # 专家 SKILL.md 内容存储
│   ├── core/                # 核心专家包
│   ├── brand/               # 品牌/内容/传播
│   ├── tech/                # AI/工程/技术
│   ├── enterprise/          # 企业/组织/管理
│   └── meta/                # Skill / Agent 工程
└── scripts/                 # 工具脚本
    ├── brain_crew_query.py      # 查询 API
    ├── check-registry.sh        # registry 校验
    ├── darwin-quick-score.py    # 快速评分
    ├── test-engine-integration.py # 集成测试
    └── benchmark.py             # 性能基准测试
```

---

## 与 Ask Five Engine 的关系

```
ask-five-engine
      ↓ 调用 query_experts() / query_panels()
brain-crew Query API
      ↓ 读取 registry 元数据（内存索引）
expert-registry.json
      ↓ 选中后调用 load_expert_content()
packs/<pack>/<expert>/SKILL.md
      ↓ 调用
专家视角输出
```

引擎不直接读取 registry 或 SKILL.md，而是通过 brain-crew 提供的 Query API 访问。这是 Turbo 模式的前置条件：查询只读元数据，只有被选中的专家才加载 SKILL.md。

---

## 专家 frontmatter 规范

每个专家 `SKILL.md` 顶部必须包含：

```yaml
---
id: steve-jobs
name: 史蒂夫·乔布斯
pack: core
core_domain: ["产品", "设计", "战略"]
style: ["聚焦", "极简", "端到端控制"]
topic_tags: ["产品战略", "功能取舍", "用户体验", "品牌表达"]
sensitivity: normal
version: 1.0.0
---
```

字段说明：
- `id`：机器标识，全局唯一。
- `name`：显示名。
- `pack`：所属 pack（core/brand/tech/enterprise/meta）。
- `core_domain`：核心领域，≤3 个。
- `style`：风格标签，≤3 个。
- `topic_tags`：具体话题标签，用于 engine 匹配。
- `sensitivity`：`normal` 或 `sensitive`。
- `version`：语义化版本。

---

## 如何使用

### 作为 Ask Five 用户

你不需要单独安装 Brain Crew。安装 Ask Five 引擎时，它会自动读取本包。

触发 Ask Five 后，引擎会根据你的议题，从 Brain Crew 中选派 3-5 位专家发言。

### 作为开发者

如果你想修改某个专家：

1. 编辑 `packs/<pack>/<expert>/SKILL.md`。
2. 同步更新 `expert-registry.json` 中对应条目。
3. 运行 `scripts/check-registry.sh` 校验一致性。

如果你想新增专家：

1. 在对应 pack 下新建目录。
2. 编写 `SKILL.md`，顶部 frontmatter 符合规范。
3. 在 `expert-registry.json` 中添加条目。
4. 运行校验脚本。

---

## 查询 API

brain-crew 提供 Python 查询模块 `scripts/brain_crew_query.py`：

```python
import brain_crew_query as bcq

# 单议题匹配（只读 registry，不读 SKILL.md）
experts = bcq.query_experts(
    categories=["产品", "战略"],
    tags=["用户体验", "聚焦"],
    mode="consensus",
    limit=3
)

# Turbo 模式：批量查询多个子议题
panels = bcq.query_panels(
    sub_topics=[
        {"id": "t1", "title": "产品战略", "categories": ["产品"], "tags": ["用户体验"]},
        {"id": "t2", "title": "投资决策", "categories": ["投资"], "tags": ["价值投资"]},
    ],
    mode="turbo",
    max_per_panel=3
)

# 延迟加载：只有选中后才读取 SKILL.md
content = bcq.load_expert_content("steve-jobs")
```

性能实测（30 位专家）：
- `query_experts`：~0.05ms
- `query_panels`（5 子议题）：~0.15ms
- `load_expert_content`：~0.5ms
- Turbo 全流程：~5ms

## 校验脚本

```bash
bash scripts/check-registry.sh
```

会检查：
- `expert-registry.json` 是否为合法 JSON。
- 每个 registry 条目的 `path` 是否对应真实文件。
- 必填字段是否齐全（id/name/pack/path/core_domain/style/topic_tags/sensitivity/version）。
- `id` 是否全局唯一。
- sensitive 专家是否被正确标记。
- frontmatter 字段是否与 registry 一致。

---

## 敏感角色说明

以下专家默认不被 Ask Five 调用，仅在用户明确点名或开启对抗模式时启用：

- 唐纳德·特朗普
- 张雪峰

这些角色仅作为分析工具使用，不替代价值观判断。

---

## 状态

当前为 `testing` 状态。

已完成：
- 30 位专家 frontmatter 统一
- Query API 实现（query_experts / query_panels / load_expert_content）
- registry 校验脚本
- 集成测试与性能基准测试

待完成：
- 与 Ask Five Engine Turbo 模式联调
- 根据真实反馈优化匹配权重

---

## 后续计划

- [ ] 与 ask-five-engine 完成联调
- [ ] 对 core pack 6 位专家跑达尔文评分
- [ ] 根据实测反馈调整 registry tag 体系
- [ ] 拆出独立的 brand-crew / tech-crew / enterprise-crew / meta-crew skill（可选）
