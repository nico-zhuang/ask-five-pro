#!/usr/bin/env python3
"""
评估 LLM 实测输出的质量。

当前规则（轻量级）：
1. 是否破角色（出现 "作为 AI"、"我是语言模型"、"我无法" 等）
2. 是否输出工程标注（Step 1、CHECKPOINT、P0、表格等）
3. 是否过度 hedging（"可能"/"或许"/"视情况而定" 等）
4. 长度是否合适（100-500 字）
5. 是否使用第一人称
"""

import json
import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(PROJECT_DIR, 'tests', 'real-outputs')
RESULTS_FILE = os.path.join(PROJECT_DIR, 'tests', 'llm-output-evaluation.json')

ROLE_BREAK_PATTERNS = [
    r'作为 AI',
    r'我是语言模型',
    r'我无法预测',
    r'我无法.*回答',
    r'我没有.*能力',
    r'基于.*训练数据',
    r'请注意.*只是模拟',
]

ENGINEERING_MARKERS = [
    r'Step \d+',
    r'CHECKPOINT',
    r'P0',
    r'P1',
    r'🛑',
    r'🔴',
    r'## ',
    r'\|.*\|.*\|',  # 表格
]

HEDGING_WORDS = [
    r'可能', r'或许', r'视情况而定', r'灵活把握', r'根据情况', r'可以考虑',
    r'也许', r'大概', r'有待商榷'
]

def evaluate_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Split into responses by P headers
    responses = re.split(r'\n## P\d+:', text)
    responses = [r.strip() for r in responses if r.strip()]
    
    eval_results = []
    for resp in responses:
        role_break = any(re.search(p, resp) for p in ROLE_BREAK_PATTERNS)
        eng_marker = any(re.search(p, resp) for p in ENGINEERING_MARKERS)
        hedging_count = sum(len(re.findall(p, resp)) for p in HEDGING_WORDS)
        first_person = bool(re.search(r'\b我\b|\bI\b', resp))
        length = len(resp)
        length_ok = 80 <= length <= 600
        
        # Score 0-10
        score = 10
        if role_break:
            score -= 4
        if eng_marker:
            score -= 2
        if hedging_count >= 2:
            score -= 2
        if not first_person:
            score -= 2
        if not length_ok:
            score -= 1
        
        eval_results.append({
            'role_break': role_break,
            'engineering_marker': eng_marker,
            'hedging_count': hedging_count,
            'first_person': first_person,
            'length': length,
            'length_ok': length_ok,
            'score': max(0, score)
        })
    
    return eval_results

def main():
    if not os.path.exists(OUTPUTS_DIR):
        print(f'Outputs dir not found: {OUTPUTS_DIR}')
        return
    
    all_results = {}
    total_score = 0
    total_count = 0
    
    for filename in sorted(os.listdir(OUTPUTS_DIR)):
        if not filename.endswith('_llm.md') and not filename.endswith('_llm-pilot.md'):
            continue
        path = os.path.join(OUTPUTS_DIR, filename)
        evals = evaluate_file(path)
        avg_score = sum(e['score'] for e in evals) / len(evals) if evals else 0
        all_results[filename] = {
            'avg_score': round(avg_score, 2),
            'responses': evals
        }
        total_score += sum(e['score'] for e in evals)
        total_count += len(evals)
    
    overall_avg = total_score / total_count if total_count else 0
    
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'overall_avg': round(overall_avg, 2),
            'total_responses': total_count,
            'files': all_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f'评估完成：{total_count} 条 LLM 输出')
    print(f'平均质量分：{overall_avg:.2f}/10')
    print(f'结果保存：{RESULTS_FILE}')

if __name__ == '__main__':
    main()
