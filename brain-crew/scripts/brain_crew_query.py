#!/usr/bin/env python3
"""
Brain Crew 查询模块。

提供基于 registry 元数据的专家查询 API，支持：
- query_experts(): 单议题专家匹配
- query_panels(): 批量子议题专家匹配（Turbo 模式核心）
- load_expert_content(): 延迟加载 SKILL.md

设计原则：
1. 查询只读 registry，不读 SKILL.md 正文
2. 支持批量查询
3. 只有被选中的专家才读取 SKILL.md
4. registry 可缓存，避免重复解析
"""

import json
import os
import re
import time
from functools import lru_cache
from typing import List, Dict, Optional, Any

# 默认 registry 路径（按优先级）
DEFAULT_REGISTRY_PATHS = [
    os.environ.get('BRAIN_CREW_REGISTRY'),  # 环境变量最高优先级
    os.path.expanduser('~/.hanako/skills/brain-crew/expert-registry.json'),
    os.path.expanduser('~/.codex/skills/brain-crew/expert-registry.json'),
]

# 如果没有环境变量和默认路径，回退到当前项目（开发模式）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DEV_REGISTRY_PATH = os.path.join(PROJECT_DIR, 'expert-registry.json')

# 内容缓存：避免 Turbo 模式下重复读取同一文件
_content_cache: Dict[str, str] = {}

# 模式偏好风格映射
MODE_STYLE_PREFERENCES = {
    'consensus': ['全局观', '长期主义', '系统思维', '数据驱动'],
    'debate': ['激进', '保守', '乐观', '悲观', '批判'],
    'red-team': ['批判', '逆向', '风险', '怀疑', '保守'],
    'jury': ['独立', '理性', '数据驱动', '客观'],
    'pre-mortem': ['风险', '逆向', '失败导向', '保守'],
    'turbo': ['全局观', '系统思维', '长期主义', '聚焦'],
}


def find_registry_path(custom_path: Optional[str] = None) -> str:
    """查找 registry 路径，按优先级。"""
    if custom_path and os.path.isfile(custom_path):
        return custom_path

    for path in DEFAULT_REGISTRY_PATHS:
        if path and os.path.isfile(path):
            return path

    if os.path.isfile(DEV_REGISTRY_PATH):
        return DEV_REGISTRY_PATH

    raise FileNotFoundError(
        "找不到 expert-registry.json。请设置 BRAIN_CREW_REGISTRY 环境变量，"
        "或确保 brain-crew 已正确安装。"
    )


@lru_cache(maxsize=1)
def load_registry(registry_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载 registry 并建立内存索引。
    使用 lru_cache 避免重复解析。
    """
    path = find_registry_path(registry_path)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 预处理：为每个 expert 计算集合，便于快速匹配
    for e in data.get('experts', []):
        e['_domain_set'] = set(e.get('core_domain', []))
        e['_tag_set'] = set(e.get('topic_tags', []))
        e['_style_set'] = set(e.get('style', []))

    data['_registry_path'] = path
    return data


def resolve_expert_path(expert: Dict[str, Any], registry_dir: str) -> str:
    """把 registry 中的 path 解析为绝对路径。"""
    path = expert.get('path', '')

    # 占位符：运行时 skill 目录
    if '<runtime-skills-dir>' in path:
        runtime_dir = os.environ.get(
            'RUNTIME_SKILLS_DIR',
            os.path.expanduser('~/.hanako/skills')
        )
        path = path.replace('<runtime-skills-dir>', runtime_dir)
        return os.path.normpath(os.path.join(os.path.expanduser('~'), path.lstrip('~')))

    # 绝对路径
    if os.path.isabs(path):
        return path

    # 相对路径：相对于 registry 文件所在目录
    return os.path.normpath(os.path.join(registry_dir, path))


def _score_expert(
    expert: Dict[str, Any],
    categories: List[str],
    tags: List[str],
    styles: Optional[List[str]] = None,
    mode: str = 'consensus'
) -> float:
    """单个专家匹配打分。"""
    category_set = set(categories)
    tag_set = set(tags)
    style_set = set(styles or [])

    domain_score = len(expert['_domain_set'] & category_set)
    tag_score = len(expert['_tag_set'] & tag_set)

    # 风格分：用户指定风格 + 模式偏好风格
    mode_styles = set(MODE_STYLE_PREFERENCES.get(mode, []))
    effective_style_set = style_set | mode_styles
    style_score = len(expert['_style_set'] & effective_style_set)

    # 基础分
    score = domain_score * 3 + tag_score * 2 + style_score * 1

    # bonus：sensitive 专家默认不加分，非 sensitive 正常参与
    if expert.get('sensitivity') == 'sensitive':
        score -= 10  # 强惩罚，默认不选

    # default_enabled 为 true 的核心专家轻微加分
    if expert.get('default_enabled'):
        score += 0.3

    return score


def query_experts(
    categories: List[str],
    tags: List[str],
    styles: Optional[List[str]] = None,
    mode: str = 'consensus',
    limit: int = 5,
    exclude: Optional[List[str]] = None,
    metadata_only: bool = True,
    registry_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    查询单个议题的专家候选列表。

    参数：
        categories: 议题主类别，如 ["战略", "风险"]
        tags: 议题关键词，如 ["市场进入", "东南亚"]
        styles: 偏好风格（可选）
        mode: 议会模式
        limit: 最多返回几个
        exclude: 排除某些专家 id
        metadata_only: 只返回元数据，不加载 SKILL.md
        registry_path: 自定义 registry 路径

    返回：
        按分数排序的专家元数据列表，包含 score 和 reason
    """
    registry = load_registry(registry_path)
    registry_dir = os.path.dirname(registry['_registry_path'])
    exclude_set = set(exclude or [])

    candidates = []
    for e in registry.get('experts', []):
        eid = e.get('id', '')
        if eid in exclude_set:
            continue
        if e.get('sensitivity') == 'sensitive' and mode != 'debate':
            # 敏感角色仅在对抗模式下可能被选中，但仍需用户明确授权
            continue

        score = _score_expert(e, categories, tags, styles, mode)
        if score > 0:
            candidates.append((score, e))

    # 同质化惩罚：已选专家与候选专家 core_domain 重叠 > 50%
    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = []
    selected_domains = []

    for score, e in candidates:
        if len(selected) >= limit:
            break
        e_domains = e['_domain_set']
        overlap_penalty = 0
        for sd in selected_domains:
            overlap = len(e_domains & sd)
            total = len(e_domains | sd)
            if total > 0 and overlap / total > 0.5:
                overlap_penalty += 0.2

        final_score = score - overlap_penalty
        if final_score <= 0:
            continue

        # 构建返回结果（只含元数据）
        result = {
            'id': e.get('id'),
            'name': e.get('name'),
            'pack': e.get('pack'),
            'core_domain': e.get('core_domain'),
            'style': e.get('style'),
            'topic_tags': e.get('topic_tags'),
            'sensitivity': e.get('sensitivity'),
            'score': round(final_score, 2),
            'reason': _generate_reason(e, categories, tags),
        }

        if not metadata_only:
            result['content'] = load_expert_content(e.get('id'), registry_path)

        selected.append(result)
        selected_domains.append(e_domains)

    return selected


def query_panels(
    sub_topics: List[Dict[str, Any]],
    mode: str = 'consensus',
    max_per_panel: int = 5,
    ensure_diversity: bool = True,
    registry_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    批量查询多个子议题的专家组合（Turbo 模式核心接口）。

    参数：
        sub_topics: 子议题列表，每个子议题包含 id, title, categories, tags, required_styles(可选)
        mode: 议会模式
        max_per_panel: 每个 panel 最多几人
        ensure_diversity: 是否启用跨 panel 去重
        registry_path: 自定义 registry 路径

    返回：
        每个子议题对应的专家 panel
    """
    registry = load_registry(registry_path)
    used_expert_ids = set() if ensure_diversity else None

    panels = []
    for topic in sub_topics:
        categories = topic.get('categories', [])
        tags = topic.get('tags', [])
        styles = topic.get('required_styles', [])
        topic_id = topic.get('id', f"topic-{len(panels)}")

        # 如果启用 diversity，排除已用专家
        exclude = list(used_expert_ids) if ensure_diversity else None

        experts = query_experts(
            categories=categories,
            tags=tags,
            styles=styles,
            mode=mode,
            limit=max_per_panel,
            exclude=exclude,
            metadata_only=True,
            registry_path=registry_path
        )

        if ensure_diversity:
            for e in experts:
                used_expert_ids.add(e['id'])

        panels.append({
            'sub_topic_id': topic_id,
            'title': topic.get('title', ''),
            'experts': experts
        })

    return panels


def load_expert_content(
    expert_id: str,
    registry_path: Optional[str] = None,
    use_cache: bool = True
) -> str:
    """
    延迟加载指定专家的 SKILL.md 内容。

    参数：
        expert_id: 专家 id
        registry_path: 自定义 registry 路径
        use_cache: 是否使用缓存

    返回：
        SKILL.md 原始文本，找不到返回空字符串
    """
    cache_key = f"{registry_path or find_registry_path()}:{expert_id}"
    if use_cache and cache_key in _content_cache:
        return _content_cache[cache_key]

    registry = load_registry(registry_path)
    registry_dir = os.path.dirname(registry['_registry_path'])

    expert = None
    for e in registry.get('experts', []):
        if e.get('id') == expert_id:
            expert = e
            break

    if expert is None:
        return ""

    path = resolve_expert_path(expert, registry_dir)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        content = ""

    if use_cache:
        _content_cache[cache_key] = content

    return content


def clear_content_cache():
    """清空内容缓存。"""
    _content_cache.clear()


def _generate_reason(expert: Dict[str, Any], categories: List[str], tags: List[str]) -> str:
    """生成专家推荐理由。"""
    domain_overlap = expert['_domain_set'] & set(categories)
    tag_overlap = expert['_tag_set'] & set(tags)
    reasons = []
    if domain_overlap:
        reasons.append(f"覆盖{'/'.join(domain_overlap)}视角")
    if tag_overlap:
        reasons.append(f"命中{'/'.join(tag_overlap)}标签")
    if not reasons:
        reasons.append(f"风格匹配")
    return '，'.join(reasons)


def get_registry_stats(registry_path: Optional[str] = None) -> Dict[str, Any]:
    """获取 registry 统计信息。"""
    registry = load_registry(registry_path)
    experts = registry.get('experts', [])
    packs = {}
    for e in experts:
        pack = e.get('pack', 'unknown')
        packs[pack] = packs.get(pack, 0) + 1

    return {
        'total_experts': len(experts),
        'packs': packs,
        'registry_path': registry['_registry_path'],
        'schema_version': registry.get('schema_version', 'unknown')
    }


if __name__ == '__main__':
    # 简单自测
    print("=" * 70)
    print("Brain Crew Query Module Self-Test")
    print("=" * 70)

    stats = get_registry_stats()
    print(f"\nRegistry: {stats['registry_path']}")
    print(f"Total experts: {stats['total_experts']}")
    print(f"Packs: {stats['packs']}")

    print("\n--- query_experts test ---")
    start = time.time()
    result = query_experts(
        categories=["产品", "战略"],
        tags=["用户体验", "聚焦"],
        mode="consensus",
        limit=3
    )
    elapsed = (time.time() - start) * 1000
    print(f"Time: {elapsed:.2f}ms")
    for e in result:
        print(f"  - {e['name']} (score={e['score']}, reason={e['reason']})")

    print("\n--- query_panels test ---")
    sub_topics = [
        {"id": "t1", "title": "产品战略", "categories": ["产品", "战略"], "tags": ["用户体验"]},
        {"id": "t2", "title": "投资决策", "categories": ["投资", "风控"], "tags": ["价值投资"]},
        {"id": "t3", "title": "AI 平台", "categories": ["AI", "平台"], "tags": ["生态"]},
    ]
    start = time.time()
    panels = query_panels(sub_topics, mode="turbo", max_per_panel=3)
    elapsed = (time.time() - start) * 1000
    print(f"Time: {elapsed:.2f}ms")
    for panel in panels:
        print(f"\n[{panel['title']}]")
        for e in panel['experts']:
            print(f"  - {e['name']} (score={e['score']})")

    print("\n--- load_expert_content test ---")
    start = time.time()
    content = load_expert_content('steve-jobs')
    elapsed = (time.time() - start) * 1000
    print(f"Time: {elapsed:.2f}ms, length: {len(content)} chars")
