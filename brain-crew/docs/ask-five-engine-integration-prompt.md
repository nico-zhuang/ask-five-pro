# Ask Five Engine × Brain Crew 联调启动提示词

## 目标

启动 Ask Five Engine 与 Brain Crew 的联调，验证 engine 能够正确读取 Brain Crew 的 expert registry、加载 expert SKILL.md、召开议会并输出会议纪要。

## Brain Crew 侧已就绪

- **30 位 expert skill** 全部通过 engine 的 `validate-expert.sh`
- Registry 路径已统一为 `<runtime-skills-dir>/brain-crew/packs/<pack>/<expert-dir>/SKILL.md`
- 提供 `query_experts()` / `query_panels()` / `load_expert_content()` 查询 API
- Darwin 快速评分：**平均 91.9/100，最低 86.6，全部 ≥85**

## 关键文件路径

| 文件 | 路径 |
|---|---|
| Brain Crew registry | `~/.hanako/skills/brain-crew/expert-registry.json` |
| Engine registry 副本 | `/Users/nicozhuang/隐形公司/2025/hanako/skills/ask-five-engine/references/expert-registry.json` |
| Expert skill 验证脚本 | `/Users/nicozhuang/隐形公司/2025/hanako/skills/ask-five-engine/scripts/validate-expert.sh` |
| 匹配算法验证脚本 | `/Users/nicozhuang/隐形公司/2025/hanako/skills/ask-five-engine/scripts/match-experts.py` |
| Brain Crew Query API | `/Users/nicozhuang/隐形公司/2025/hanako/skills/brain-crew/scripts/brain_crew_query.py` |

## 建议的首个联调用例

**议题**：我们要不要做短视频矩阵？

**期望流程**：
1. Engine 读取 Brain Crew registry
2. 匹配出内容/传播/增长领域的专家
3. 召开共识模式议会
4. 输出结构化会议纪要

## 请验证

1. Engine 能正确读取 `~/.hanako/skills/brain-crew/expert-registry.json`
2. Registry 中所有 expert 的 `path` 都能解析到真实 SKILL.md 文件
3. `match-experts.py` 能基于议题选出合理的 3-5 人 panel
4. 议会流程能正确调用每位专家的发言规则
5. 输出符合 Ask Five Engine 预期的会议纪要格式
6. 敏感角色（Trump、张雪峰）默认被排除，仅在 `debate` 或用户点名时出现

## 备注

- Brain Crew 采用 `packs/<pack>/<expert>/` 的分组结构，而非 flat `experts/`，registry 中的 `path` 已显式包含完整路径
- 部分 expert 的 `身份卡 / 心智模型 / 决策启发式 / 表达风格 / 边界声明` 章节为兼容性 placeholder，联调通过后会逐步重写为角色化内容
- 如需要 Brain Crew 侧配合调整，请直接列出具体字段或结构要求
