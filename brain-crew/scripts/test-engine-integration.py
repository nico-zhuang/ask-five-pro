#!/usr/bin/env python3
"""
测试 Ask Five Engine 与 Brain Crew 的集成。
通过 brain_crew_query 模块验证：
1. registry 可加载
2. 专家文件路径可解析且存在
3. query_experts / query_panels 返回合理结果
4. load_expert_content 延迟加载正常
5. 性能满足 Turbo 模式要求
"""

import os
import sys
import time

# 确保能导入 brain_crew_query
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import brain_crew_query as bcq


def test_registry_loading():
    print("[TEST] Registry 加载")
    stats = bcq.get_registry_stats()
    print(f"  Registry: {stats['registry_path']}")
    print(f"  Total experts: {stats['total_experts']}")
    print(f"  Packs: {stats['packs']}")
    assert stats['total_experts'] > 0, "registry 中专家数量必须 > 0"
    print("  [OK] Registry 加载成功\n")


def test_expert_paths():
    print("[TEST] 专家文件路径可达性")
    registry = bcq.load_registry()
    registry_dir = os.path.dirname(registry['_registry_path'])
    missing = []

    for e in registry.get('experts', []):
        path = bcq.resolve_expert_path(e, registry_dir)
        if not os.path.isfile(path):
            missing.append((e.get('id'), path))

    if missing:
        print(f"  [ERROR] {len(missing)} 个专家文件不可达:")
        for eid, path in missing:
            print(f"    - {eid}: {path}")
        sys.exit(1)
    else:
        print(f"  [OK] 所有 {len(registry['experts'])} 个专家文件路径均可达\n")


def test_query_experts():
    print("[TEST] query_experts 单议题匹配")
    test_cases = [
        {
            "name": "产品战略决策",
            "categories": ["产品", "战略"],
            "tags": ["用户体验", "聚焦"],
            "expect_top": "steve-jobs"
        },
        {
            "name": "投资决策",
            "categories": ["投资", "风控"],
            "tags": ["价值投资", "能力圈"],
            "expect_top": "charlie-munger"
        },
        {
            "name": "AI 平台战略",
            "categories": ["AI", "平台"],
            "tags": ["生态", "基础设施"],
            "expect_top": "jensen-huang"
        }
    ]

    for case in test_cases:
        start = time.time()
        result = bcq.query_experts(
            categories=case["categories"],
            tags=case["tags"],
            mode="consensus",
            limit=3
        )
        elapsed = (time.time() - start) * 1000

        assert len(result) > 0, f"{case['name']} 必须匹配到专家"
        top_id = result[0]['id']
        assert top_id == case['expect_top'], \
            f"{case['name']} 期望 top={case['expect_top']}, 实际={top_id}"

        print(f"  {case['name']}: {elapsed:.2f}ms")
        for e in result:
            print(f"    - {e['name']} (score={e['score']})")

    print("  [OK] query_experts 匹配正确\n")


def test_query_panels():
    print("[TEST] query_panels 批量子议题匹配（Turbo 模式）")
    sub_topics = [
        {"id": "t1", "title": "产品战略", "categories": ["产品", "战略"], "tags": ["用户体验"]},
        {"id": "t2", "title": "投资决策", "categories": ["投资", "风控"], "tags": ["价值投资"]},
        {"id": "t3", "title": "AI 平台", "categories": ["AI", "平台"], "tags": ["生态"]},
        {"id": "t4", "title": "组织管理", "categories": ["组织", "管理"], "tags": ["团队"]},
        {"id": "t5", "title": "品牌传播", "categories": ["品牌", "传播"], "tags": ["内容"]},
    ]

    start = time.time()
    panels = bcq.query_panels(sub_topics, mode="turbo", max_per_panel=3)
    elapsed = (time.time() - start) * 1000

    assert len(panels) == len(sub_topics), "panel 数量必须等于子议题数量"

    print(f"  5 个子议题批量查询: {elapsed:.2f}ms")
    for panel in panels:
        print(f"  [{panel['title']}]")
        for e in panel['experts']:
            print(f"    - {e['name']} (score={e['score']})")

    # Turbo 模式要求 <300ms 5 个子议题
    assert elapsed < 300, f"批量查询太慢: {elapsed:.2f}ms"
    print("  [OK] query_panels 性能达标\n")


def test_lazy_loading():
    print("[TEST] load_expert_content 延迟加载")

    # 第一次加载
    start = time.time()
    content1 = bcq.load_expert_content('steve-jobs')
    elapsed1 = (time.time() - start) * 1000

    # 第二次加载（应命中缓存）
    start = time.time()
    content2 = bcq.load_expert_content('steve-jobs')
    elapsed2 = (time.time() - start) * 1000

    assert len(content1) > 1000, "SKILL.md 内容应该较长"
    assert content1 == content2, "缓存内容应一致"

    print(f"  首次加载: {elapsed1:.2f}ms, length={len(content1)}")
    print(f"  缓存命中: {elapsed2:.2f}ms")
    print("  [OK] 延迟加载 + 缓存正常\n")


def test_sensitive_exclusion():
    print("[TEST] 敏感角色默认排除")
    result = bcq.query_experts(
        categories=["谈判", "博弈"],
        tags=["权力", "利益交换"],
        mode="consensus",
        limit=5
    )
    sensitive_ids = {e['id'] for e in result if e.get('sensitivity') == 'sensitive'}
    print(f"  匹配到 {len(result)} 个专家，敏感角色: {sensitive_ids or '无'}")
    assert 'donald-trump' not in [e['id'] for e in result], "默认不应选中 Trump"
    print("  [OK] 敏感角色默认排除\n")


def test_content_not_loaded_during_query():
    print("[TEST] query_experts 不加载 SKILL.md")
    bcq.clear_content_cache()

    start = time.time()
    result = bcq.query_experts(
        categories=["产品"],
        tags=["战略"],
        limit=10
    )
    elapsed = (time.time() - start) * 1000

    assert len(_cache_keys()) == 0, "查询过程中不应产生内容缓存"
    print(f"  查询 10 个专家: {elapsed:.2f}ms, 内容缓存数: {len(_cache_keys())}")
    print("  [OK] 查询阶段零 SKILL.md 读取\n")


def _cache_keys():
    return bcq._content_cache.keys()


def main():
    print("=" * 70)
    print("Ask Five Engine + Brain Crew 集成测试（基于 query API）")
    print("=" * 70)
    print("")

    test_registry_loading()
    test_expert_paths()
    test_query_experts()
    test_query_panels()
    test_lazy_loading()
    test_sensitive_exclusion()
    test_content_not_loaded_during_query()

    print("=" * 70)
    print("所有测试通过")
    print("=" * 70)


if __name__ == '__main__':
    main()
