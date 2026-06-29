#!/bin/bash
# Ask Five Engine · mock expert full-test 脚本
# 临时用测试 registry 替换主 registry，跑 check-experts，然后恢复

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MAIN_REGISTRY="$ENGINE_DIR/references/expert-registry.json"
MOCK_REGISTRY="$SCRIPT_DIR/mock-expert-registry.json"
BACKUP="$SCRIPT_DIR/expert-registry.json.backup"

echo "=== Ask Five Engine Full Test ==="
echo "Engine dir: $ENGINE_DIR"

# 备份主 registry
cp "$MAIN_REGISTRY" "$BACKUP"

# 用 mock registry 替换
cp "$MOCK_REGISTRY" "$MAIN_REGISTRY"

echo ""
echo "--- check-experts output ---"
bash "$ENGINE_DIR/scripts/check-experts.sh" "$ENGINE_DIR" | python3 -m json.tool

# 恢复主 registry
cp "$BACKUP" "$MAIN_REGISTRY"
rm "$BACKUP"

echo ""
echo "=== Registry restored ==="
