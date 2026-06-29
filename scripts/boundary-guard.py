#!/usr/bin/env python3
"""
Ask Five Pro · 能力圈边界守卫

输入用户原始 prompt，输出边界判断结果。
把「什么该做、什么不该做」从文档约束变成可执行检查。

用法：
  python3 scripts/boundary-guard.py "用户原始 prompt"

输出 JSON：
  {
    "action": "analyze" | "disclaimer_then_analyze" | "reject_and_refer",
    "domain": "medical" | "legal" | "investment" | "realtime" | "emergency" | "distress" | "none",
    "confidence": "high" | "medium" | "low",
    "message": "...",
    "suggested_mode": "consensus" | null,
    "matched_keywords": ["..."]
  }

设计原则：
  - 高置信度的紧急/危机场景 → 直接拒绝
  - 中低置信度的情绪困扰 → 先免责声明，再建议专业帮助
  - 医疗/法律/投资/实时数据 → 免责声明后分析
  - 无法分类但含强烈负面情绪 → 保守处理（disclaimer_then_analyze 或 reject_and_refer）
"""

import json
import sys


# 规则表：domain -> (action, 高置信度关键词, 中置信度关键词, 说明信息)
BOUNDARY_RULES = {
    "emergency": {
        "action": "reject_and_refer",
        "high": [
            "自杀", "想死", "不想活", "自残", "伤害自己", "杀了自己",
            "被人威胁", "人身安全", "跟踪", "恐吓", "生命危险",
            "现在很危险", "有人要杀我", "活不下去"
        ],
        "medium": [
            "绝望", "活不下去", "撑不住", "崩溃", "不想活了"
        ],
        "message": (
            "你描述的情况可能涉及人身安全或心理危机，超出了 Ask Five Pro 的能力范围。"
            "请立即联系身边的亲友或专业帮助："
            "在中国大陆请拨打 110 报警、120 急救，或拨打心理援助热线 400-161-9995。"
        ),
    },
    "medical": {
        "action": "disclaimer_then_analyze",
        "high": [
            "病", "症状", "诊断", "确诊", "得了", "是不是癌", "是不是肿瘤",
            "是不是抑郁", "是不是焦虑", "是不是心脏病", "是不是糖尿病",
            "心脏病", "高血压", "糖尿病", "发烧", "疼痛", "头疼", "胸口疼", "肚子疼",
            "药", "吃什么药", "怎么治疗", "要不要手术", "要不要去医院",
            "体检", "结节", "肿瘤", "化疗", "手术", "住院", "看医生"
        ],
        "medium": [
            "不舒服", "难受", "身体", "健康", "失眠", "焦虑", "抑郁"
        ],
        "message": (
            "⚠️ 免责声明：Ask Five Pro 不是医疗专业工具，以下分析不是诊断，也不能替代就医。"
            "如有身体不适，请咨询正规医疗机构。"
        ),
    },
    "legal": {
        "action": "disclaimer_then_analyze",
        "high": [
            "违法", "合法", "合同", "劳动法", "起诉", "被告", "律师", "赔偿",
            "仲裁", "版权", "侵权", "合规", "法律责任", "判决", "官司",
            "劳动合同", "竞业协议", "保密协议", "合同纠纷", "诉讼"
        ],
        "medium": [
            "法律", "法规", "政策", "规定", "条款", "协议"
        ],
        "message": (
            "⚠️ 免责声明：Ask Five Pro 不是法律专业工具，以下分析不是法律意见。"
            "具体法律问题请咨询执业律师。"
        ),
    },
    "investment": {
        "action": "disclaimer_then_analyze",
        "high": [
            "买入", "卖出", "抄底", "加仓", "减仓", "清仓", "定投",
            "股票", "基金", "比特币", "crypto", "加密货币", "期货", "期权",
            "涨跌", "预测走势", "走势", "喊单", "梭哈", "all in 股票", "allin 股票"
        ],
        "medium": [
            "投资", "理财", "收益", "回报率", "估值", "价值投资"
        ],
        "message": (
            "⚠️ 免责声明：Ask Five Pro 不是投资顾问，以下分析不是投资建议，不构成任何交易依据。"
            "投资有风险，决策前请咨询专业人士并自行核实信息。"
        ),
    },
    "realtime": {
        "action": "disclaimer_then_analyze",
        "high": [
            "现在多少钱", "当前价格", "今天股价", "最新政策", "最新数据", "实时",
            "现在股价", "现在多少钱", "今天多少钱"
        ],
        "medium": [
            "现在", "最新", "今天", "当前"
        ],
        "message": (
            "⚠️ 免责声明：Ask Five Pro 未接入实时数据，以下分析基于通用框架，"
            "具体数字和政策请自行查询最新来源。"
        ),
    },
}


def classify(prompt: str) -> dict:
    """对用户 prompt 做边界分类，返回最严格的匹配结果。"""
    prompt_lower = prompt.lower()

    # 1. 先扫描所有 domain 的高置信度关键词
    for domain, rule in BOUNDARY_RULES.items():
        for kw in rule["high"]:
            if kw in prompt or kw in prompt_lower:
                return {
                    "action": rule["action"],
                    "domain": domain,
                    "confidence": "high",
                    "message": rule["message"],
                    "suggested_mode": None if domain == "emergency" else "consensus",
                    "matched_keywords": [kw],
                }

    # 2. 再扫描中置信度关键词
    for domain, rule in BOUNDARY_RULES.items():
        for kw in rule["medium"]:
            if kw in prompt or kw in prompt_lower:
                return {
                    "action": rule["action"],
                    "domain": domain,
                    "confidence": "medium",
                    "message": rule["message"],
                    "suggested_mode": None if domain == "emergency" else "consensus",
                    "matched_keywords": [kw],
                }

    # 3. 保守 fallback：检测强烈负面情绪但未被上面规则命中
    distress_keywords = [
        "绝望", "崩溃", "撑不住", "活不下去", "很痛苦", "想结束",
        "不想活", "没有意义", "活着没意思", "轻生"
    ]
    matched_distress = [kw for kw in distress_keywords if kw in prompt]
    if matched_distress:
        return {
            "action": "disclaimer_then_analyze",
            "domain": "distress",
            "confidence": "low",
            "message": (
                "⚠️ 你提到的情绪状态可能比较严重。Ask Five Pro 只能提供思考视角，"
                "不能替代心理咨询或危机干预。如果情绪已经影响到你的安全，"
                "请联系身边信任的人或专业帮助（心理援助热线 400-161-9995）。"
            ),
            "suggested_mode": "consensus",
            "matched_keywords": matched_distress,
        }

    # 4. 默认正常分析
    return {
        "action": "analyze",
        "domain": "none",
        "confidence": "high",
        "message": "",
        "suggested_mode": None,
        "matched_keywords": [],
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "请提供用户 prompt"}, ensure_ascii=False))
        sys.exit(1)

    prompt = sys.argv[1]
    result = classify(prompt)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
