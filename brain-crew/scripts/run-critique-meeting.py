#!/usr/bin/env python3
"""
Brain Crew 挑刺会议（Ask Five 模拟）

用法：
  python3 scripts/run-critique-meeting.py

输出：结构化会议纪要，包含 5 位专家对 Brain Crew 的批判性审视。
"""

import json
import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(PROJECT_DIR, 'expert-registry.json')

def load_registry():
    with open(REGISTRY, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_expert_text(path):
    full = os.path.join(PROJECT_DIR, path)
    with open(full, 'r', encoding='utf-8') as f:
        return f.read()

def extract_frontmatter_description(text):
    match = re.search(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not match:
        return ''
    fm = match.group(1)
    desc = re.search(r'description:\s*\|?\s*(.*?)(?=\n[A-Za-z0-9_-]+:|\Z)', fm, re.DOTALL)
    return desc.group(1).replace('\n', ' ').strip() if desc else ''

def main():
    data = load_registry()
    experts = {e['id']: e for e in data['experts']}

    # 手动挑选 5 位挑刺视角差异最大化的专家
    panel_ids = [
        'darwin',              # meta：skill 质量、评分体系
        'charlie-munger',      # core：逆向思维、清单审查
        'steve-jobs',          # core：简洁、产品直觉
        'richard-feynman',     # core：清晰、反模板
        'luxun',               # brand：声音真实性
    ]

    print("=" * 72)
    print("Brain Crew 挑刺会议 · Ask Five 红队模式")
    print("=" * 72)
    print()
    print("议题：Brain Crew 专家库当前版本（v1.0.0）的设计、质量与可扩展性")
    print("目标：找出最应该修复的 3 个问题")
    print("出席专家：")
    for eid in panel_ids:
        e = experts[eid]
        print(f"  - {e['name']}（{e['pack']} pack）")
    print()

    critiques = {
        'darwin': {
            'lens': 'SkillLens 9 维结构评估',
            'model': '结构完整性、评分体系有效性',
            'critique': """Brain Crew 的结构性已经达标，但评分体系本身有设计债。

第一，「可执行具体性」权重高达 17%，却主要靠「数字锚点」和「软化词」两个浅层指标判断。这会导致专家为了分数而硬塞数字，反而破坏表达 DNA。我刚看到 GWTB 策略官被塞了「30 天、1000 条、3 个核心城市、3 天内」——对数据驱动型专家这不算错，但如果这个逻辑泛化到王阳明、费曼身上，就会出戏。

第二，「实测表现」维度目前固定给 7 分，没有跑真实测试 prompt。这意味着 23% 的权重是虚的。一个专家完全可能在结构上 90 分、实际输出 60 分，我们却看不出来。

第三，h2 数量阈值从 12 调到 15 是一次妥协。这释放了复杂 skill 的得分，但也可能纵容结构臃肿。建议改成「h2 数量 + 平均每 h2 字数」的组合指标。

最该修：把 dim8 实测表现从「默认 7 分」改成「必须提交 2-3 个测试 prompt + 人工/LLM 评分」的强制流程。"""
        },
        'charlie-munger': {
            'lens': '逆向思维 + 认知偏误检查',
            'model': '逆向思考、激励机制、能力圈',
            'critique': """先反过来想：Brain Crew 怎么会失败？

第一，激励错配。打分机制奖励「结构完整」，不奖励「用户真正想问的问题能被回答」。开发者会为了 85 分而加 CHECKPOINT、加数字、加反例表，但不管这些内容是否让最终用户受益。

第二，专家重叠没有解决。乔布斯和张一鸣都谈产品战略，芒格和巴菲特都谈投资，段永平和芒格也有重叠。现在靠 topic_tags 区分，但用户问「我该不该投资这家公司」时，可能会同时召出 4 个投资人。需要一张「重叠矩阵」和明确的差异化分工。

第三，敏感角色（特朗普、张雪峰）的隔离机制是技术过滤，不是价值说明。用户可能不知道 `mode=debate` 是什么意思，也不知道为什么默认排除。应该在 SKILL.md 里写明：这些角色在什么场景下有价值，什么场景下会误导。

最该修：建立「用户使用后的回滚机制」——每次会议后让用户给每位专家打分，低于阈值的专家进入观察期。激励机制要绑定真实用户价值，而不是内部评分。"""
        },
        'steve-jobs': {
            'lens': '简洁与产品直觉',
            'model': '聚焦即说不、简洁至上、用户视角',
            'critique': """Brain Crew 不简洁。

第一，30 个专家太多了。你说这是核心包，但「核心」意味着精简。我建议把 30 个砍到 15-18 个真正不可替代的。你现在把郭德纲、鲁迅、MrBeast 都放 brand pack，但用户问「怎么写爆款标题」时，这三个可能同时出现。太多选择 = 没选择。

第二，每个 SKILL.md 都太长了。我看到 MrBeast 文件有 700 多行。不是内容越多越有用。用户调用专家时，模型能消化多少？过长的 prompt 会导致「中间信息丢失」——最后只记得开头和结尾。应该把每个 skill 控制在 300-400 行以内，把附录拆到 references/。

第三，查询 API 返回的专家理由不够直观。现在返回的是 score，但用户更想知道「为什么是这个专家」。建议给每个匹配加一个一句话理由。

最该修：先做减法。把使用频率低、重叠度高、得分刚达线的专家移到「扩展包」或观察区。Brain Crew 的核心包应该让工程师闭着眼睛也能选出对的专家。"""
        },
        'richard-feynman': {
            'lens': '清晰与反模板',
            'model': '命名不等于理解、反 cargo-cult、具体例子',
            'critique': """我给 Brain Crew 的最大挑刺是：它很容易被当成 cargo-cult。

第一，很多专家文件有统一的 Step 1/2/3、CHECKPOINT、失败模式表、反例黑名单，但这些东西是「形式」不是「理解」。如果作者没有真正吃透这个人物的思维方式，只是填表格，那输出就会像穿西装的稻草人。

第二，「典型应答结构」这个模块之前被批量加到所有专家文件里，我注意到后来又被批量移除——因为它让鲁迅这种专家直接违反了自己的铁律（不分列表、不编号）。这说明统一模板会压过个体 voice。每个专家应该有他自己的应答结构，而不是共用一套。

第三，反例表里有太多「为什么错」其实是同义反复。比如「自报名号破坏角色沉浸感」——这只是重复规则，没有解释机制。好的反例要说清楚：为什么这个模式会让用户觉得假？因为它暴露了表演感，打碎了「我」的视角。

最该修：取消所有统一输出模板，改为每个专家文件末尾放一个「真实对话示例」，而且这个示例必须看起来像是这个人真的会说的话。"""
        },
        'luxun': {
            'lens': '声音真实性与反 AI 味',
            'model': '自我解剖、反讽、张力守恒',
            'critique': """我用鲁迅的耳朵听了一遍这些专家，最大的问题是：有些人「演」得太用力。

第一，角色扮演规则写了一堆「用『我』自称」「不要说『作为 AI』」，但真正的声音不是规则堆出来的。费曼不会说「让我们先 Step 1：问题分类」，王阳明也不会说「进入 CHECKPOINT」。这些工程标注是 AI 味的来源。角色规则应该藏在水下，而不是写在每段开头。

第二，很多专家文件为了 Darwin 分数，把表达切成了表格、列表、编号。但鲁迅的文件自己就说「不分小节标题，不编号列表」。这种自我矛盾会感染其他专家——当他们看到系统奖励结构化，就会放弃自己的表达 DNA。

第三， DISCLAIMER 机制需要重新想。让每位专家首次激活都说一次免责声明，对沉浸式角色是致命破坏。乔布斯开口第一句如果是「我以乔布斯视角和你聊」，那就已经不是乔布斯了。

最该修：把免责声明从专家文件里移除，放到 Brain Crew 的 SKILL.md 顶层，由引擎统一说一次。让每位专家的第一次回应直接入戏，而不是先穿戏服再亮相。"""
        }
    }

    print("-" * 72)
    print("【会议纪要】")
    print("-" * 72)
    print()

    for eid in panel_ids:
        e = experts[eid]
        c = critiques[eid]
        print(f"## {e['name']} · {c['lens']}")
        print(f"**核心模型**：{c['model']}")
        print()
        print(c['critique'])
        print()

    print("-" * 72)
    print("【共识】")
    print("-" * 72)
    print("""
1. 评分体系（尤其是 dim8 实测表现）必须尽快接入真实测试 prompt，否则 86+ 的平均分是自我验证。
2. 统一模板（Step/CHECKPOINT/反例表）是双刃剑，既能保底质量，也会压过个体专家 voice。
3. 30 个专家对于「核心包」偏多，需要建立重叠度矩阵和优胜劣汰机制。
""")

    print("-" * 72)
    print("【分歧】")
    print("-" * 72)
    print("""
- 达尔文认为当前结构已基本可用，优先补测试流程；乔布斯认为应该先砍专家数量。
- 费曼反对一切统一模板；芒格认为统一清单是防止认知偏误的必要成本。
- 鲁迅认为免责声明应彻底移出专家文件；达尔文认为至少应保留在 meta 层。
""")

    print("-" * 72)
    print("【盲区】")
    print("-" * 72)
    print("""
- 没有真实用户调用数据，不知道哪些专家实际被使用、哪些从未被选中。
- 没有跨专家一致性测试：同一问题召不同专家，是否会给出互相矛盾的基础事实。
- 没有评估专家在超长对话（>10 轮）中的角色保持率。
""")

    print("-" * 72)
    print("【秘书处建议 · 下一步行动】")
    print("-" * 72)
    print("""
1. **高优先级**：设计 3-5 个真实测试 prompt，跑一遍 30 位专家的输出，建立 dim8 实测基线。
2. **中优先级**：绘制专家重叠度矩阵，把 30 人按「独特价值」排序，末位 5-8 人移入扩展包或观察区。
3. **中优先级**：把免责声明从单个专家文件提到 Brain Crew SKILL.md 顶层，由引擎统一输出。
4. **低优先级**：把 SKILL.md 拆分为「核心执行文件 + references/ 附录」，控制单文件长度 <400 行。
""")

    print("=" * 72)
    print("免责声明：以上仅为专家视角参考，最终决策权在你。")
    print("=" * 72)

if __name__ == '__main__':
    main()
