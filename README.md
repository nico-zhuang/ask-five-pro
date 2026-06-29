# Ask Five Pro · 开箱即用的专家议会系统

**版本：v2.0.0**

Ask Five Pro 是 Ask Five 的下一代版本，把议会引擎和官方专家库打包在一起，安装后即可直接使用。

## 与 Ask Five Engine 的区别

| 维度 | Ask Five Pro | Ask Five Engine |
|---|---|---|
| 定位 | 开箱即用套件 | 可插拔引擎 |
| 内置专家 | 34 位 | 0 位 |
| 依赖 | 无 | 需安装 brain-crew |
| 适用 | 普通用户、快速上手 | 高级用户、二次开发 |
| 体积 | 较大 | 轻量 |

## 安装

### HanaAgent

```bash
install_skill ask-five-pro
```

### Codex

```bash
codex skill install ask-five-pro
```

## 使用

安装后直接对 Agent 说：

```
专家团开会，帮我评估一下这个方案。
```

或指定模式：

```
叫专家团来吵一架，议题是：我们该不该 all-in 短视频矩阵？
```

## 议会模式

- 共识模式（默认）
- 对抗模式
- 红队模式
- 陪审团模式
- 预审模式
- 淬火模式

## 内置专家

本包内置 `brain-crew` 官方专家库，共 34 位专家，覆盖：

- 产品与战略（乔布斯、张一鸣、雷军、张小龙等）
- 投资与决策（巴菲特、芒格、段永平等）
- 工程与系统（Andrej Karpathy、Ilya、Rob Pike 等）
- 内容与增长（MrBeast、大卫·奥格威等）
- 风险与心理（塔勒布、弗洛伊德等）
- 东方智慧（孙子、王阳明、稻盛和夫等）

## 验证安装

```bash
bash ~/.hanako/skills/ask-five-pro/scripts/check-experts.sh
```

或 Codex 环境：

```bash
bash ~/.codex/skills/ask-five-pro/scripts/check-experts.sh
```

## 扩展

如果你想添加自定义专家，建议改用 `ask-five-engine` + `brain-crew` 拆分版，按照 engine 的 registry 机制注册新专家。

## 版本历史

- **v2.0.0**（2026-06-29）：完全重构，引擎 + 专家库整合为开箱即用套件
