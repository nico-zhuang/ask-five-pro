#!/usr/bin/env python3
"""
移除各专家 SKILL.md 内的首次激活免责声明，统一放到 Brain Crew SKILL.md 顶层。

处理内容：
1. 删除 "免责声明仅首次激活时说一次" 及其附带引语
2. 删除 STOP 块中关于免责声明的指令
3. 删除 checkpoint 中 "首次激活才说一次免责" 的检查项
4. 把 failure modes 里 "引用 STOP 段免责声明" 改为 "引用 Brain Crew 顶层免责声明"
"""

import json
import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(PROJECT_DIR, 'expert-registry.json')

def load_registry():
    with open(REGISTRY, 'r', encoding='utf-8') as f:
        return json.load(f)

def remove_disclaimers(text):
    original_len = len(text)
    
    # Pattern 1: **免责声明仅首次激活时说一次**（...），后续对话不再重复
    text = re.sub(
        r'[-\*\s]*\*\*免责声明仅首次激活时说一次\*\*.*?后续对话不再重复\s*\n',
        '',
        text,
        flags=re.DOTALL
    )
    
    # Pattern 2: 🛑 STOP block with disclaimer
    text = re.sub(
        r'[-\*\s]*[🛑🔴]?\s*\*\*STOP[^*]*\*\*[:：]?\s*首次激活时[^。]*?免责声明[^。]*?[。!！].*?后续对话[^\n]*\n',
        '',
        text,
        flags=re.DOTALL
    )
    
    # Pattern 3: 首次激活时，必须说一次免责声明：「...」。**此后对话绝不重复**...
    text = re.sub(
        r'[-\*\s]*首次激活时，[^。]*?免责声明[^。]*?[。!！]\s*\*\*此后对话绝不重复\*\*[^\n]*\n',
        '',
        text,
        flags=re.DOTALL
    )
    
    # Pattern 4: 首次激活时输出免责声明一次——「...」。后续对话**绝不**重复
    text = re.sub(
        r'[-\*\s]*首次激活时输出免责声明一次[^。]*?[。!！]\s*后续对话[^\n]*\n',
        '',
        text,
        flags=re.DOTALL
    )
    
    # Pattern 5: 首次激活说一次：「...」。后续不再重复
    text = re.sub(
        r'[-\*\s]*首次激活说一次[^。]*?[。!！]\s*后续不再重复\s*\n',
        '',
        text,
        flags=re.DOTALL
    )
    
    # Pattern 6: standalone disclaimer quote lines
    text = re.sub(
        r'[-\*\s]*「?我以[^」]*?视角和你聊，基于公开言论推断，非本人观点。?」?\s*\n',
        '',
        text
    )
    
    # Pattern 7: checkpoint items about disclaimer
    text = re.sub(
        r'\d+\.\s*\*\*首次激活才说一次免责[^\n]*\n',
        '',
        text
    )
    
    # Pattern 8: failure mode references to STOP disclaimer
    text = re.sub(
        r'引用 STOP 段免责声明',
        '引用 Brain Crew 顶层免责声明',
        text
    )
    
    # Pattern 9: 退一步引免责声明 / 后退引免责声明
    text = re.sub(
        r'([^。])引免责声明',
        r'\1引用 Brain Crew 顶层免责声明',
        text
    )
    
    # Clean up excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text, len(text) != original_len

def main():
    data = load_registry()
    changed = []
    for e in data['experts']:
        path = e['path']
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        text, was_changed = remove_disclaimers(text)
        if was_changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
            changed.append(e['name'])
    
    print(f'Processed {len(data["experts"])} experts, changed {len(changed)}:')
    for name in changed:
        print(f'  - {name}')

if __name__ == '__main__':
    main()
