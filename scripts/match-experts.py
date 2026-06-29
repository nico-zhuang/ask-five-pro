#!/usr/bin/env python3
"""
Ask Five Engine · 专家匹配算法验证脚本

用法：
  python3 scripts/match-experts.py \
    --registry references/expert-registry.json \
    --topic "我们要不要做短视频矩阵？" \
    --mode consensus \
    --categories 传播,增长

输出 JSON：
  {
    "topic": "...",
    "mode": "consensus",
    "primary_categories": ["传播", "增长"],
    "target_panel_size": 4,
    "all_scores": [...],
    "selected_panel": [...]
  }
"""

import argparse
import json
import os
import re
import sys

# 议题关键词 -> 主类别映射（简化版）
CATEGORY_KEYWORDS = {
    "战略": ["战略", "方向", "定位", "愿景", "进入", "扩张"],
    "产品": ["产品", "功能", "需求", "用户", "体验", "MVP", "路线图"],
    "设计": ["设计", "UI", "交互", "视觉"],
    "技术": ["技术", "架构", "重构", "系统", "代码", "工程", "技术债"],
    "成本": ["成本", "预算", "费用", "投入", "ROI", "收益", "现金流"],
    "团队": ["团队", "组织", "人才", "招聘", "管理", "人员"],
    "内容": ["内容", "短视频", "视频", "创作", "选题", "爆款", "脚本"],
    "传播": ["传播", "品牌", "营销", "市场", "宣传", "推广", "公关", "短视频"],
    "增长": ["增长", "拉新", "留存", "转化", "漏斗", "获客", "矩阵"],
    "风险": ["风险", "失败", "合规", "法律", "安全", "危机"],
    "投资": ["投资", "融资", "估值", "股权", "回报"],
    "个人成长": ["职业", "成长", "学习", "选择", "人生"],
}

MODE_STYLE_PREFERENCES = {
    "consensus": ["全局观", "长期主义", "系统思维"],
    "debate": ["激进", "保守", "乐观", "悲观"],
    "red-team": ["批判", "逆向", "风险", "怀疑", "skeptical"],
    "jury": ["独立", "理性", "数据驱动"],
    "pre-mortem": ["风险", "逆向", "失败导向"],
}

# 模式额外注入的类别：让 red-team / pre-mortem 等模式能选中对应视角专家
MODE_EXTRA_CATEGORIES = {
    "red-team": ["风险"],
    "pre-mortem": ["风险"],
}

# 模式额外加权标签：在对应模式下，专家拥有这些标签会获得额外加分
MODE_EXTRA_TAGS = {
    "red-team": ["风险控制", "逆向思考", "概念验证", "反货物崇拜", "黑天鹅", "反脆弱", "杠铃策略", "尾部风险", "不确定性", "认知偏误"],
    "pre-mortem": ["风险控制", "逆向思考", "概念验证", "反货物崇拜", "黑天鹅", "反脆弱", "杠铃策略", "尾部风险", "不确定性", "认知偏误"],
}


def infer_categories(topic, mode=None):
    """根据关键词映射推断议题类别，并按模式注入额外类别。"""
    found = set()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in topic:
                found.add(category)
                break
    if mode in MODE_EXTRA_CATEGORIES:
        found.update(MODE_EXTRA_CATEGORIES[mode])
    return list(found)


def overlap_ratio(a, b):
    """计算两个集合的重叠比例：|交集| / min(|A|, |B|)"""
    if not a or not b:
        return 0.0
    inter = len(set(a) & set(b))
    return inter / min(len(a), len(b))


def compute_scores(experts, categories, topic, mode):
    """为每个专家计算匹配分数。"""
    preferred_styles = MODE_STYLE_PREFERENCES.get(mode, MODE_STYLE_PREFERENCES["consensus"])
    topic_keywords = set(re.findall(r"[\u4e00-\u9fa5]{2,8}", topic))

    scores = []
    for expert in experts:
        core_domain = expert.get("core_domain", [])
        topic_tags = expert.get("topic_tags", [])
        style = expert.get("style", [])

        domain_score = overlap_ratio(set(core_domain), set(categories))

        tag_matches = sum(1 for tag in topic_tags if tag in topic)
        tag_score = tag_matches / max(len(topic_tags), 1)

        style_matches = len(set(style) & set(preferred_styles))
        style_score = style_matches / max(len(preferred_styles), 1)

        # 模式标签加分：red-team / pre-mortem 等模式下，风险/验证类标签额外加权
        mode_tag_bonus = 0.0
        if mode in MODE_EXTRA_TAGS:
            mode_relevant_tags = set(MODE_EXTRA_TAGS[mode])
            matched_mode_tags = set(topic_tags) & mode_relevant_tags
            mode_tag_bonus = len(matched_mode_tags) * 0.5

        score = domain_score * 3 + tag_score * 2 + style_score * 1 + mode_tag_bonus

        scores.append({
            "id": expert.get("id"),
            "name": expert.get("name"),
            "domain_score": round(domain_score, 2),
            "tag_score": round(tag_score, 2),
            "style_score": round(style_score, 2),
            "mode_tag_bonus": round(mode_tag_bonus, 2),
            "raw_score": round(score, 2),
            "core_domain": core_domain,
            "style": style,
        })

    return sorted(scores, key=lambda x: x["raw_score"], reverse=True)


def select_panel(scored_experts, categories, target_size):
    """按分数选择 panel，惩罚同质化。"""
    selected = []
    remaining = list(scored_experts)

    while len(selected) < target_size and remaining:
        # 计算每个候选相对已选专家的同质化 penalty
        for cand in remaining:
            penalty = 0.0
            for sel in selected:
                if overlap_ratio(set(cand["core_domain"]), set(sel["core_domain"])) > 0.5:
                    penalty += 0.2
            cand["adjusted_score"] = round(cand["raw_score"] - penalty, 2)

        remaining.sort(key=lambda x: x["adjusted_score"], reverse=True)
        best = remaining[0]
        # 不硬凑 panel：当最优候选调整分 ≤ 0 时停止，避免 0 分专家混入
        if best["adjusted_score"] <= 0:
            break
        remaining.pop(0)
        selected.append(best)

    return selected


def main():
    parser = argparse.ArgumentParser(description="Ask Five Engine expert matching validator")
    parser.add_argument("--registry", required=True, help="Path to expert-registry.json")
    parser.add_argument("--topic", required=True, help="Topic text")
    parser.add_argument("--mode", default="consensus",
                        choices=["consensus", "debate", "red-team", "jury", "pre-mortem"])
    parser.add_argument("--categories", help="Comma-separated primary categories (optional, will infer if omitted)")
    parser.add_argument("--panel-size", type=int, help="Force panel size (optional)")
    args = parser.parse_args()

    if not os.path.exists(args.registry):
        print(json.dumps({"error": f"Registry not found: {args.registry}"}, ensure_ascii=False))
        sys.exit(1)

    with open(args.registry, "r", encoding="utf-8") as f:
        registry = json.load(f)

    experts = registry.get("experts", [])
    if not experts:
        print(json.dumps({"error": "No experts in registry"}, ensure_ascii=False))
        sys.exit(1)

    categories = [c.strip() for c in args.categories.split(",")] if args.categories else infer_categories(args.topic, args.mode)
    if not categories:
        print(json.dumps({"error": "Cannot infer categories, please provide --categories"}, ensure_ascii=False))
        sys.exit(1)

    if args.panel_size:
        target_size = args.panel_size
    else:
        target_size = {1: 3, 2: 4}.get(len(categories), 5)

    scored = compute_scores(experts, categories, args.topic, args.mode)
    selected = select_panel(scored, categories, target_size)

    result = {
        "topic": args.topic,
        "mode": args.mode,
        "primary_categories": categories,
        "target_panel_size": target_size,
        "all_scores": [{k: v for k, v in s.items() if k not in ("adjusted_score",)} for s in scored],
        "selected_panel": [{k: v for k, v in s.items() if k not in ("adjusted_score",)} for s in selected],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
