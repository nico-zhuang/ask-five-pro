#!/usr/bin/env python3
"""
Ask Five Engine × Brain Crew 联调验证脚本

用法：
  python3 tests/brain-crew-integration-test.py

输出：
  控制台报告 + 当前目录 brain-crew-integration-report.json
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 把 Brain Crew scripts 加入路径
sys.path.insert(0, os.path.expanduser('~/.hanako/skills/brain-crew/scripts'))
from brain_crew_query import (
    load_registry,
    query_experts,
    query_panels,
    load_expert_content,
    resolve_expert_path,
    get_registry_stats,
)

ENGINE_DIR = Path(__file__).resolve().parent.parent
BRAIN_CREW_REGISTRY = os.path.expanduser('~/.hanako/skills/brain-crew/expert-registry.json')
ENGINE_REGISTRY = ENGINE_DIR / 'references' / 'expert-registry.json'
VALIDATE_SCRIPT = ENGINE_DIR / 'scripts' / 'validate-expert.sh'
MATCH_SCRIPT = ENGINE_DIR / 'scripts' / 'match-experts.py'

TOPIC = '我们要不要做短视频矩阵？'


def run_validate_expert(expert_dir: Path) -> dict:
    """调用 engine 的 validate-expert.sh 检查单个 expert。"""
    try:
        out = subprocess.check_output(
            ['bash', str(VALIDATE_SCRIPT), str(expert_dir)],
            text=True, stderr=subprocess.STDOUT
        )
        return json.loads(out)
    except Exception as e:
        return {'valid': False, 'errors': [str(e)], 'warnings': []}


def test_registry_sync():
    """验证 Brain Crew registry 与 Engine registry 副本同步。"""
    print('\n' + '=' * 70)
    print('1. Registry 同步性验证')
    print('=' * 70)

    with open(BRAIN_CREW_REGISTRY, 'r', encoding='utf-8') as f:
        bc_data = json.load(f)
    with open(ENGINE_REGISTRY, 'r', encoding='utf-8') as f:
        eng_data = json.load(f)

    bc_experts = {e['id']: e for e in bc_data.get('experts', [])}
    eng_experts = {e['id']: e for e in eng_data.get('experts', [])}

    bc_only = set(bc_experts) - set(eng_experts)
    eng_only = set(eng_experts) - set(bc_experts)

    # 忽略 engine 副本额外字段 bundled/onboarding
    field_diff = []
    for eid in bc_experts:
        bc_e = bc_experts[eid]
        eng_e = eng_experts.get(eid, {})
        for key in ['name', 'pack', 'path', 'core_domain', 'style', 'topic_tags', 'sensitivity', 'version']:
            if bc_e.get(key) != eng_e.get(key):
                field_diff.append((eid, key, bc_e.get(key), eng_e.get(key)))

    ok = not bc_only and not eng_only and not field_diff
    print(f"  Brain Crew experts: {len(bc_experts)}")
    print(f"  Engine registry experts: {len(eng_experts)}")
    print(f"  Brain Crew only: {bc_only or '无'}")
    print(f"  Engine only: {eng_only or '无'}")
    print(f"  字段差异: {len(field_diff)} 处")
    if field_diff:
        for eid, key, v1, v2 in field_diff[:5]:
            print(f"    - {eid}.{key}: BC={v1} vs ENG={v2}")
    print(f"  ✅ 同步" if ok else f"  ❌ 不同步")
    return ok, {'bc_only': list(bc_only), 'eng_only': list(eng_only), 'field_diff': field_diff}


def test_path_resolution():
    """验证所有 expert path 能解析到真实 SKILL.md。"""
    print('\n' + '=' * 70)
    print('2. 专家路径解析验证')
    print('=' * 70)

    registry = load_registry(BRAIN_CREW_REGISTRY)
    registry_dir = os.path.dirname(registry['_registry_path'])
    missing = []
    ok_count = 0

    for e in registry.get('experts', []):
        resolved = resolve_expert_path(e, registry_dir)
        exists = os.path.isfile(resolved)
        if not exists:
            missing.append({'id': e['id'], 'path': e.get('path'), 'resolved': resolved})
        else:
            ok_count += 1

    ok = len(missing) == 0
    print(f"  可解析: {ok_count} / {len(registry.get('experts', []))}")
    if missing:
        for m in missing:
            print(f"    ❌ {m['id']}: {m['resolved']}")
    print(f"  {'✅ 全部可解析' if ok else '❌ 存在缺失'}")
    return ok, {'ok_count': ok_count, 'missing': missing}


def test_validate_all_experts():
    """对所有 expert 运行 validate-expert.sh。"""
    print('\n' + '=' * 70)
    print('3. Expert SKILL.md 规范验证')
    print('=' * 70)

    registry = load_registry(BRAIN_CREW_REGISTRY)
    registry_dir = os.path.dirname(registry['_registry_path'])
    invalid = []
    warn_count = 0

    for e in registry.get('experts', []):
        resolved = resolve_expert_path(e, registry_dir)
        expert_dir = Path(resolved).parent
        result = run_validate_expert(expert_dir)
        if not result.get('valid'):
            invalid.append({'id': e['id'], 'errors': result.get('errors', [])})
        warn_count += len(result.get('warnings', []))

    ok = len(invalid) == 0
    print(f"  通过: {len(registry.get('experts', [])) - len(invalid)} / {len(registry.get('experts', []))}")
    print(f"  警告: {warn_count} 处")
    if invalid:
        for item in invalid:
            print(f"    ❌ {item['id']}")
            for err in item['errors']:
                print(f"       - {err}")
    print(f"  {'✅ 全部通过' if ok else '❌ 存在不通过'}")
    return ok, {'invalid': invalid, 'warn_count': warn_count}


def test_match_experts():
    """测试 engine 的 match-experts.py。"""
    print('\n' + '=' * 70)
    print('4. Engine match-experts.py 验证')
    print('=' * 70)

    def run_match(mode):
        out = subprocess.check_output([
            sys.executable, str(MATCH_SCRIPT),
            '--registry', str(ENGINE_REGISTRY),
            '--topic', TOPIC,
            '--mode', mode,
        ], text=True)
        return json.loads(out)

    consensus = run_match('consensus')
    redteam = run_match('red-team')

    print(f"  议题: {consensus['topic']}")
    print(f"  推断主类别: {consensus['primary_categories']}")
    print(f"  目标 panel 人数: {consensus['target_panel_size']}")

    print(f"\n  [consensus] 选中:")
    for e in consensus['selected_panel']:
        print(f"    - {e['name']} (score={e['raw_score']}, domain={e['core_domain']})")

    print(f"\n  [red-team] 选中:")
    for e in redteam['selected_panel']:
        print(f"    - {e['name']} (score={e['raw_score']}, domain={e['core_domain']})")

    # 合理性检查
    risk_expert_ids = {'nassim-taleb', 'charlie-munger', 'richard-feynman'}
    redteam_ids = {e['id'] for e in redteam['selected_panel']}
    has_risk_expert = bool(redteam_ids & risk_expert_ids)
    no_zero_score = all(e['raw_score'] > 0 for e in redteam['selected_panel'])

    ok = (
        len(consensus['selected_panel']) >= 3 and
        len(redteam['selected_panel']) >= 3 and
        any(e['id'] == 'mrbeast' for e in consensus['selected_panel']) and
        has_risk_expert and
        no_zero_score
    )

    print(f"\n  red-team 含风险/验证视角专家: {'✅' if has_risk_expert else '❌'}")
    print(f"  red-team 无 0 分凑数专家: {'✅' if no_zero_score else '❌'}")
    print(f"\n  {'✅ match-experts 输出合理' if ok else '❌ match-experts 输出异常'}")
    return ok, {'consensus': consensus, 'redteam': redteam}


def test_brain_crew_query():
    """测试 Brain Crew query API。"""
    print('\n' + '=' * 70)
    print('5. Brain Crew Query API 验证')
    print('=' * 70)

    categories = ['内容', '增长', '传播']
    tags = ['短视频', '矩阵', '内容创作', '增长实验']

    consensus = query_experts(categories, tags, mode='consensus', limit=5, registry_path=BRAIN_CREW_REGISTRY)
    redteam = query_experts(categories + ['风险'], tags, mode='red-team', limit=5, registry_path=BRAIN_CREW_REGISTRY)

    print(f"  [consensus] 选中:")
    for e in consensus:
        print(f"    - {e['name']} (score={e['score']}, reason={e['reason']})")

    print(f"\n  [red-team] 选中:")
    for e in redteam:
        print(f"    - {e['name']} (score={e['score']}, reason={e['reason']})")

    # 延迟加载测试
    first_id = consensus[0]['id']
    content = load_expert_content(first_id, registry_path=BRAIN_CREW_REGISTRY)
    print(f"\n  延迟加载 {first_id}: {len(content)} chars")

    ok = len(consensus) >= 3 and len(redteam) >= 3 and len(content) > 0
    print(f"\n  {'✅ Brain Crew Query API 正常' if ok else '❌ Brain Crew Query API 异常'}")
    return ok, {
        'consensus': [{'id': e['id'], 'name': e['name'], 'score': e['score'], 'reason': e['reason']} for e in consensus],
        'redteam': [{'id': e['id'], 'name': e['name'], 'score': e['score'], 'reason': e['reason']} for e in redteam],
        'loaded_content_length': len(content),
    }


def test_sensitive_exclusion():
    """验证敏感角色默认被排除，对抗模式下可出现。"""
    print('\n' + '=' * 70)
    print('6. 敏感角色排除验证')
    print('=' * 70)

    categories = ['谈判', '博弈', '权力']
    tags = ['谈判策略', '利益交换', '舆论操控']

    normal = query_experts(categories, tags, mode='consensus', limit=5, registry_path=BRAIN_CREW_REGISTRY)
    debate = query_experts(categories, tags, mode='debate', limit=5, registry_path=BRAIN_CREW_REGISTRY)

    normal_has_sensitive = any(e['sensitivity'] == 'sensitive' for e in normal)
    debate_has_sensitive = any(e['sensitivity'] == 'sensitive' for e in debate)

    print(f"  默认模式敏感角色: {'有' if normal_has_sensitive else '无'}")
    print(f"  对抗模式敏感角色: {'有' if debate_has_sensitive else '无'}")
    print(f"  默认模式选中: {[e['name'] for e in normal]}")
    print(f"  对抗模式选中: {[e['name'] for e in debate]}")

    ok = (not normal_has_sensitive) and debate_has_sensitive
    print(f"\n  {'✅ 敏感角色排除机制正常' if ok else '❌ 敏感角色排除机制异常'}")
    return ok, {
        'normal_has_sensitive': normal_has_sensitive,
        'debate_has_sensitive': debate_has_sensitive,
        'normal_names': [e['name'] for e in normal],
        'debate_names': [e['name'] for e in debate],
    }


def test_check_experts_script():
    """验证 engine 的 check-experts.sh 对 Brain Crew 专家的解析。"""
    print('\n' + '=' * 70)
    print('7. Engine check-experts.sh 验证')
    print('=' * 70)

    try:
        out = subprocess.check_output(
            ['bash', str(ENGINE_DIR / 'scripts' / 'check-experts.sh'), str(ENGINE_DIR)],
            text=True, stderr=subprocess.STDOUT
        )
        result = json.loads(out)
        installed = result.get('installed', [])
        simulated = result.get('simulated', [])
        print(f"  installed: {len(installed)}")
        print(f"  simulated: {len(simulated)}")
        # 期望全部 installed
        ok = len(installed) == 34 and len(simulated) == 0
        print(f"\n  {'✅ 全部识别为 installed' if ok else '⚠️  部分专家被识别为 simulated（可能是 check-experts.sh 的占位符解析问题）'}")
        return ok, result
    except Exception as e:
        print(f"\n  ❌ check-experts.sh 执行失败: {e}")
        return False, {'error': str(e)}


def main():
    print('Ask Five Engine × Brain Crew 联调验证')
    print(f'时间: {datetime.now().isoformat()}')
    print(f'Brain Crew registry: {BRAIN_CREW_REGISTRY}')
    print(f'Engine registry: {ENGINE_REGISTRY}')
    print(f'测试议题: {TOPIC}')

    results = {}
    checks = [
        ('registry_sync', test_registry_sync),
        ('path_resolution', test_path_resolution),
        ('validate_experts', test_validate_all_experts),
        ('match_experts', test_match_experts),
        ('brain_crew_query', test_brain_crew_query),
        ('sensitive_exclusion', test_sensitive_exclusion),
        ('check_experts_script', test_check_experts_script),
    ]

    all_ok = True
    for name, fn in checks:
        try:
            ok, data = fn()
            results[name] = {'ok': ok, 'data': data}
            if not ok:
                all_ok = False
        except Exception as e:
            results[name] = {'ok': False, 'error': str(e)}
            all_ok = False
            print(f"\n💥 {name} 执行异常: {e}")

    report_path = ENGINE_DIR / 'tests' / 'brain-crew-integration-report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'topic': TOPIC,
            'overall_ok': all_ok,
            'results': results,
        }, f, ensure_ascii=False, indent=2)

    print('\n' + '=' * 70)
    print('联调总结')
    print('=' * 70)
    for name, r in results.items():
        status = '✅' if r.get('ok') else '❌'
        print(f"  {status} {name}")
    print(f"\n报告已保存: {report_path}")
    print(f"整体结果: {'✅ 通过' if all_ok else '❌ 未通过'}")


if __name__ == '__main__':
    main()
