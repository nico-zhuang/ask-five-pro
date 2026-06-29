#!/usr/bin/env python3
"""
Brain Crew 查询机制性能基准测试。

目标：验证 query_experts / query_panels / load_expert_content
满足《brain-crew 查询机制设计规范》中的性能要求：
- 单次 query_experts < 100ms
- 单次 query_panels（5 个子议题） < 300ms
- load_expert_content < 50ms
- Turbo 模式全流程查询 < 1s
"""

import os
import sys
import time
import statistics

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import brain_crew_query as bcq


def benchmark_query_experts(iterations=100):
    print("[BENCHMARK] query_experts")
    times = []
    for _ in range(iterations):
        start = time.time()
        bcq.query_experts(
            categories=["产品", "战略"],
            tags=["用户体验", "聚焦"],
            mode="consensus",
            limit=5
        )
        times.append((time.time() - start) * 1000)

    avg = statistics.mean(times)
    p95 = sorted(times)[int(iterations * 0.95)]
    max_t = max(times)

    print(f"  迭代次数: {iterations}")
    print(f"  平均耗时: {avg:.3f}ms")
    print(f"  P95 耗时: {p95:.3f}ms")
    print(f"  最大耗时: {max_t:.3f}ms")
    print(f"  目标: <100ms")
    print(f"  结果: {'✅ 通过' if avg < 100 else '❌ 未通过'}\n")

    return avg < 100


def benchmark_query_panels(iterations=100):
    print("[BENCHMARK] query_panels（5 个子议题）")
    sub_topics = [
        {"id": "t1", "title": "产品战略", "categories": ["产品", "战略"], "tags": ["用户体验"]},
        {"id": "t2", "title": "投资决策", "categories": ["投资", "风控"], "tags": ["价值投资"]},
        {"id": "t3", "title": "AI 平台", "categories": ["AI", "平台"], "tags": ["生态"]},
        {"id": "t4", "title": "组织管理", "categories": ["组织", "管理"], "tags": ["团队"]},
        {"id": "t5", "title": "品牌传播", "categories": ["品牌", "传播"], "tags": ["内容"]},
    ]

    times = []
    for _ in range(iterations):
        start = time.time()
        bcq.query_panels(sub_topics, mode="turbo", max_per_panel=3)
        times.append((time.time() - start) * 1000)

    avg = statistics.mean(times)
    p95 = sorted(times)[int(iterations * 0.95)]
    max_t = max(times)

    print(f"  迭代次数: {iterations}")
    print(f"  平均耗时: {avg:.3f}ms")
    print(f"  P95 耗时: {p95:.3f}ms")
    print(f"  最大耗时: {max_t:.3f}ms")
    print(f"  目标: <300ms")
    print(f"  结果: {'✅ 通过' if avg < 300 else '❌ 未通过'}\n")

    return avg < 300


def benchmark_load_expert_content(iterations=100):
    print("[BENCHMARK] load_expert_content")
    bcq.clear_content_cache()

    # 首次加载
    start = time.time()
    bcq.load_expert_content('steve-jobs')
    first_time = (time.time() - start) * 1000

    # 缓存命中
    times = []
    for _ in range(iterations):
        start = time.time()
        bcq.load_expert_content('steve-jobs')
        times.append((time.time() - start) * 1000)

    avg = statistics.mean(times)
    p95 = sorted(times)[int(iterations * 0.95)]

    print(f"  首次加载: {first_time:.3f}ms")
    print(f"  缓存命中平均: {avg:.3f}ms")
    print(f"  缓存命中 P95: {p95:.3f}ms")
    print(f"  目标: <50ms")
    print(f"  结果: {'✅ 通过' if first_time < 50 and avg < 50 else '❌ 未通过'}\n")

    return first_time < 50 and avg < 50


def benchmark_turbo_full_flow():
    print("[BENCHMARK] Turbo 模式全流程查询")
    bcq.clear_content_cache()

    # 模拟：顶层分解 + 5 个子议会 + 综合会议
    sub_topics = [
        {"id": "t1", "title": "产品战略", "categories": ["产品", "战略"], "tags": ["用户体验"]},
        {"id": "t2", "title": "投资决策", "categories": ["投资", "风控"], "tags": ["价值投资"]},
        {"id": "t3", "title": "AI 平台", "categories": ["AI", "平台"], "tags": ["生态"]},
        {"id": "t4", "title": "组织管理", "categories": ["组织", "管理"], "tags": ["团队"]},
        {"id": "t5", "title": "品牌传播", "categories": ["品牌", "传播"], "tags": ["内容"]},
    ]

    start = time.time()

    # 1. 顶层分解（query_experts）
    bcq.query_experts(
        categories=["战略", "决策"],
        tags=["优先级", "资源分配"],
        mode="turbo",
        limit=5
    )

    # 2. N 次子议会（query_panels）
    panels = bcq.query_panels(sub_topics, mode="turbo", max_per_panel=3)

    # 3. 加载每个 panel 中选中的专家的 SKILL.md
    for panel in panels:
        for expert in panel['experts']:
            bcq.load_expert_content(expert['id'])

    # 4. 综合会议（query_experts）
    bcq.query_experts(
        categories=["综合", "决策"],
        tags=["汇总", "结论"],
        mode="consensus",
        limit=3
    )

    elapsed = (time.time() - start) * 1000

    print(f"  全流程耗时: {elapsed:.3f}ms")
    print(f"  包含: 顶层分解 + 5 子议会 + 延迟加载所有选中专家 + 综合会议")
    print(f"  目标: <1000ms")
    print(f"  结果: {'✅ 通过' if elapsed < 1000 else '❌ 未通过'}\n")

    return elapsed < 1000


def main():
    print("=" * 70)
    print("Brain Crew 查询机制性能基准测试")
    print("=" * 70)
    print("")

    results = []
    results.append(("query_experts", benchmark_query_experts()))
    results.append(("query_panels", benchmark_query_panels()))
    results.append(("load_expert_content", benchmark_load_expert_content()))
    results.append(("turbo_full_flow", benchmark_turbo_full_flow()))

    print("=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 未通过"
        print(f"  {name:25s} {status}")

    all_passed = all(passed for _, passed in results)
    print("")
    if all_passed:
        print("🎉 所有性能基准测试通过")
    else:
        print("⚠️ 部分性能基准测试未通过，需要优化")
        sys.exit(1)


if __name__ == '__main__':
    main()
