---
id: ask-five-pro
name: ask-five-pro
displayName: Ask Five Pro
version: 2.0.0
category: 04_workflow-automation
owner: NicoZhuang
author: NicoZhuang
status: testing
purpose: 开箱即用的专家议会系统，内置 34 位跨领域专家，支持共识/对抗/红队/陪审团等多种议会模式。
triggers:
- Ask Five
- ask five
- 专家团开会
- 叫专家团
- panel
- expert panel
- 大事商量
- 开个会
- 让他们吵一架
- 红队
- 找问题
- 陪审团
- 淬火
lastUpdated: '2026-06-29'
projects:
- xmade
platforms:
- hana
- codex
tags:
- skill
- ask-five
- expert-panel
- decision-support
- workflow
changelog:
- version: 2.0.0
  date: '2026-06-29'
  changes:
  - 完全重构，从固定 25 位专家升级为可插拔 34 位专家 + 议会引擎
  - 内置 brain-crew 专家库，安装后无需额外依赖
  - 支持共识/对抗/红队/陪审团/预审/淬火六种议会模式
---

> ⚠️ **本包已内置 `brain-crew` 专家库，无需额外安装依赖。** 安装后即可直接使用。
>
> 如果你需要更轻量、可自定义的引擎，请使用 `ask-five-engine` + `brain-crew` 拆分版。

# Ask Five Pro · 开箱即用的专家议会系统

> 不是专家的集合，而是让专家高效协作的机制。

Ask Five Pro 是 Ask Five 的下一代版本，整合了议会引擎与官方专家库：

- **34 位专家**：覆盖产品、战略、投资、工程、内容、风险、心理等领域
- **6 种议会模式**：共识 / 对抗 / 红队 / 陪审团 / 预审 / 淬火
- **开箱即用**：安装后无需配置，直接说「专家团开会」即可调用
- **可扩展**：如需添加自定义专家，参考 `ask-five-engine` 的 registry 机制

## 触发词

- 「Ask Five」「ask five」「专家团开会」「叫专家团」
- 「panel」「expert panel」「大事商量」「开个会」
- 「让他们吵一架」「红队」「找问题」「陪审团」「淬火」

## 安装

```bash
# HanaAgent
install_skill ask-five-pro

# Codex
codex skill install ask-five-pro
```

安装后即可使用，无需额外安装 `brain-crew`。

## 使用示例

```
我想做一个面向年轻人的智能硬件品牌，但团队内部有人主张先做大单品冲量，有人主张先做精品慢慢打磨。叫专家团来开个会。
```

## 核心原则

- 不替代决策，只提供多元视角
- 每次会议不超过 5 人
- 必须指出分歧和盲区

## 议会模式

| 模式 | 触发词 | 机制 |
|---|---|---|
| **共识模式（默认）** | 无 | 选派视角互补的专家，快速对齐方向 |
| **对抗模式** | 「对抗」「让他们吵一架」 | 故意选派立场对立的专家，突出张力 |
| **红队模式** | 「红队」「找问题」「挑刺」 | 选派风险、逆向、批判型专家，专门找方案漏洞 |
| **陪审团模式** | 「陪审团」「投票」 | 专家针对一个决策投票，输出多数意见 + 少数意见 |
| **预审模式** | 「预审」「先想怎么失败」 | 所有专家从「这个决策怎么一定会失败」出发 |
| **淬火模式** | 「淬火」「严格一点」「再挑挑刺」 | 两场会议 + 一次综合，输出带置信度的最终结论 |

## 专家来源

本包内置 `brain-crew` 官方专家库。专家元数据存储在 `references/expert-registry.json`，专家 SKILL.md 位于 `brain-crew/packs/<pack>/<expert>/`。

## 验证

```bash
bash scripts/check-experts.sh
```

正常输出：

```json
{"installed":[...],"simulated":[],"warnings":[]}
```

## 与 Ask Five Engine 的关系

- `ask-five-pro` = `ask-five-engine` + `brain-crew`，开箱即用
- `ask-five-engine` = 纯引擎，需要搭配专家包使用
- `brain-crew` = 官方专家包，可被多个引擎复用

如果你需要自定义专家组合或二次开发，建议使用拆分版。

## 版本历史

- **v2.0.0**（2026-06-29）：完全重构，从固定 25 位专家升级为可插拔 34 位专家 + 议会引擎
