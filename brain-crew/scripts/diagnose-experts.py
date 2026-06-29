#!/usr/bin/env python3
"""诊断所有专家 SKILL.md 的结构缺失项。"""
import json
import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(PROJECT_DIR, 'expert-registry.json')

def load_registry():
    with open(REGISTRY, 'r', encoding='utf-8') as f:
        return json.load(f)

def diagnose(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return {
        'has_step_workflow': bool(re.search(r'Step 1[:：]', text)),
        'has_checkpoint': bool(re.search(r'CHECKPOINT|🛑 STOP', text)),
        'has_failure_modes': bool(re.search(r'失败模式|Fallback|fallback', text)),
        'has_explicit_failure_branch': bool(re.search(r'如果.*失败|如果.*异常|如果.*未安装|如果.*不存在|如果.*不足', text)),
        'has_anti_patterns': bool(re.search(r'反模式|反例|黑名单|不要做|禁止', text)),
        'has_why_wrong_table': bool(re.search(r'为什么错.*正确做法|正确做法.*为什么错', text, re.DOTALL)),
        'h2_count': len(re.findall(r'\n## ', text)),
    }

def main():
    data = load_registry()
    print(f"{'专家':20s} {'Step':5s} {'CP':4s} {'失败':5s} {'分支':5s} {'反例':5s} {'表格':5s} {'H2':4s}")
    print("-" * 70)
    for e in data['experts']:
        path = os.path.join(PROJECT_DIR, e['path'])
        d = diagnose(path)
        print(f"{e['name']:20s} {'✓' if d['has_step_workflow'] else '✗':5s} "
              f"{'✓' if d['has_checkpoint'] else '✗':4s} "
              f"{'✓' if d['has_failure_modes'] else '✗':5s} "
              f"{'✓' if d['has_explicit_failure_branch'] else '✗':5s} "
              f"{'✓' if d['has_anti_patterns'] else '✗':5s} "
              f"{'✓' if d['has_why_wrong_table'] else '✗':5s} "
              f"{d['h2_count']:4d}")

if __name__ == '__main__':
    main()
