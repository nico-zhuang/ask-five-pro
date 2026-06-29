#!/usr/bin/env python3
"""
达尔文快速评分（简化版）
基于 Darwin Skill 2.0 的 9 维 rubric，对 core pack 专家做快速结构评分。
注意：这不是完整的 Darwin 评分（无子 agent 盲测、无多测试 prompt 验证），
仅用于快速发现结构问题和定位改进方向。
"""

import json
import os
import re
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(PROJECT_DIR, 'expert-registry.json')
PACKS_DIR = os.path.join(PROJECT_DIR, 'packs')

# 9 维 rubric 权重（来自 Darwin Skill 2.0）
RUBRIC = {
    'frontmatter':      {'weight': 7,  'name': 'Frontmatter质量'},
    'workflow':         {'weight': 12, 'name': '工作流清晰度'},
    'failure_modes':    {'weight': 12, 'name': '失败模式编码'},
    'checkpoints':      {'weight': 6,  'name': '检查点设计'},
    'actionable':       {'weight': 17, 'name': '可执行具体性'},
    'resources':        {'weight': 4,  'name': '资源整合度'},
    'architecture':     {'weight': 12, 'name': '整体架构'},
    'measured':         {'weight': 23, 'name': '实测表现'},
    'anti_patterns':    {'weight': 6,  'name': '反例与黑名单'},
}


def read_skill(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_frontmatter(text):
    m = re.search(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line and not line.strip().startswith('#'):
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip()
    return fm


def score_frontmatter(text, fm):
    score = 10
    required = ['id', 'name', 'pack', 'core_domain', 'style', 'topic_tags', 'sensitivity', 'version']
    missing = [k for k in required if k not in fm]
    if missing:
        score -= 2 * len(missing)

    # 提取 frontmatter 区域
    fm_match = re.search(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not fm_match:
        return max(1, score - 2)

    fm_text = fm_match.group(1)
    # 匹配多行 description
    desc_match = re.search(r'description:\s*\|?\s*(.*?)(?=\n[A-Za-z0-9_-]+:|\Z)', fm_text, re.DOTALL)
    if desc_match:
        d = desc_match.group(1).replace('\n', ' ').strip()
        if len(d) > 1024:
            score -= 1
        if d.endswith('灵活应用') or d.endswith('根据情况判断') or '视情况而定' in d:
            score -= 2
        # bonus：description 包含做什么 + 何时用 + 触发词，且长度适中
        has_what = bool(re.search(r'用途|作为|用于|触发|当用户', d))
        has_when = bool(re.search(r'当|如果|涉及|适合', d))
        has_trigger = bool(re.search(r'触发|提到|说|问', d))
        if has_what and has_when and has_trigger and len(d) < 512:
            score = min(10, score + 1)
    else:
        score -= 2
    return max(1, score)

def score_workflow(text):
    score = 10
    has_step1 = bool(re.search(r'Step 1[:：]', text))
    has_step2 = bool(re.search(r'Step 2[:：]', text))
    has_step3 = bool(re.search(r'Step 3[:：]', text))
    if not (has_step1 and has_step2 and has_step3):
        score -= 3
    if not re.search(r'## 回答工作流|回答工作流', text):
        score -= 2
    return max(1, score)


def score_failure_modes(text):
    score = 10
    has_failure = bool(re.search(r'失败模式|Fallback|fallback|错误处理', text))
    if not has_failure:
        score -= 4
    has_explicit_branch = bool(re.search(r'如果.*失败|如果.*异常|如果.*未安装', text))
    if not has_explicit_branch:
        score -= 2
    return max(1, score)


def score_checkpoints(text):
    score = 10
    cp_count = len(re.findall(r'CHECKPOINT|🛑 STOP|STOP', text))
    if cp_count == 0:
        score -= 4
    elif cp_count < 2:
        score -= 1
    return max(1, score)


def score_actionable(text):
    # 可执行具体性：粗略统计软化措辞和数字锚点
    score = 10
    soft_words = re.findall(r'建议|可以考虑|根据情况|灵活把握|视情况而定|也许|大概', text)
    score -= min(3, len(soft_words) // 5)
    # 数字锚点：预算、时间、人数、指标等
    anchors = len(re.findall(r'\d+\s*(万|千|百|人|天|周|月|年|%)', text))
    if anchors < 3:
        score -= 1
    if anchors < 1:
        score -= 2
    return max(1, score)


def score_resources(text):
    score = 6
    # 检查是否引用 references、scripts、assets
    if re.search(r'references/|scripts/|assets/', text):
        score += 2
    # 检查是否依赖外部 skill
    if re.search(r'web_search|web_fetch|browser|子agent|subagent', text, re.I):
        score += 2
    return min(10, score)


def score_architecture(text):
    score = 10
    # 检查冗余 AI 腔
    fluff = re.findall(r'说白了|换句话说|首先|其次|综上|总而言之|不难发现', text)
    score -= min(3, len(fluff) // 5)
    # 检查是否有清晰一级/二级标题
    h2_count = len(re.findall(r'\n## ', text))
    if h2_count < 3:
        score -= 2
    if h2_count > 15:
        score -= 2
    return max(1, score)


def score_measured(text, expert_name, expert_id=None, project_dir=None):
    """
    实测表现评分：基于 LLM 批量生成的真实输出质量评估。
    """
    if project_dir is None:
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    tests_file = os.path.join(project_dir, 'tests', 'real-prompt-tests.json')
    results_file = os.path.join(project_dir, 'tests', 'real-prompt-test-results.json')
    eval_file = os.path.join(project_dir, 'tests', 'llm-output-evaluation.json')

    score = 5  # 基准分：未建立实测流程

    if os.path.exists(tests_file):
        score += 0.5  # 有测试 prompt 设计

    if os.path.exists(results_file):
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            avg_match = results.get('avg_match_score', 0)
            coverage = results.get('coverage_rate', 0)
            if avg_match >= 0.8:
                score += 0.5
            if coverage >= 0.8:
                score += 0.5
        except Exception:
            pass

    # 读取 LLM 输出质量评分
    if os.path.exists(eval_file):
        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                eval_data = json.load(f)
            # 找到当前专家对应的评估文件
            expert_key = None
            for filename in eval_data.get('files', {}):
                # 文件名格式: <expert-id>_llm.md 或 <expert-id>_llm-pilot.md
                base = filename.replace('_llm-pilot.md', '').replace('_llm.md', '')
                # 优先用 expert_id 精确匹配
                if expert_id and base == expert_id:
                    expert_key = filename
                    break
                # fallback：用名字模糊匹配
                if base.replace('-', '') in expert_name.replace(' ', '').lower() or \
                   expert_name.lower().replace(' ', '') in base.replace('-', ''):
                    expert_key = filename
                    break
            if expert_key:
                avg_quality = eval_data['files'][expert_key].get('avg_score', 0)
                # 质量分 0-10 映射到 0-3.5 分加成
                score += (avg_quality / 10) * 3.5
        except Exception:
            pass

    return min(10, max(1, round(score)))


def score_anti_patterns(text):
    score = 10
    has_blacklist = bool(re.search(r'反模式|反例|黑名单|不要做|禁止', text))
    if not has_blacklist:
        score -= 4
    # 检查是否有"为什么错 / 正确做法"表格
    if re.search(r'为什么错.*正确做法|正确做法.*为什么错', text, re.DOTALL):
        score += 1
    return min(10, max(1, score))


def main():
    import sys
    target_pack = sys.argv[1] if len(sys.argv) > 1 else 'core'
    
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    filtered_experts = registry['experts'] if target_pack == 'all' else [e for e in registry['experts'] if e.get('pack') == target_pack]

    print("=" * 70)
    if target_pack == 'all':
        print("Brain Crew 全量专家 · 达尔文快速评分（简化版）")
    else:
        print(f"Brain Crew {target_pack} Pack · 达尔文快速评分（简化版）")
    print("=" * 70)
    print("")
    print("说明：本评分为结构快速检查，非完整 Darwin 评分。")
    print("实测表现（dim8）因无法自动跑测试 prompt，暂给基准分 7/10。")
    print("")

    if not filtered_experts:
        print(f"未找到 pack={target_pack} 的专家")
        return

    total_scores = []

    for expert in filtered_experts:
        path = expert['path']
        if '<runtime-skills-dir>' in path:
            runtime_dir = os.environ.get('RUNTIME_SKILLS_DIR', os.path.expanduser('~/.hanako/skills'))
            path = path.replace('<runtime-skills-dir>', runtime_dir)
        elif not os.path.isabs(path):
            path = os.path.join(PROJECT_DIR, path)
        text = read_skill(path)
        fm = parse_frontmatter(text)

        scores = {
            'frontmatter': score_frontmatter(text, fm),
            'workflow': score_workflow(text),
            'failure_modes': score_failure_modes(text),
            'checkpoints': score_checkpoints(text),
            'actionable': score_actionable(text),
            'resources': score_resources(text),
            'architecture': score_architecture(text),
            'measured': score_measured(text, expert['name'], expert['id'], PROJECT_DIR),
            'anti_patterns': score_anti_patterns(text),
        }

        total = sum(scores[k] * RUBRIC[k]['weight'] for k in scores) / 10
        total_scores.append((expert['name'], total))

        print(f"【{expert['name']}】总分: {total:.1f}/100")
        for k in scores:
            dim = RUBRIC[k]
            print(f"  {dim['name']:12s} {scores[k]:2d}/10 × {dim['weight']:2d} = {scores[k] * dim['weight'] / 10:.1f}")
        print("")

    avg = sum(s for _, s in total_scores) / len(total_scores)
    print("-" * 70)
    if target_pack == 'all':
        print(f"全量平均分: {avg:.1f}/100")
    else:
        print(f"{target_pack} Pack 平均分: {avg:.1f}/100")
    print("-" * 70)
    print("")
    print("改进建议：")
    print("1. 实测表现维度需要手动设计 2-3 个测试 prompt 并跑分。")
    print("2. 部分专家可补充更明确的'反例黑名单'表格。")
    print("3. 检查软化措辞（建议/可以考虑/视情况而定）是否过度使用。")
    print("3. 检查软化措辞（建议/可以考虑/视情况而定）是否过度使用。")


if __name__ == '__main__':
    main()
