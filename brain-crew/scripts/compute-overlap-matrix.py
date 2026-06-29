#!/usr/bin/env python3
"""
计算 Brain Crew 专家之间的重叠度矩阵。

重叠度 = (共同 core_domain + 共同 topic_tags) / 较小集合大小
"""

import json
import os
from itertools import combinations

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(PROJECT_DIR, 'expert-registry.json')

def load_registry():
    with open(REGISTRY, 'r', encoding='utf-8') as f:
        return json.load(f)

def overlap_ratio(a, b):
    set_a = set(a)
    set_b = set(b)
    if not set_a or not set_b:
        return 0.0
    inter = set_a & set_b
    return len(inter) / min(len(set_a), len(set_b))

def combined_overlap(e1, e2):
    domain = overlap_ratio(e1.get('core_domain', []), e2.get('core_domain', []))
    tags = overlap_ratio(e1.get('topic_tags', []), e2.get('topic_tags', []))
    # domain 权重 0.6，tags 权重 0.4
    return domain * 0.6 + tags * 0.4

def main():
    data = load_registry()
    experts = data['experts']
    
    # 只计算同 pack 内的重叠
    by_pack = {}
    for e in experts:
        by_pack.setdefault(e['pack'], []).append(e)
    
    print("# Brain Crew 专家重叠度矩阵\n")
    print("> 重叠度 = 0.6 × core_domain 重叠 + 0.4 × topic_tags 重叠\n")
    
    high_overlap_pairs = []
    
    for pack, members in sorted(by_pack.items()):
        if len(members) < 2:
            continue
        print(f"## {pack.upper()} Pack（{len(members)} 人）\n")
        
        # 表头
        names = [e['name'] for e in members]
        print("| 专家 | " + " | ".join(names) + " |")
        print("|" + "---|" * (len(members) + 1))
        
        for i, e1 in enumerate(members):
            row = [e1['name']]
            for j, e2 in enumerate(members):
                if i == j:
                    row.append("—")
                elif i < j:
                    score = combined_overlap(e1, e2)
                    row.append(f"{score:.2f}")
                    if score >= 0.5:
                        high_overlap_pairs.append((pack, e1['name'], e2['name'], score))
                else:
                    # 下三角，复用上三角结果
                    score = combined_overlap(e1, e2)
                    row.append(f"{score:.2f}")
            print("| " + " | ".join(row) + " |")
        print()
    
    print("## 高重叠配对（≥0.50）\n")
    if high_overlap_pairs:
        high_overlap_pairs.sort(key=lambda x: -x[3])
        print("| Pack | 专家 A | 专家 B | 重叠度 | 建议 |")
        print("|---|---|---|---|---|")
        for pack, a, b, score in high_overlap_pairs:
            print(f"| {pack} | {a} | {b} | {score:.2f} | 考虑差异化分工或迁移 |")
    else:
        print("无高重叠配对。")
    print()
    
    # 计算每位专家的平均重叠度
    print("## 每位专家平均重叠度\n")
    print("| 专家 | Pack | 平均重叠 | 状态 |")
    print("|---|---|---|---|")
    
    overlap_sum = {e['id']: 0.0 for e in experts}
    overlap_count = {e['id']: 0 for e in experts}
    
    for pack, members in by_pack.items():
        for e1, e2 in combinations(members, 2):
            score = combined_overlap(e1, e2)
            overlap_sum[e1['id']] += score
            overlap_sum[e2['id']] += score
            overlap_count[e1['id']] += 1
            overlap_count[e2['id']] += 1
    
    for e in sorted(experts, key=lambda x: overlap_sum[x['id']] / max(1, overlap_count[x['id']]), reverse=True):
        avg = overlap_sum[e['id']] / max(1, overlap_count[e['id']])
        status = "⚠️ 高重叠" if avg >= 0.4 else "✅ 正常"
        print(f"| {e['name']} | {e['pack']} | {avg:.2f} | {status} |")

if __name__ == '__main__':
    main()
