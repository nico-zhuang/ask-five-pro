#!/usr/bin/env python3
"""
Brain Crew 实测 prompt 测试框架。

当前阶段：
1. 验证 query_experts 对实测 prompt 的匹配正确性
2. 验证专家内容是否覆盖 prompt 所需框架
3. （TODO）接入 LLM 生成真实输出后做人工/自动评分

用法：
  python3 scripts/run-real-prompt-tests.py
"""

import json
import os
import re
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_DIR, 'scripts'))

from brain_crew_query import query_experts, load_expert_content

TESTS_FILE = os.path.join(PROJECT_DIR, 'tests', 'real-prompt-tests.json')

def load_tests():
    with open(TESTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_content_coverage(expert_id, prompt, text):
    """简单检查专家内容是否包含 prompt 所需的框架关键词。"""
    prompt_lower = prompt.lower()
    
    coverage_keywords = []
    if any(w in prompt_lower for w in ['产品', '功能', '优先']):
        coverage_keywords.extend(['聚焦', '说不', '取舍', 'AB测试', 'Press Release'])
    if any(w in prompt_lower for w in ['投资', '公司']):
        coverage_keywords.extend(['护城河', '能力圈', '安全边际'])
    if any(w in prompt_lower for w in ['视频', '标题', '播放量']):
        coverage_keywords.extend(['CTR', 'AVD', '标题', '缩略图'])
    if any(w in prompt_lower for w in ['硬件', 'AI', '初创']):
        coverage_keywords.extend(['Narrow AI', '算力', '任务', '平台'])
    if any(w in prompt_lower for w in ['品牌', '小红书', '笔记', '评论']):
        coverage_keywords.extend(['GET', 'WHO', 'TO', 'BY', '高频词'])
    if any(w in prompt_lower for w in ['决策', '信息']):
        coverage_keywords.extend(['单向门', '双向门', '能力圈', '知行合一'])
    
    if not coverage_keywords:
        return True, []
    
    matched = [kw for kw in coverage_keywords if kw in text]
    return len(matched) >= 1, matched

def main():
    tests_data = load_tests()
    prompts = tests_data['prompts']
    
    print("=" * 72)
    print("Brain Crew 实测 Prompt 测试")
    print("=" * 72)
    print(f"\n测试 prompt 数量：{len(prompts)}\n")
    
    total_match_score = 0
    results = []
    
    for p in prompts:
        print(f"\n【{p['id']}】{p['prompt'][:40]}...")
        print(f"  期望专家：{', '.join(p['expected_experts'])}")
        
        # Query API match: use expected categories + extracted tags
        import re
        tags = re.findall(r'[一-龥]{2,6}', p['prompt'])
        tags = [t for t in tags if len(t) >= 2][:8]
        matched = query_experts(
            categories=p.get('expected_categories', []),
            tags=tags,
            limit=5
        )
        matched_ids = [m['id'] for m in matched]
        print(f"  实际匹配：{', '.join(matched_ids)}")
        
        # Check if expected experts are in top 3
        top3_ids = matched_ids[:3]
        found_expected = [eid for eid in p['expected_experts'] if eid in top3_ids]
        match_score = len(found_expected) / len(p['expected_experts'])
        total_match_score += match_score
        
        # Check content coverage for top matched expert
        top_expert_id = matched_ids[0]
        text = load_expert_content(top_expert_id)
        covered, keywords = check_content_coverage(top_expert_id, p['prompt'], text)
        
        status = "✅" if match_score >= 0.5 and covered else "⚠️"
        print(f"  {status} 期望专家命中：{match_score:.0%}，内容覆盖：{'是' if covered else '否'}")
        
        results.append({
            'id': p['id'],
            'match_score': match_score,
            'content_covered': covered,
            'top_expert': top_expert_id,
        })
    
    avg_match = total_match_score / len(prompts)
    coverage_rate = sum(1 for r in results if r['content_covered']) / len(prompts)
    
    print("\n" + "=" * 72)
    print("测试汇总")
    print("=" * 72)
    print(f"平均专家匹配率：{avg_match:.1%}")
    print(f"内容覆盖率：{coverage_rate:.1%}")
    print(f"\n说明：当前为匹配+覆盖测试，真实输出生成需在接入 LLM 后补充。")
    
    # Save results
    results_file = os.path.join(PROJECT_DIR, 'tests', 'real-prompt-test-results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'avg_match_score': avg_match,
            'coverage_rate': coverage_rate,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存：{results_file}")

if __name__ == '__main__':
    main()
