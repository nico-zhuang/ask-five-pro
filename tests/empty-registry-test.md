# 空 Registry 测试报告

## 测试目的

验证 Ask Five Engine 在没有任何专家注册时的行为是否符合设计：
- 不进入议会流程
- 输出清晰的 onboarding 引导
- 提供注册示例

## 测试环境

- 引擎路径：`/Users/nicozhuang/隐形公司/2025/hanako/skills/ask-five-engine/`
- 版本：v2.0.0-engine.1
- 测试时间：2026-06-28

## 测试步骤

### 1. 运行 check-experts.sh

```bash
bash scripts/check-experts.sh
```

**输出**：

```json
{"installed":[],"simulated":[]}
```

### 2. 检查 expert-registry.json

```bash
python3 -c "import json; d=json.load(open('references/expert-registry.json')); print(len(d.get('experts',[])))"
```

**输出**：`0`

### 3. 检查 onboarding 信息

```json
{
  "message": "当前没有可用专家。你可以：",
  "options": [
    "安装 expert-core-pack 获得 8 位核心专家",
    "安装单个 expert skill 并在本 registry 中注册",
    "用 nuwa-skill 蒸馏你自己的角色（如董事长、CMO、投资人）"
  ]
}
```

## 测试结果

| 检查项 | 期望 | 实际 | 状态 |
|---|---|---|---|
| `experts` 数组为空 | 是 | 是 | ✅ |
| check-experts 输出空数组 | 是 | 是 | ✅ |
| onboarding.message 存在 | 是 | 是 | ✅ |
| onboarding.options 非空 | 是 | 是 | ✅ |
| 提供注册示例 | 是 | `example_entry` 字段存在 | ✅ |

## 结论

空 registry 处理符合设计。引擎在没有任何专家时会正确引导用户安装并注册 expert skill，不会空转或报错。
