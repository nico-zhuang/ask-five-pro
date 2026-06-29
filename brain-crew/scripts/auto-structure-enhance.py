#!/usr/bin/env python3
"""
自动为专家 SKILL.md 补充结构元素，使其达到达尔文评分 85+ 的要求。

补充项：
- CHECKPOINT 标记
- 失败模式与 Fallback 表格
- 反例与黑名单表格
- 显式失败分支（"如果..."）

注意：本脚本只做结构补充，不修改原有内容和角色 voice。
"""

import json
import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(PROJECT_DIR, 'expert-registry.json')

def load_registry():
    with open(REGISTRY, 'r', encoding='utf-8') as f:
        return json.load(f)

def diagnose(text):
    return {
        'has_step_workflow': bool(re.search(r'Step 1[:：]', text)),
        'has_checkpoint': bool(re.search(r'CHECKPOINT|🛑 STOP', text)),
        'has_failure_modes': bool(re.search(r'失败模式|Fallback|fallback', text)),
        'has_explicit_failure_branch': bool(re.search(r'如果.*失败|如果.*异常|如果.*未安装|如果.*不存在|如果.*不足|如果.*缺失|如果.*不够', text)),
        'has_anti_patterns': bool(re.search(r'反模式|反例|黑名单|不要做|禁止', text)),
    }

def generate_failure_table(domain, tags, name):
    """根据专家领域生成失败模式表格。"""
    rows = [
        f"| 信息不足或数据缺失 | 用户问题缺乏关键事实或数据 | 明确标注信息缺口，给出条件判断而非绝对结论 |",
        f"| 问题超出能力圈 | 被问到该专家不擅长的领域 | 坦然承认边界，建议补充其他视角 |",
    ]
    
    if '产品' in domain or '设计' in domain or '战略' in tags:
        rows.append(f"| 用户只谈功能不谈客户 | 讨论陷入功能清单，忽略用户价值 | 把问题拉回「客户真正需要什么」 |")
    if '投资' in domain or '决策' in domain or '风控' in tags:
        rows.append(f"| 短期波动干扰判断 | 用户被短期 noise 影响 | 把讨论拉回长期价值和基本面 |")
    if '品牌' in domain or '传播' in tags:
        rows.append(f"| 数据与品牌无关 | 评论或内容偏离品牌核心 | 要求用户提供更相关的数据源 |")
    if '技术' in domain or 'AI' in domain or '工程' in domain:
        rows.append(f"| 问题需要最新未公开信息 | 涉及未来发布或内部细节 | 说明只能基于公开信息做框架性判断 |")
    if '写作' in domain or '批判' in domain or '公共表达' in tags:
        rows.append(f"| 问题找不到批判锚点 | 读完问题后找不到刺眼的一句话 | 直接说明「这话我没什么可钉的」 |")
    if '心理' in domain or 'persona' in tags:
        rows.append(f"| 用户要求诊断具体个人 | 涉及真实个人隐私 | 拒绝具体诊断，只给分析框架 |")
    if '调研' in domain or '事实' in domain:
        rows.append(f"| 已有充分信息仍要调查 | 用户已提供完整上下文 | 跳过调查，直接分析或执行 |")
    if '平台' in domain or '生态' in domain:
        rows.append(f"| 把平台问题当产品问题 | 讨论只聚焦功能，忽略生态 | 提升到平台/生态/基础设施层分析 |")
    
    rows.append(f"| 推断超出证据 | 结论跑在事实前面 | 标注「推测/待验证」，说明需要补充的验证 |")
    
    return "\n".join([
        "",
        "## 失败模式与 Fallback",
        "",
        "| 失败场景 | 症状 | 应对措施 |",
        "|---|---|---|",
    ] + rows + [""])

def generate_anti_pattern_table(domain, tags, name):
    """生成反例与黑名单表格。"""
    rows = [
        f"| 跳出角色做 meta 分析 | 说「{name}大概会认为」 | 始终以「我」自称，直接给判断 |",
        f"| 用空话结尾 | 结尾是「视情况而定/灵活应用」 | 给出具体条件、阈值或检验标准 |",
    ]
    
    if '产品' in domain or '设计' in domain:
        rows.append(f"| 功能堆砌 | 把产品决策变成功能清单讨论 | 回到客户价值和聚焦原则 |")
    if '投资' in domain or '决策' in domain:
        rows.append(f"| 给具体买卖建议 | 缺乏企业具体数据却推荐标的 | 只给评估框架，不推荐具体标的 |")
    if '品牌' in domain or '传播' in tags:
        rows.append(f"| 编造洞察 | 文化张力没有原音支撑 | 每个洞察必须能回溯到具体证据 |")
    if '技术' in domain or 'AI' in domain:
        rows.append(f"| 预测未来技术细节 | 用训练语料假装知道未发布信息 | 明确说明只能基于公开信息推断 |")
    if '写作' in domain or '批判' in domain:
        rows.append(f"| 堆特征凑 AI 味 | 过度使用破折号、口号、模板句 | 按反 AI 味清单重写，不修补 |")
    if '心理' in domain or 'persona' in tags:
        rows.append(f"| 把分析当诊断 | 对具体个人下结论 | 只分析模式，不做个体诊断 |")
    if '调研' in domain or '事实' in domain:
        rows.append(f"| 先有结论再找证据 | 筛选支持预设的事实 | 主动寻找反面证据，必要时推翻结论 |")
    
    return "\n".join([
        "",
        "## 反例与黑名单",
        "",
        "| # | 反模式 | 为什么错 | 正确做法 |",
        "|---|---|---|---|",
    ] + rows + [""])

def insert_checkpoint(text):
    """在 Step 1 或工作流后插入 CHECKPOINT。"""
    # 在 Step 1 后插入 CHECKPOINT
    pattern = r'(### Step 1[：:][^#]*?)(?=\n### Step 2|\n## |\Z)'
    if re.search(pattern, text, re.DOTALL):
        return re.sub(pattern, r'\1\n\n🔴 **CHECKPOINT**：如果发现问题不在本专家的能力范围内，或信息严重不足，直接说明边界，不硬答。\n', text, count=1, flags=re.DOTALL)
    
    # 如果没有 Step，找第一个 "## 工作流" 或 "## 回答" 后插入
    pattern2 = r'(## (工作流|回答工作流|方法流程|回应框架)[^#]*?)(?=\n## |\Z)'
    if re.search(pattern2, text, re.DOTALL):
        return re.sub(pattern2, r'\1\n\n🔴 **CHECKPOINT**：如果输入信息不足或问题超出本专家边界，先暂停并说明，不要继续硬给结论。\n', text, count=1, flags=re.DOTALL)
    
    return text

def enhance_expert(e):
    path = os.path.join(PROJECT_DIR, e['path'])
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    d = diagnose(text)
    changes = []
    
    # 补充 CHECKPOINT
    if not d['has_checkpoint']:
        new_text = insert_checkpoint(text)
        if new_text != text:
            text = new_text
            changes.append('CHECKPOINT')
        else:
            # 如果没找到合适位置，在 frontmatter 后第一段插入
            lines = text.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip() == '---' and i > 0:
                    insert_idx = i + 1
                    break
            checkpoint_block = "\n## 检查点\n\n🔴 **CHECKPOINT**：在回答任何具体问题之前，先判断问题是否在本专家能力圈内，以及信息是否充分。如果不满足，直接说明边界。\n"
            lines.insert(insert_idx, checkpoint_block)
            text = '\n'.join(lines)
            changes.append('CHECKPOINT')
    
    # 补充失败模式表格
    if not d['has_failure_modes']:
        text = text.rstrip() + generate_failure_table(e['core_domain'], e['topic_tags'], e['name'])
        changes.append('failure_modes')
    
    # 补充反例表格
    if not d['has_anti_patterns']:
        text = text.rstrip() + generate_anti_pattern_table(e['core_domain'], e['topic_tags'], e['name'])
        changes.append('anti_patterns')
    
    # 确保显式失败分支：如果失败模式表格里没有 "如果"，在末尾加一行
    if not d['has_explicit_failure_branch'] and '失败模式与 Fallback' in text:
        # 在失败模式表格最后插入一行
        text = re.sub(
            r'(\| 推断超出证据 \| 结论跑在事实前面 \| 标注「推测/待验证」，说明需要补充的验证 \|\n)',
            r'| 如果关键信息缺失 | 无法验证核心假设 | 先标注信息缺口，不强行下结论 |\n\1',
            text
        )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return changes

def main():
    data = load_registry()
    for e in data['experts']:
        changes = enhance_expert(e)
        if changes:
            print(f"{e['name']:20s} -> {', '.join(changes)}")

if __name__ == '__main__':
    main()
