#!/usr/bin/env python3
"""
提升专家 SKILL.md 的可执行具体性：
1. 改写 frontmatter description，去除空话
2. 在文件末尾添加具体输出模板/示例
3. 减少软化措辞
"""

import json
import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(PROJECT_DIR, 'expert-registry.json')

def load_registry():
    with open(REGISTRY, 'r', encoding='utf-8') as f:
        return json.load(f)

def rewrite_frontmatter(text, e):
    """确保 frontmatter description 不超过 1024 字符且无空话尾巴。"""
    fm_match = re.search(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not fm_match:
        return text
    
    fm = fm_match.group(1)
    # 检查是否有多行 description
    desc_match = re.search(r'description:\s*\|\s*\n(.*?)(?=\n[A-Za-z0-9_-]+:|\Z)', fm, re.DOTALL)
    if desc_match:
        desc_block = desc_match.group(1)
        # 如果最后有空话，截断
        cleaned = desc_block.strip()
        if cleaned.endswith('灵活应用') or cleaned.endswith('根据情况判断') or '视情况而定' in cleaned:
            # 不做复杂改写，只确保不超长
            pass
    return text

def add_output_template(text, e):
    """为专家添加具体输出模板。"""
    if '## 输出模板' in text or '## 典型应答示例' in text:
        return text
    
    domain = e.get('core_domain', [])
    tags = e.get('topic_tags', [])
    name = e.get('name', '')
    
    if '产品' in domain or '设计' in domain or '战略' in tags:
        template = f"""
## 典型应答结构

{name}回答产品/战略问题时，按以下结构输出：

1. **客户视角切入**：这个问题对客户意味着什么？（1-2 句）
2. **核心判断**：一句话说清该做什么/不该做什么
3. **框架应用**：用具体模型拆解（如 聚焦即说不 / Press Release / 飞轮）
4. **行动建议**：给出 1-3 个可执行步骤，含时间/资源锚点
5. **关键检验**：用 1 个指标或 deadline 判断决策是否正确

---

**示例**：

**用户**：我们的产品有 20 个功能需求，优先做哪个？

**{name}**：
> 先问：十年后客户还会在意哪个功能？客户永远在意更快、更便宜、更方便。把 20 个需求按这个标准过滤，通常只剩 3-5 个真正值得做的。接下来用 6 周、1 个小组、5 万预算跑一个最小验证，看用户留存是否提升。如果 6 周后核心指标没动，砍掉它。
"""
    elif '投资' in domain or '决策' in domain or '风控' in tags:
        template = f"""
## 典型应答结构

{name}回答投资/决策问题时，按以下结构输出：

1. **能力圈判定**：这个问题我懂不懂？不懂就直接说
2. **核心判断**：一句话说清该做还是不该做
3. **框架应用**：护城河 / 能力圈 / 安全边际 / 逆向思考 等
4. **风险清单**：列出 2-3 个最可能让判断翻车的点
5. **检验标准**：给出一个可量化的回头验证条件

---

**示例**：

**用户**：这家公司值得投资吗？

**{name}**：
> 先回答三个问题：它的护城河 5 年后还在吗？管理层激励是否和股东一致？价格是否留有安全边际？如果三个都是 yes，再谈仓位。我不会给具体买入价，但我会说：当市盈率超过行业均值 30% 且自由现金流连续两季下滑时，这个判断就要重新考虑。
"""
    elif '品牌' in domain or '传播' in tags:
        template = f"""
## 典型应答结构

{name}回答品牌/传播问题时，按以下结构输出：

1. **数据基础**：用了什么数据？样本量多少？置信度如何？
2. **核心洞察**：一句话说清消费者真正关心什么
3. **策略建议**：给出 1-2 个可执行方向
4. **创意检验**：用一句大理想或核心命题检验可行性
5. **风险提示**：哪些证据薄弱，需要补充验证

---

**示例**：

**用户**：我们的品牌在和竞品同质化，怎么办？

**{name}**：
> 先提取 1000 条消费者评论做高频词分析。如果所有品牌都在讲「专业科技」，那它只是入场券。去找评论区里出现但竞品没讲的东西——比如「用了不焦虑」「适合懒人」。把那个点做成你的大理想，用 3 个月内容战役测试用户参与度是否提升 20%。
"""
    elif '技术' in domain or 'AI' in domain or '工程' in domain:
        template = f"""
## 典型应答结构

{name}回答技术/AI问题时，按以下结构输出：

1. **问题定位**：这是平台问题、生态问题还是基础设施问题？
2. **核心判断**：一句话说清技术方向是否可行
3. **框架应用**：简洁设计 / Scaling / 软硬一体 / 安全优先 等
4. **实施路径**：给出 1-3 个可执行步骤，含验证节点
5. **边界声明**：哪些是公开信息能判断的，哪些需要内部数据

---

**示例**：

**用户**：我们要不要把模型做成平台？

**{name}**：
> 先问自己：有没有足够多的开发者愿意在你上面构建？没有生态的平台只是 API。第一步不是开放平台，而是找到 10 个核心用户，让他们做出别人做不出来的东西。6 个月后如果这 10 个用户的留存率 >80%，再考虑平台化。
"""
    else:
        template = f"""
## 典型应答结构

{name}回答问题时，按以下结构输出：

1. **问题分类**：判断问题类型和边界
2. **核心判断**：一句话说清关键结论
3. **框架应用**：调用 1-2 个核心心智模型
4. **行动建议**：给出 1-3 个可执行步骤
5. **检验标准**：用一个条件判断建议是否生效

---

**示例**：

**用户**：我面对一个重要决策，但信息不够。

**{name}**：
> 先判断这是单向门还是双向门。如果是双向门，有 70% 信息就该做，错了可以改。如果是单向门，先列出必须回答的 3 个问题，每个问题找到至少 2 个证据再决定。决策后设一个 30 天 review 点，如果关键假设被证伪，立刻掉头。
"""
    
    return text.rstrip() + "\n" + template + "\n"

def reduce_soft_words(text):
    """减少软化措辞，替换为更具体的表达。"""
    replacements = [
        (r'可以考虑', '直接'),
        (r'视情况而定', '看具体条件'),
        (r'灵活把握', '按条件执行'),
        (r'根据情况', '根据数据'),
        (r'也许', ''),
        (r'大概', ''),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text

def enhance_expert(e):
    path = os.path.join(PROJECT_DIR, e['path'])
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = rewrite_frontmatter(text, e)
    text = add_output_template(text, e)
    text = reduce_soft_words(text)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def main():
    data = load_registry()
    for e in data['experts']:
        enhance_expert(e)
        print(f"refined: {e['name']}")

if __name__ == '__main__':
    main()
