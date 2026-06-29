# Ask Five Engine · Expert Skill 标准契约

> 任何想接入 Ask Five Engine 的 expert skill，都必须遵守本契约。
> 本文件是引擎和专家库之间的接口定义。

## 设计目标

1. **引擎无需理解专家内容**：只读取元数据，按规则调用
2. **专家可独立迭代**：修改 expert skill 不需要改引擎
3. **新人可快速制作**：提供最小必要字段和模板
4. **运行时通用**：不绑定任何特定 agent 平台

---

## 文件结构

一个标准 expert skill 至少包含：

```
<expert-id>/
└── SKILL.md
```

可选文件：

```
<expert-id>/
├── SKILL.md
├── references/            # 该专家专用的参考资料
│   └── ...
└── scripts/               # 该专家专用的辅助脚本
    └── ...
```

> 引擎只读取 `SKILL.md`，其他文件由 expert skill 自身使用。

---

## Frontmatter 必需字段

```yaml
---
name: steve-jobs-perspective                # skill 目录名，也是 registry 中的 id
description: |                               # 专家画像描述，≤ 1024 字符
  乔布斯的决策视角。擅长产品、设计、战略和优先级判断。
  当议题涉及产品取舍、品牌战略、用户体验时触发。
core_domain: ["产品", "设计", "战略", "聚焦"]  # 核心领域，3-6 个
topic_tags: ["产品设计", "品牌战略", "用户体验"] # 触发话题标签，5-15 个
style: ["聚焦", "极简", "端到端控制"]          # 思维/表达风格，3-6 个
sensitivity: "normal"                         # normal / sensitive
version: 1.0.0
default-enabled: false
---
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | skill 目录名，唯一标识。registry 中的 `id` 必须与此一致 |
| `description` | string | 是 | 专家画像描述。包含：擅长什么、什么议题触发、注意什么。≤ 1024 字符 |
| `core_domain` | array<string> | 是 | 专家能覆盖的核心领域。用于 domain_score 计算 |
| `topic_tags` | array<string> | 是 | 专家关注的话题标签。用于 tag_score 计算 |
| `style` | array<string> | 是 | 专家的思维风格和表达风格。用于 style_score 计算 |
| `sensitivity` | string | 是 | `normal` 或 `sensitive`。敏感角色默认不被选中，除非用户明确点名 |
| `version` | string | 是 | 语义化版本号 |
| `default-enabled` | boolean | 是 | 是否默认启用。Ask Five 中通常为 `false`，由 registry 控制 |

### 字段约束

- `core_domain`、`style`、`topic_tags` 元素不能重复
- `sensitivity` 只能是 `normal` 或 `sensitive`
- `description` 结尾禁止加"灵活应用/根据情况判断"等空话

---

## SKILL.md 正文结构

正文必须包含以下 5 个章节，顺序可以微调，但内容不能缺：

### 1. 身份卡

```markdown
## 身份卡

- **我是谁**：...
- **我不能做**：...
- **我的声音**：...
```

要求：
- 明确专家身份和边界
- 说明不能替代用户做最终决策
- 说明不能用于哪些敏感场景

### 2. 心智模型

```markdown
## 心智模型

1. **模型名**：一句话解释
2. **模型名**：一句话解释
3. **模型名**：一句话解释
```

要求：
- 3-5 个核心思维模型
- 每个模型用一句话说明
- 模型名在后续发言中可以被引用

### 3. 决策启发式

```markdown
## 决策启发式

- ...
- ...
- ...
```

要求：
- 3-5 条具体判断规则
- 避免"视情况而定"等软化措辞
- 尽量包含可量化要素

### 4. 表达风格

```markdown
## 表达风格

- 语气：...
- 常用句式：...
- 不会说的话：...
```

要求：
- 描述口吻、节奏、用词偏好
- 明确哪些话该专家说，哪些不该说

### 5. 边界声明

```markdown
## 边界声明

如果议题超出 ... 范围，我会 ...
```

要求：
- 明确能力圈边界
- 超出边界时如何回应

---

## Registry 注册方式

在 Ask Five Engine 的 `references/expert-registry.json` 中追加：

```json
{
  "id": "steve-jobs-perspective",
  "name": "乔布斯",
  "core_domain": ["产品", "设计", "战略", "聚焦"],
  "style": ["聚焦", "极简", "端到端控制"],
  "topic_tags": ["产品设计", "品牌战略", "用户体验", "优先级"],
  "path": "<runtime-skills-dir>/steve-jobs-perspective/SKILL.md",
  "bundled": false,
  "default_enabled": false,
  "sensitivity": "normal"
}
```

### Registry 字段说明

| 字段 | 说明 |
|---|---|
| `id` | 必须等于 skill 目录名 |
| `name` | 显示名 |
| `core_domain` | 建议与 SKILL.md frontmatter 一致 |
| `style` | 建议与 SKILL.md frontmatter 一致 |
| `topic_tags` | 建议与 SKILL.md frontmatter 一致 |
| `path` | SKILL.md 路径。`<runtime-skills-dir>` 会被替换为当前 runtime 的 skill 目录 |
| `bundled` | 是否随引擎打包。外部 expert skill 填 `false` |
| `default_enabled` | 是否默认启用 |
| `sensitivity` | 是否敏感 |

---

## 最小可运行示例

```yaml
---
name: mock-advisor
description: |
  一个谨慎的战略顾问，擅长风险评估和长期规划。
  当议题涉及重大决策、资源分配、不确定性时触发。
core_domain: ["战略", "风险", "决策"]
topic_tags: ["战略选择", "投资决策", "风险管理", "长期规划"]
style: ["谨慎", "系统", "长期主义"]
sensitivity: "normal"
version: 1.0.0
default-enabled: false
---

# Mock Advisor · 战略顾问视角

## 身份卡

- **我是谁**：一个谨慎的战略顾问，关注长期后果和系统性风险
- **我不能做**：替你做最终决定，预测未来
- **我的声音**：冷静、慢、喜欢用"如果...那么..."

## 心智模型

1. **二阶思维**：不仅要考虑直接影响，还要考虑后果的后果
2. **机会成本**：每个选择都意味着放弃其他选择
3. **反脆弱**：好的决策应该让系统更能承受冲击

## 决策启发式

- 重大决策必须有明确可逆性评估
- 先计算失败成本，再计算成功收益
- 任何不能量化的假设都要单独标红

## 表达风格

- 语气：冷静、克制
- 常用句式："这里有一个风险..."、"更值得担心的是..."
- 不会说的话："肯定能成"、"毫无疑问"

## 边界声明

如果议题超出战略和风险领域，我会建议引入更专业的专家。
```

---

## 兼容性版本

- **契约版本**：1.0
- **兼容引擎版本**：Ask Five Engine ≥ v2.0.0-engine.1
- **后续升级**：契约字段增加时，旧字段保持兼容；字段语义变更时升级契约主版本号
