# Ask Five Pro · 开箱即用的专家议会系统

> 不是专家的集合，而是让专家高效协作的机制。

**版本：v2.0.0** | 状态：testing

Ask Five Pro 是 Ask Five 的下一代版本，把**议会引擎**和**官方专家库**打包在一起，安装后无需配置，直接说「专家团开会」即可调用。

---

## 快速开始

```bash
# HanaAgent（推荐）
install_skill github_url=https://github.com/nico-zhuang/ask-five-pro

# 或 Codex
codex skill install https://github.com/nico-zhuang/ask-five-pro
```

安装后直接使用：

```
叫专家团来开会，议题是：我们该不该 all-in 短视频矩阵？
```

---

## 整合包结构

Ask Five Pro 是一个**单包整合**设计，内部包含两个独立模块：

```
ask-five-pro/
├── SKILL.md                    # 整合包入口，声明依赖关系
├── README.md                   # 使用文档
├── brain-crew/                 # 内置专家库（34位专家）
│   ├── SKILL.md               # 专家库元数据和 Query API
│   ├── expert-registry.json   # 专家注册表
│   └── packs/                 # 按领域分组的专家 skill
│       ├── core/              # 产品与战略（乔布斯、张一鸣、Paul Graham 等）
│       ├── tech/              # 工程与系统（Andrej Karpathy、雷军、张小龙 等）
│       ├── brand/             # 内容与品牌（MrBeast、奥格威、Naval 等）
│       ├── enterprise/        # 投资与决策（巴菲特、芒格、塔勒布 等）
│       └── meta/              # 元与系统（达尔文、孙子、苏格拉底 等）
├── references/                 # 引擎注册表和参考文档
│   ├── expert-registry.json   # 指向 brain-crew 的本地注册表
│   ├── matching-algorithm.md  # 专家匹配算法说明
│   └── parliament-mode-templates.md  # 议会模式模板
├── scripts/                    # 引擎脚本
│   ├── check-experts.sh       # 专家可用性检查
│   └── match-experts.py       # 议题-专家匹配
└── tests/                      # 集成测试
```

### 为什么这样设计？

**`brain-crew` 是专家注册表的权威来源**，负责：
- 维护 `expert-registry.json`（34 位专家的元数据）
- 提供 `scripts/brain_crew_query.py`（Query API，供引擎调用）
- 管理专家的分类、标签、风格定义

**`ask-five-engine` 是议会引擎**，负责：
- 读取注册表，按议题匹配 3-5 位专家
- 组织议会发言（共识/对抗/红队/陪审团/预审/淬火）
- 输出结构化会议纪要

**`ask-five-pro` 把两者打包在一起**，因为：
- 大多数用户不需要知道引擎和专家库的区别
- 开箱即用，避免「先装 engine 后装 brain-crew」的依赖提醒问题
- 版本统一管理，升级时不会两边不同步

---

## 与 Ask Five Engine 的区别

| 维度 | Ask Five Pro | Ask Five Engine |
|------|------|------|
| **定位** | 开箱即用套件 | 可插拔引擎 |
| **内置专家** | 34 位 | 0 位 |
| **依赖** | 无（已内置） | 需安装 brain-crew |
| **体积** | 较大（含全部专家） | 轻量（仅引擎） |
| **适用场景** | 普通用户，快速上手 | 高级用户，二次开发 |
| **安装方式** | `install_skill github_url=...` | `install_skill github_url=...` + `install_skill brain-crew` |

**建议**：
- 如果你只是想要「叫专家团来开会」→ 用 **Ask Five Pro**
- 如果你需要自定义专家组合、替换 brain-crew 为其他专家包 → 用 **Ask Five Engine + brain-crew**

---

## 6 种议会模式

| 模式 | 触发词 | 机制 |
|------|--------|------|
| **共识模式（默认）** | 无 | 选派视角互补的专家，快速对齐方向 |
| **对抗模式** | 「对抗」「让他们吵一架」 | 故意选派立场对立的专家，突出张力 |
| **红队模式** | 「红队」「找问题」「挑刺」 | 选派风险、逆向、批判型专家，专门找方案漏洞 |
| **陪审团模式** | 「陪审团」「投票」 | 专家针对一个决策投票，输出多数意见 + 少数意见 |
| **预审模式** | 「预审」「先想怎么失败」 | 所有专家从「这个决策怎么一定会失败」出发 |
| **淬火模式** | 「淬火」「严格一点」 | 两场会议 + 一次综合，输出带置信度的最终结论 |

---

## 34 位内置专家

### 产品与战略
- **史蒂夫·乔布斯** — 聚焦、极简、端到端控制
- **张一鸣** — 系统、数据驱动、全局优化
- **雷军** — 产品、效率、生态
- **张小龙** — 用户体验、平台生态、克制

### 工程与系统
- **Andrej Karpathy** — AI、工程、教育
- **Ilya Sutskever** — AI、研究、安全
- **Rob Pike** — 工程、设计、简洁
- **黄仁勋** — 平台、生态、AI

### 内容与品牌
- **MrBeast** — 内容、增长、传播
- **大卫·奥格威** — 品牌、广告、社媒
- **Naval Ravikant** — 个人成长、财富、杠杆
- **X 导师** — 内容、个人 IP、社媒

### 投资与决策
- **沃伦·巴菲特** — 投资、企业、管理
- **查理·芒格** — 决策、投资、风控
- **段永平** — 投资、商业、决策
- **塔勒布** — 风险、不确定性、抗脆弱

### 东方智慧
- **孙子** — 战略、竞争、不确定性
- **王阳明** — 决策、心性、实践
- **稻盛和夫** — 经营、哲学、团队
- **苏格拉底** — 批判思维、认知谦逊

### 元与系统
- **达尔文 Skill** — 优化、评估、迭代
- **花叔蜂群** — 协作、系统、并行
- **花叔女娲** — 蒸馏、创造、造人

---

## 验证安装

```bash
bash ~/.hanako/skills/ask-five-pro/scripts/check-experts.sh
```

正常输出：
```json
{"installed":34,"simulated":0,"warnings":[]}
```

---

## 扩展：添加自定义专家

如果你需要添加自己的专家，建议改用 **Ask Five Engine + brain-crew 拆分版**，按以下步骤：

1. 安装 `ask-five-engine`（纯引擎）
2. 安装 `brain-crew`（专家库）
3. 在 `brain-crew/packs/` 下新建你的专家目录
4. 在 `brain-crew/expert-registry.json` 中注册新专家
5. 引擎会自动读取新注册表

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| **v2.0.0** | 2026-06-29 | 完全重构，引擎 + 专家库整合为开箱即用套件 |

---

## 相关仓库

- [ask-five-engine](https://github.com/nico-zhuang/ask-five-engine) — 纯议会引擎（可插拔专家）
- [brain-crew](https://github.com/nico-zhuang/brain-crew) — 官方专家库（可独立使用）

## 许可证

MIT
