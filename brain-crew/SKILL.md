---
name: brain-crew
description: |
  Brain Crew 是 Ask Five 引擎的 Core Expert Pack，提供一组跨领域、已按统一契约格式化的专家 skill。
  当 ask-five-engine 需要为议题匹配专家时，读取本 skill 的 expert-registry.json 并按路径调用对应专家。
  触发词：Brain Crew、专家库、核心专家包、brain crew。
version: 1.0.0
default-enabled: false
---

# Brain Crew｜Ask Five 核心专家包

> 不是专家名人堂，而是引擎可调用的、已经格式化的专家实例集合。

## 角色定位

Brain Crew 是 Ask Five 2.0 架构中的**第一层专家包**：
- 它**不**做议题分析、选派逻辑、会议流程控制——那是 ask-five-engine 的事。
- 它**不**做专家目录管理、跨 pack 索引——那是 expert-registry.json 和 registry 机制的事。
- 它只负责一件事：**把一组经过筛选的核心专家，以统一格式打包好，让 engine 能按需调用。**

## 统一免责声明

Brain Crew 中的所有专家角色均基于公开言论、著作、访谈、决策记录和可验证事实提炼而成，是**思维框架与表达 DNA 的模拟**，不代表该人物本人观点，也不具备该人物的最新认知或私人信息。

- 每位专家 skill 的时间锚、能力圈和沉默主题已在各自文件中标注。
- 涉及最新事件时，以 skill 中规定的研究流程为准，不可凭训练记忆编造立场。
- 敏感角色（`sensitivity: sensitive`）默认不启用，仅在用户明确点名或对抗模式下调用。

## 目录结构

```
brain-crew/
├── SKILL.md                 # 本文件
├── expert-registry.json     # 专家注册表，engine 通过它发现专家
├── README.md                # 给人看的说明
├── packs/                   # 专家内容存储
│   ├── core/                # 核心专家包
│   ├── brand/               # 品牌/内容/传播专家
│   ├── tech/                # AI/工程/技术决策专家
│   ├── enterprise/          # 企业/组织/管理专家
│   └── meta/                # Skill / Agent 工程专家
└── scripts/                 # 查询模块与校验工具
    ├── brain_crew_query.py      # 核心查询 API
    ├── check-registry.sh        # registry 校验
    ├── darwin-quick-score.py    # 快速评分
    ├── test-engine-integration.py # 集成测试
    └── benchmark.py             # 性能基准测试
```

## 核心规则

### 1. 调用契约

ask-five-engine 与 Brain Crew 的交互通过 `scripts/brain_crew_query.py` 提供的 Query API 完成：

1. engine 根据议题分析出 `categories`（主类别）和 `tags`（关键词）。
2. engine 调用 `query_experts()` 或 `query_panels()`，**只读取 registry 元数据**，不读取 SKILL.md。
3. engine 对选中的专家调用 `load_expert_content()`，**延迟加载**其 SKILL.md。

**核心原则**：
- 查询阶段只读 registry/索引，不读 expert SKILL.md 正文。
- 支持批量查询（`query_panels`），满足 Turbo 模式需求。
- 只有被选中的专家，才读取其 SKILL.md。

### 2. Core Pack 边界

Core Pack 固定为 **5-8 人**，当前为 6 人：

| 专家 | 核心领域 | 覆盖议题 |
|---|---|---|
| 史蒂夫·乔布斯 | 产品、设计、战略 | 产品战略、功能取舍、用户体验、品牌表达 |
| 张一鸣 | 系统、组织、产品 | 系统设计、组织管理、信息分发、全球化 |
| 查理·芒格 | 决策、投资、风控 | 投资决策、认知偏误、风险控制、跨学科 |
| Paul Graham | 创业、产品、写作 | 初创判断、产品早期、写作表达、人生选择 |
| 理查德·费曼 | 学习、验证、解释 | 概念验证、反自欺、第一性原理、教学表达 |
| 埃隆·马斯克 | 工程、成本、迭代 | 成本拆解、垂直整合、快速迭代、工程决策 |

Core Pack 的专家必须满足：
- 跨领域调用频率高
- 与 pack 内其他专家视角互补
- 不与其他 pack 的专职角色过度重叠

### 3. 专家 SKILL.md 规范

每个专家文件必须在顶部包含统一 frontmatter：

```yaml
---
id: steve-jobs                 # 机器标识，与 registry 中一致
name: 史蒂夫·乔布斯             # 给人看的名字
pack: core                     # 所属 pack
core_domain: ["产品", "设计", "战略"]
style: ["聚焦", "极简", "端到端控制"]
topic_tags: ["产品战略", "功能取舍", "用户体验", "品牌表达"]
sensitivity: normal            # normal / sensitive
version: 1.0.0
---
```

**强制规则**：
- `description` 在 SKILL.md 中必须包含"做什么 + 何时用 + 触发词"，≤1024 字符。
- `core_domain` 和 `style` 元素各不超过 3 个。
- `sensitivity` 必填。
- 禁止用"灵活应用/视情况而定/根据情况判断"等空话结尾。

### 4. 敏感角色处理

以下专家标记为 `sensitivity: sensitive`：
- `donald-trump`
- `zhang-xuefeng`

engine 默认不调用 sensitive 专家，仅在以下情况启用：
- 用户明确点名
- 用户开启"对抗模式"或要求"观点冲突"
- 议题明确涉及谈判、博弈、权力、舆论操控等场景

### 5. 新增专家流程

向 Brain Crew 新增专家必须：

1. 在 `packs/<pack>/` 下创建 `<expert-dir>/` 目录。
2. 编写 `SKILL.md`，顶部 frontmatter 符合本规范。
3. 在 `expert-registry.json` 中添加对应条目。
4. 运行 `scripts/check-registry.sh` 校验 registry 与文件路径一致性（待实现）。
5. 对 core pack 专家，目标达尔文评分 ≥80。

## 查询机制

### Query API

brain-crew 通过 `scripts/brain_crew_query.py` 暴露三个核心 API：

#### `query_experts()`

```python
query_experts(
    categories: List[str],      # 议题主类别，如 ["战略", "风险"]
    tags: List[str],            # 议题关键词，如 ["市场进入", "东南亚"]
    styles: List[str],          # 偏好风格（可选）
    mode: str,                  # 议会模式
    limit: int = 5,             # 最多返回几个
    exclude: List[str] = None,  # 排除某些专家 id
    metadata_only: bool = True  # 只返回元数据，不加载 SKILL.md
) -> List[ExpertMeta]
```

用于单议题专家匹配。返回按分数排序的专家元数据列表，包含 `score` 和 `reason`。

#### `query_panels()`

```python
query_panels(
    sub_topics: List[SubTopic],  # 多个子议题
    mode: str = "consensus",
    max_per_panel: int = 5,
    ensure_diversity: bool = True
) -> List[Panel]
```

Turbo 模式核心接口。一次查询多个子议题的专家组合，避免 engine 循环调用 `query_experts()` 带来的重复解析开销。

#### `load_expert_content()`

```python
load_expert_content(expert_id: str) -> str
```

延迟加载指定专家的 SKILL.md。结果可缓存，同一次 Turbo 中重复读取直接命中缓存。

### 匹配算法

默认打分公式：

```
score = domain_score * 3 + tag_score * 2 + style_score * 1 + bonus - penalty
```

- `domain_score`：专家 `core_domain` 与议题类别重叠度
- `tag_score`：专家 `topic_tags` 与议题关键词重叠度
- `style_score`：专家 `style` 与当前议会模式偏好风格匹配度
- 同质化 penalty：已选专家与候选专家 `core_domain` 重叠 > 50% 时，-0.2
- 敏感角色：默认强惩罚，仅在对抗模式或用户点名时启用

### 性能要求

| 场景 | 目标响应时间 | 当前实测 |
|---|---|---|
| 单次 `query_experts` | < 100ms | ~0.05ms |
| 单次 `query_panels`（5 个子议题） | < 300ms | ~0.15ms |
| `load_expert_content` | < 50ms | ~0.5ms |
| Turbo 模式全流程查询 | < 1s | ~5ms |

### Registry 路径解析

`load_expert_content()` 支持三种 path 格式：

1. **占位符路径**：`<runtime-skills-dir>/steve-jobs-perspective/SKILL.md`
   - 解析为 `~/.hanako/skills/steve-jobs-perspective/SKILL.md`
   - 可通过 `RUNTIME_SKILLS_DIR` 环境变量覆盖
2. **相对路径**：`packs/core/steve-jobs-perspective/SKILL.md`
   - 解析为相对于 registry 文件所在目录的路径
3. **绝对路径**：直接读取

可通过 `BRAIN_CREW_REGISTRY` 环境变量指定自定义 registry 路径。

## 失败模式与 Fallback

| 失败场景 | 应对措施 |
|---|---|
| registry 中 path 指向不存在的文件 | `load_expert_content()` 返回空字符串；engine 跳过该专家，记录日志 |
| 专家 SKILL.md 缺少 frontmatter | `check-registry.sh` 校验阶段报错；运行时跳过该专家 |
| sensitive 专家被默认调用 | `query_experts()` 默认排除 sensitive 专家，除非 mode="debate" 或用户点名 |
| core pack 专家不足 5 个 | engine 从 brand/tech 等 official pack 中补充匹配专家 |
| 多个 pack 含同名专家 | registry 中 id 必须唯一，pack 名作为命名空间 |
| Turbo 模式重复读取 SKILL.md | `load_expert_content()` 内置缓存，同一次调用只读一次磁盘 |

## 反模式（不要做）

- 不要把 Brain Crew 变成第二个 ask-five-engine。
- 不要在一个 pack 里放两个视角高度重叠的专家（如 core 里同时放 Munger 和 Buffett）。
- 不要把版本号写进文件夹名。
- 不要让 engine 硬编码任何专家身份或 pack 名称。
- 不要在 frontmatter 里堆砌标签，标签必须可被 engine 用于匹配。

## 与 Ask Five Engine 的关系

```
ask-five-engine
      ↓ 调用 query_experts() / query_panels()
brain-crew Query API
      ↓ 读取 registry 元数据（内存索引）
expert-registry.json
      ↓ 选中后调用 load_expert_content()
brain-crew/packs/<pack>/<expert>/SKILL.md
      ↓ 调用
专家视角输出
```

Brain Crew 是 engine 的**依赖包**，不是 engine 的**子模块**。engine 不直接读取 registry 或 SKILL.md，而是通过 brain-crew 提供的 Query API 访问。

### 环境变量

| 环境变量 | 作用 | 默认值 |
|---|---|---|
| `BRAIN_CREW_REGISTRY` | 指定 registry 文件路径 | `~/.hanako/skills/brain-crew/expert-registry.json` |
| `RUNTIME_SKILLS_DIR` | 解析 `<runtime-skills-dir>` 占位符 | `~/.hanako/skills` |

## 后续迭代方向

1. ✅ 实现 `scripts/brain_crew_query.py` Query API（query_experts / query_panels / load_expert_content）。
2. ✅ 实现 `scripts/check-registry.sh` 自动校验。
3. ✅ 实现 `scripts/benchmark.py` 性能基准测试。
4. 与 Ask Five Engine Turbo 模式联调。
5. 根据真实用户反馈优化匹配权重。
6. 拆出独立的 `brand-crew`、`tech-crew`、`enterprise-crew`、`meta-crew` skill（可选）。
7. 支持企业用户的 private-crew 通过私有 registry 接入。
