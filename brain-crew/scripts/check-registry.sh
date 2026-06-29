#!/usr/bin/env bash
# check-registry.sh
# 校验 brain-crew 的 expert-registry.json 与 packs/ 下实际文件的一致性

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REGISTRY="$PROJECT_DIR/expert-registry.json"
PACKS_DIR="$PROJECT_DIR/packs"

ERRORS=0
WARNINGS=0

log_info() { echo "[INFO] $1"; }
log_ok() { echo "[OK] $1"; }
log_warn() { echo "[WARN] $1"; ((WARNINGS++)) || true; }
log_error() { echo "[ERROR] $1"; ((ERRORS++)) || true; }

echo "======================================"
echo "Brain Crew Registry Checker"
echo "======================================"
echo ""

# 1. 检查 registry 文件存在
if [[ ! -f "$REGISTRY" ]]; then
    log_error "registry 文件不存在: $REGISTRY"
    exit 1
fi
log_ok "registry 文件存在"

# 2. 检查 JSON 合法性
if ! python3 -c "import json; json.load(open('$REGISTRY'))" 2>/dev/null; then
    log_error "registry 不是合法 JSON"
    exit 1
fi
log_ok "registry 是合法 JSON"

# 3. Python 校验主逻辑
python3 << 'PYEOF'
import json
import os
import re
import sys

registry_path = os.environ.get('REGISTRY', 'expert-registry.json')
packs_dir = os.environ.get('PACKS_DIR', 'packs')
errors = 0
warnings = 0

def log_error(msg):
    global errors
    errors += 1
    print(f"[ERROR] {msg}")

def log_warn(msg):
    global warnings
    warnings += 1
    print(f"[WARN] {msg}")

def log_ok(msg):
    print(f"[OK] {msg}")

with open(registry_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

required_top_fields = {'schema_version', 'registry_description', 'experts'}
missing_top = required_top_fields - set(data.keys())
if missing_top:
    log_error(f"registry 缺少顶层字段: {missing_top}")

experts = data.get('experts', [])
if not experts:
    log_error("registry 中 experts 数组为空")
    sys.exit(1)

log_ok(f"registry 包含 {len(experts)} 位专家")

required_fields = {'id', 'name', 'pack', 'path', 'core_domain', 'style', 'topic_tags', 'sensitivity', 'version'}
valid_packs = {'core', 'brand', 'tech', 'enterprise', 'meta'}
valid_sensitivity = {'normal', 'sensitive'}
ids_seen = set()

for idx, expert in enumerate(experts):
    prefix = f"experts[{idx}]"
    
    # 必填字段检查
    missing = required_fields - set(expert.keys())
    if missing:
        log_error(f"{prefix} 缺少字段: {missing}")
    
    eid = expert.get('id')
    if eid:
        if eid in ids_seen:
            log_error(f"id 重复: {eid}")
        ids_seen.add(eid)
    
    # pack 合法性
    pack = expert.get('pack')
    if pack and pack not in valid_packs:
        log_error(f"{prefix} pack 不合法: {pack}，必须是 {valid_packs}")
    
    # sensitivity 合法性
    sens = expert.get('sensitivity')
    if sens and sens not in valid_sensitivity:
        log_error(f"{prefix} sensitivity 不合法: {sens}，必须是 {valid_sensitivity}")
    
    # 数组字段检查
    for arr_field in ['core_domain', 'style', 'topic_tags']:
        val = expert.get(arr_field)
        if val is not None:
            if not isinstance(val, list):
                log_error(f"{prefix} {arr_field} 必须是数组")
            elif len(val) == 0:
                log_error(f"{prefix} {arr_field} 不能为空数组")
            elif arr_field in ['core_domain', 'style'] and len(val) > 3:
                log_warn(f"{prefix} {arr_field} 建议不超过 3 个，当前 {len(val)} 个")
    
    # path 检查
    path = expert.get('path')
    if path:
        if '<runtime-skills-dir>' in path:
            runtime_dir = os.environ.get('RUNTIME_SKILLS_DIR', os.path.expanduser('~/.hanako/skills'))
            full_path = path.replace('<runtime-skills-dir>', runtime_dir)
        else:
            full_path = os.path.join(os.path.dirname(registry_path), path)
        if not os.path.isfile(full_path):
            log_error(f"{prefix} path 指向文件不存在: {path}")
        else:
            # 检查 frontmatter 关键字段是否匹配
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                if not match:
                    log_error(f"{path} 缺少 frontmatter")
                else:
                    fm_text = match.group(1)
                    # 简单解析 YAML-like frontmatter
                    fm = {}
                    for line in fm_text.split('\n'):
                        if ':' in line and not line.strip().startswith('#'):
                            key, val = line.split(':', 1)
                            fm[key.strip()] = val.strip()
                    
                    if fm.get('id') != eid:
                        log_error(f"{path} frontmatter id ({fm.get('id')}) 与 registry id ({eid}) 不一致")
                    expected_dir_name = os.path.basename(os.path.dirname(full_path))
                    if fm.get('name') != expected_dir_name:
                        log_error(f"{path} frontmatter name ({fm.get('name')}) 与目录名 ({expected_dir_name}) 不一致")
                    if fm.get('pack') != pack:
                        log_error(f"{path} frontmatter pack ({fm.get('pack')}) 与 registry pack ({pack}) 不一致")
                    if fm.get('sensitivity') != sens:
                        log_error(f"{path} frontmatter sensitivity ({fm.get('sensitivity')}) 与 registry sensitivity ({sens}) 不一致")
            except Exception as e:
                log_error(f"{path} 读取失败: {e}")

# 检查 packs 目录下是否有未注册的专家
runtime_dir = os.environ.get('RUNTIME_SKILLS_DIR', os.path.expanduser('~/.hanako/skills'))
project_dir = os.path.dirname(registry_path)
def resolve_paths(p):
    paths = set()
    if '<runtime-skills-dir>' in p:
        paths.add(os.path.normpath(p.replace('<runtime-skills-dir>', runtime_dir)))
        # 同时加入本地项目路径，便于开发时校验
        rel = p.replace('<runtime-skills-dir>/', '')
        if rel.startswith('brain-crew/'):
            rel = rel[len('brain-crew/'):]
        paths.add(os.path.normpath(os.path.join(project_dir, rel)))
    else:
        paths.add(os.path.normpath(os.path.join(project_dir, p)))
    return paths
registered_paths = set()
for e in experts:
    if 'path' in e:
        registered_paths.update(resolve_paths(e['path']))
for root, dirs, files in os.walk(packs_dir):
    if 'SKILL.md' in files:
        skill_path = os.path.normpath(os.path.join(root, 'SKILL.md'))
        if skill_path not in registered_paths:
            rel_path = os.path.relpath(skill_path, os.path.dirname(registry_path))
            log_warn(f"未在 registry 中注册的专家文件: {rel_path}")

print("")
print(f"检查完成: {len(experts)} 位专家, {errors} 个错误, {warnings} 个警告")

if errors > 0:
    sys.exit(1)
PYEOF

exit "$ERRORS"
