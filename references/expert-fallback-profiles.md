# 专家 Fallback 画像

当 registry 中的某个 expert skill 未安装或无法读取时，Ask Five Engine 使用通用 fallback 机制模拟该专家视角。

## 通用 Fallback 规则

1. 在专家发言末尾标注：「（该专家 skill 未安装，以上为通用画像模拟）」
2. 基于该专家的 `core_domain` 和 `style` 字段，推断其可能持有的立场
3. 不使用具体的心智模型名称，除非你能从公开信息中合理推断
4. 保持简短，不编造无法验证的细节

## 示例

如果 registry 中注册了：

```json
{
  "id": "steve-jobs-perspective",
  "name": "乔布斯",
  "core_domain": ["产品", "设计", "战略", "聚焦"],
  "style": ["聚焦", "端到端控制", "极简"]
}
```

但对应的 SKILL.md 未安装，则 fallback 输出应体现：
- 对产品体验的极端重视
- 对功能和选择的减法倾向
- 对端到端控制的关注

## 注意事项

- Fallback 画像质量远低于真实 expert skill
- 应尽量安装真实的 expert skill
- 敏感角色（如政治人物）即使 fallback 也必须标注「仅作分析工具」
