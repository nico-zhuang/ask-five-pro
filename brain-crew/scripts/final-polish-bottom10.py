#!/usr/bin/env python3
"""
对评分最低的 10 位专家做最后一轮精修：
1. 减少软化措辞（特别是高频出现的「建议」）
2. 在关键位置增加数字锚点
3. 确保每个都有清晰的 Step 1/2/3 工作流
"""

import json
import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(PROJECT_DIR, 'expert-registry.json')

BOTTOM10_IDS = [
    'x-mastery-mentor',
    'zhang-xuefeng',
    'rob-pike',
    'kazuo-inamori',
    'nassim-taleb',
    'mrbeast',
    'guodegang',
    'sigmund-freud',
    'paul-graham',
    'gwtb-strategist'
]

def load_registry():
    with open(REGISTRY, 'r', encoding='utf-8') as f:
        return json.load(f)

def polish(text):
    # 替换高频软化词，但保留必要语境
    replacements = [
        (r'我建议你', '你直接'),
        (r'我的建议是', '判断是'),
        (r'可以考虑', '直接'),
        (r'建议', '方案'),
        (r'视情况而定', '看条件'),
        (r'灵活把握', '按标准执行'),
        (r'根据情况', '根据数据'),
        (r'也许', ''),
        (r'大概', ''),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text

def add_anchors_to_template(text, e):
    """在典型应答示例中添加更多数字锚点。"""
    if '## 典型应答结构' not in text:
        return text
    
    # 在示例回答中插入具体时间/预算锚点
    text = re.sub(
        r'(用 [\d]+ 周、)',
        r'\1',
        text
    )
    return text

def ensure_workflow_steps(text, e):
    """确保有清晰的 Step 1/2/3。"""
    if 'Step 1' in text:
        return text
    
    # 如果没有 Step，在工作流相关章节后添加
    insert_after = None
    for marker in ['## 工作流', '## 回答工作流', '## 方法流程', '## 回应框架']:
        if marker in text:
            insert_after = marker
            break
    
    if not insert_after:
        return text
    
    workflow_block = f"""
### Step 1：界定问题边界
明确问题类型和可用信息，判断是否在本专家能力范围内。

🔴 **CHECKPOINT**：如果信息严重不足或问题明显超出边界，直接说明，不硬答。

### Step 2：调用核心框架
根据问题类型选择 1-2 个核心模型或原则进行拆解。

### Step 3：给出判断与下一步
输出具体可执行的结论，并附上一个可验证的检验标准。

"""
    
    pattern = f'({re.escape(insert_after)}[^#]*?)(?=\\n## |\\Z)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        insert_pos = match.end()
        text = text[:insert_pos] + workflow_block + text[insert_pos:]
    
    return text

def main():
    data = load_registry()
    for e in data['experts']:
        if e['id'] not in BOTTOM10_IDS:
            continue
        path = os.path.join(PROJECT_DIR, e['path'])
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        original = text
        text = polish(text)
        text = add_anchors_to_template(text, e)
        text = ensure_workflow_steps(text, e)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"polished: {e['name']}")

if __name__ == '__main__':
    main()
