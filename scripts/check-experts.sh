#!/bin/bash
# Ask Five Pro · 专家可用性扫描脚本
# 本包已内置 brain-crew，扫描包内专家可用性
# 输出 JSON：{"installed": [...], "simulated": [...], "warnings": []}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/../SKILL.md" ]; then
  DEFAULT_ASK_FIVE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
elif [ -d "$HOME/.hanako/skills/ask-five-pro" ]; then
  DEFAULT_ASK_FIVE_DIR="$HOME/.hanako/skills/ask-five-pro"
elif [ -d "$HOME/.codex/skills/ask-five-pro" ]; then
  DEFAULT_ASK_FIVE_DIR="$HOME/.codex/skills/ask-five-pro"
else
  DEFAULT_ASK_FIVE_DIR="$HOME/.hanako/skills/ask-five-pro"
fi

ASK_FIVE_DIR="${1:-$DEFAULT_ASK_FIVE_DIR}"
# 将传入路径转为绝对路径，避免相对路径导致 system_skills_dir 计算错误
if [ -d "$ASK_FIVE_DIR" ]; then
  ASK_FIVE_DIR="$(cd "$ASK_FIVE_DIR" && pwd)"
fi
REGISTRY="$ASK_FIVE_DIR/references/expert-registry.json"

if [ -n "$ASK_FIVE_SKILLS_DIR" ]; then
  SYSTEM_SKILLS_DIR="$ASK_FIVE_SKILLS_DIR"
else
  SYSTEM_SKILLS_DIR="$(dirname "$ASK_FIVE_DIR")"
fi

warnings=()

# 1. 检查内置 brain-crew 是否存在
BUILT_IN_BRAIN_CREW="$ASK_FIVE_DIR/brain-crew"
BUILT_IN_BRAIN_CREW_REGISTRY="$BUILT_IN_BRAIN_CREW/expert-registry.json"
if [ ! -d "$BUILT_IN_BRAIN_CREW" ]; then
  warnings+=("brain-crew not bundled in $ASK_FIVE_DIR; this should not happen for ask-five-pro")
fi

# 2. 检查 engine registry 与内置 brain-crew registry 是否一致
if [ -f "$REGISTRY" ] && [ -f "$BUILT_IN_BRAIN_CREW_REGISTRY" ]; then
  diff_result=$(python3 - <<PY
import json
try:
    with open('$REGISTRY', 'r', encoding='utf-8') as f:
        engine = json.load(f)
    with open('$BUILT_IN_BRAIN_CREW_REGISTRY', 'r', encoding='utf-8') as f:
        brain = json.load(f)
    engine_ids = {e.get('id') for e in engine.get('experts', [])}
    brain_ids = {e.get('id') for e in brain.get('experts', [])}
    only_in_engine = sorted(engine_ids - brain_ids)
    only_in_brain = sorted(brain_ids - engine_ids)
    if only_in_engine or only_in_brain:
        msgs = []
        if only_in_engine:
            msgs.append(f"experts only in engine registry: {', '.join(only_in_engine)}")
        if only_in_brain:
            msgs.append(f"experts only in brain-crew registry: {', '.join(only_in_brain)}")
        print(' | '.join(msgs))
except Exception as ex:
    print(f'registry comparison error: {ex}')
PY
)
  if [ -n "$diff_result" ]; then
    warnings+=("registry mismatch: $diff_result")
  fi
elif [ ! -f "$REGISTRY" ]; then
  warnings+=("engine registry missing at $REGISTRY")
fi

installed=()
simulated=()

if [ -f "$REGISTRY" ]; then
  result=$(python3 - <<PY
import json, sys, os
registry_path = '$REGISTRY'
ask_five_dir = '$ASK_FIVE_DIR'
system_skills_dir = '$SYSTEM_SKILLS_DIR'
try:
    with open(registry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for e in data.get('experts', []):
        expert_id = e.get('id', '')
        path = e.get('path', '')
        bundled = e.get('bundled', False)
        found = False
        if path:
            resolved = path.replace('<runtime-skills-dir>', system_skills_dir)
            if not os.path.isabs(resolved):
                resolved = os.path.join(ask_five_dir, resolved)
            if os.path.exists(resolved):
                found = True
        if not found and bundled:
            bundled_dir = os.path.join(ask_five_dir, 'references', 'experts', expert_id)
            if os.path.isdir(bundled_dir):
                found = True
        if not found and not bundled:
            external_dir = os.path.join(system_skills_dir, expert_id)
            if os.path.isdir(external_dir):
                found = True
        print(f"{expert_id}\t{'installed' if found else 'simulated'}")
except Exception as ex:
    sys.stderr.write(f'registry error: {ex}\n')
PY
)
  while IFS=$'\t' read -r expert status; do
    if [ -n "$expert" ]; then
      if [ "$status" = "installed" ]; then
        installed+=("$expert")
      else
        simulated+=("$expert")
      fi
    fi
  done <<< "$result"
fi

printf '{"installed":['
first=1
for e in "${installed[@]}"; do
  if [ $first -eq 1 ]; then first=0; else printf ','; fi
  printf '"%s"' "$e"
done
printf '],"simulated":['
first=1
for e in "${simulated[@]}"; do
  if [ $first -eq 1 ]; then first=0; else printf ','; fi
  printf '"%s"' "$e"
done
printf '],"warnings":['
first=1
for w in "${warnings[@]}"; do
  if [ $first -eq 1 ]; then first=0; else printf ','; fi
  printf '"%s"' "$w"
done
printf ']}\n'
