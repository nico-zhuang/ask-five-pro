#!/bin/bash
# Ask Five Engine · Expert Skill 验证脚本
# 用法：bash scripts/validate-expert.sh <expert-skill-dir>
# 输出：检查结果，最后以 JSON 汇总

set -e

EXPERT_DIR="${1:-}"
if [ -z "$EXPERT_DIR" ]; then
  echo "用法：bash scripts/validate-expert.sh <expert-skill-dir>"
  exit 1
fi

if [ ! -d "$EXPERT_DIR" ]; then
  echo "错误：目录不存在 $EXPERT_DIR"
  exit 1
fi

SKILL_FILE="$EXPERT_DIR/SKILL.md"
if [ ! -f "$SKILL_FILE" ]; then
  echo "错误：$SKILL_FILE 不存在"
  exit 1
fi

python3 - <<PY
import re, sys, json, os

skill_file = '$SKILL_FILE'
expert_dir = '$EXPERT_DIR'
errors = []
warnings = []

with open(skill_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 frontmatter
fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
if not fm_match:
    errors.append("缺少 frontmatter")
    print(json.dumps({"valid": False, "errors": errors, "warnings": warnings}, ensure_ascii=False))
    sys.exit(0)

import yaml
try:
    fm = yaml.safe_load(fm_match.group(1))
except Exception as e:
    errors.append(f"frontmatter YAML 解析失败: {e}")
    print(json.dumps({"valid": False, "errors": errors, "warnings": warnings}, ensure_ascii=False))
    sys.exit(0)

required_fields = {
    'name': str,
    'description': str,
    'core_domain': list,
    'topic_tags': list,
    'style': list,
    'sensitivity': str,
    'version': str,
    'default-enabled': bool,
}

for field, expected_type in required_fields.items():
    if field not in fm:
        errors.append(f"缺少必需字段: {field}")
        continue
    if not isinstance(fm[field], expected_type):
        errors.append(f"字段 {field} 类型错误，期望 {expected_type.__name__}，实际 {type(fm[field]).__name__}")

# id 与目录名一致
expert_id = os.path.basename(os.path.normpath(expert_dir))
if fm.get('name') != expert_id:
    errors.append(f"frontmatter name ({fm.get('name')}) 与目录名 ({expert_id}) 不一致")

# 数组字段约束
for field in ['core_domain', 'topic_tags', 'style']:
    if field in fm and isinstance(fm[field], list):
        if len(fm[field]) == 0:
            errors.append(f"{field} 不能为空")
        if len(fm[field]) != len(set(fm[field])):
            errors.append(f"{field} 包含重复值")

# sensitivity 取值
if 'sensitivity' in fm and fm['sensitivity'] not in ['normal', 'sensitive']:
    errors.append(f"sensitivity 必须是 normal 或 sensitive，当前: {fm['sensitivity']}")

# description 长度
desc = fm.get('description', '')
if len(desc) > 1024:
    errors.append(f"description 超过 1024 字符，当前 {len(desc)}")

# 禁止空话尾巴
for phrase in ['灵活应用', '根据情况判断', '视情况而定']:
    if phrase in desc:
        warnings.append(f"description 可能包含空话: {phrase}")

# 检查正文章节
body = content[fm_match.end():]
required_sections = ['身份卡', '心智模型', '决策启发式', '表达风格', '边界声明']
for section in required_sections:
    if f'## {section}' not in body:
        errors.append(f"正文缺少章节: {section}")

# 输出结果
valid = len(errors) == 0
result = {
    "valid": valid,
    "expert_id": expert_id,
    "path": skill_file,
    "errors": errors,
    "warnings": warnings,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
PY
