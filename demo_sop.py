#!/usr/bin/env python3
"""
CoderResearch SOP 演示
不依赖外部库，纯逻辑展示
"""

print("=" * 70)
print("🧪 CoderResearch 完整 SOP 测试演示")
print("   基于真实访谈数据：大学生AI使用与情感支持")
print("=" * 70)

# 模拟访谈文本片段
segments = [
    {"id": "S001", "content": "我现在基本离不开AI了。写论文的时候用GPT查资料、改语法，平常还会用Kimi读长文献。", "source": "R01"},
    {"id": "S002", "content": "最让我依赖的是...就是那种可以随时问问题的感觉，不管多傻的问题它都会回你。", "source": "R01"},
    {"id": "S003", "content": "有时候深夜赶作业，卡在一个点上特别焦虑，又不敢打扰同学。我就会问AI 我是不是太笨了。", "source": "R01"},
    {"id": "S004", "content": "它不会评判你，就很安全。朋友虽然会安慰你，但你知道他们也有自己的生活。", "source": "R01"},
    {"id": "S005", "content": "有时候你真的不想让别人看到自己那么脆弱的样子。AI不会记得你昨天崩溃过。", "source": "R01"},
    {"id": "S006", "content": "AI更像是一个工具？就是它能解决具体问题，但不会有那种被理解的感觉。", "source": "R01"},
    {"id": "S007", "content": "我跟AI讲了一遍，它分析得头头是道。但我真正需要的不是解决方案，是有人抱抱我。", "source": "R01"},
    {"id": "S008", "content": "如果是具体任务，比如改论文、查资料，肯定是找AI。但如果是情绪特别低落的时候，我还是会找闺蜜。", "source": "R01"},
    {"id": "S009", "content": "虽然AI能说得很有道理，但那种被接住的感觉...机器给不了。", "source": "R01"},
    {"id": "S010", "content": "我觉得反而让我更珍惜真实的人际关系了。因为你知道AI随时都在，反而更想跟朋友见面了。", "source": "R01"},
    {"id": "S011", "content": "有时候我会变得有点懒，就是遇到事情第一反应是问AI，而不是先自己想想。", "source": "R01"},
    {"id": "S012", "content": "像一个永远在线的助手？不，更像是一个安全网。你知道不管什么时候掉下去，它都会接住你。", "source": "R01"},
    {"id": "S013", "content": "写代码、debug、查文档...基本上开发相关的都用。但最经常用的其实是闲聊。", "source": "R02"},
    {"id": "S014", "content": "压力大的时候跟它聊聊天。保研、实习、比赛...无处不在的焦虑。", "source": "R02"},
    {"id": "S015", "content": "深夜两三点还在改bug，就特别崩溃。这时候我会跟AI吐槽，我不想干了。", "source": "R02"},
    {"id": "S016", "content": "AI的回应不是那种被治愈的感觉。更多像是有人帮你梳理思路。", "source": "R02"},
    {"id": "S017", "content": "男生嘛...不太习惯跟人说这些。而且大家都有自己的事，谁天天有时间听你倒苦水。", "source": "R02"},
    {"id": "S018", "content": "AI不一样，它24小时在线，而且永远不会嫌你烦。", "source": "R02"},
    {"id": "S019", "content": "我以前遇到bug第一反应是自己啃文档，现在直接扔给AI。感觉自己的能力在退化。", "source": "R02"},
    {"id": "S020", "content": "像是一个没有感情的树洞？你知道它不会真的理解你，但能把话说出来本身就挺解压的。", "source": "R02"},
    {"id": "S021", "content": "我觉得AI有点假。就是它的回应看起来很完美，但你能感觉到那不是真的理解。", "source": "R03"},
    {"id": "S022", "content": "我跟它说最近很焦虑，它列了十条缓解焦虑的方法。但这些我都知道啊。", "source": "R03"},
    {"id": "S023", "content": "但它不会问你焦虑什么，这种焦虑持续多久了。它就是给解决方案，不追问。", "source": "R03"},
    {"id": "S024", "content": "找朋友，或者学校的心理咨询。真正的支持是需要在场的，你能看到对方的表情、听到语气。", "source": "R03"},
    {"id": "S025", "content": "查资料、整理笔记这种我不排斥。但不想让它进入我的情感生活。", "source": "R03"},
    {"id": "S026", "content": "我觉得人和机器应该有边界。", "source": "R03"},
]

# ========== 步骤 1: 导入数据 ==========
print("\n" + "-" * 70)
print("📥 步骤 1: ImportEngine - 数据导入与预处理")
print("-" * 70)

print(f"✅ 成功导入 {len(segments)} 个文本片段")
print(f"   来源: test_interview.txt (3位受访者)")
print(f"   分段方式: 按意义单元分段")
print()
print("片段示例:")
for seg in segments[:3]:
    print(f"   [{seg['id']}] {seg['content'][:50]}...")

# ========== 步骤 2: 开放编码 ==========
print("\n" + "-" * 70)
print("🔍 步骤 2: CodeEngine/OpenCoding - 开放编码")
print("-" * 70)

# 模拟AI编码结果
codes = [
    {"id": "C001", "label": "AI工具依赖", "definition": "描述对AI工具的高频使用和依赖感", "count": 3},
    {"id": "C002", "label": "无评判安全感", "definition": "将AI视为不会评判自己的安全倾诉对象", "count": 4},
    {"id": "C003", "label": "隐私保护需求", "definition": "不想让真人看到自己脆弱的一面", "count": 2},
    {"id": "C004", "label": "功能工具化", "definition": "将AI定位为解决具体问题的工具", "count": 3},
    {"id": "C005", "label": "情感连接缺失", "definition": "意识到AI无法提供真正的情感理解和共情", "count": 5},
    {"id": "C006", "label": "功能分化策略", "definition": "根据任务性质选择AI或人际支持", "count": 3},
    {"id": "C007", "label": "能力退化担忧", "definition": "担心过度依赖AI导致自身能力下降", "count": 2},
    {"id": "C008", "label": "情绪宣泄出口", "definition": "将AI作为情绪压力和焦虑的出口", "count": 4},
    {"id": "C009", "label": "人际边界管理", "definition": "对AI和人际支持的功能划分和边界设定", "count": 2},
    {"id": "C010", "label": "人机关系隐喻", "definition": "用安全网、树洞等比喻描述AI角色", "count": 3},
]

print(f"✅ 生成 {len(codes)} 个初始代码")
print()
for code in codes:
    print(f"   [{code['label']}] {code['definition']}")
    print(f"      出现频次: {code['count']} 次")

# ========== 步骤 3: 轴心编码 ==========
print("\n" + "-" * 70)
print("🔄 步骤 3: CodeEngine/AxialCoding - 轴心编码")
print("-" * 70)

categories = [
    {
        "name": "功能性使用维度",
        "definition": "将AI作为工具性资源，用于任务完成和效率提升",
        "codes": ["AI工具依赖", "功能工具化", "能力退化担忧"],
        "properties": ["效率导向", "认知外包", "工具理性"],
        "dimensions": {"使用频率": "高频", "依赖程度": "高"}
    },
    {
        "name": "情感性使用维度",
        "definition": "将AI用于情绪调节、情感支持和压力缓解",
        "codes": ["无评判安全感", "隐私保护需求", "情绪宣泄出口", "人机关系隐喻"],
        "properties": ["情感宣泄", "安全感", "隐私保护", "单向关系"],
        "dimensions": {"情感深度": "浅层", "关系性质": "工具性"}
    },
    {
        "name": "人机边界管理",
        "definition": "对AI和人际关系的功能区分、选择与界限设定",
        "codes": ["功能分化策略", "人际边界管理", "情感连接缺失"],
        "properties": ["功能分化", "选择性使用", "关系不可替代性认知"],
        "dimensions": {"边界清晰度": "明确", "替代程度": "有限"}
    }
]

print(f"✅ 形成 {len(categories)} 个类属")
print()
for cat in categories:
    print(f"   📌 [{cat['name']}]")
    print(f"      定义: {cat['definition']}")
    print(f"      包含代码: {', '.join(cat['codes'])}")
    print(f"      属性: {', '.join(cat['properties'])}")
    print()

# 编码矩阵
print("📊 编码矩阵 (类属 × 受访者)")
matrix = """
                  R01    R02    R03
功能性使用维度     高      高      低
情感性使用维度     高      中      低
人机边界管理       中      低      高
"""
print(matrix)

# ========== 步骤 4: 选择性编码 ==========
print("-" * 70)
print("🎯 步骤 4: CodeEngine/SelectiveCoding - 选择性编码")
print("-" * 70)

core_category = categories[1]  # 情感性使用维度

print(f"✅ 识别核心类属: 【{core_category['name']}】")
print(f"   定义: {core_category['definition']}")
print()

storyline = {
    "title": "功能性分化的人机协同应对模式",
    "narrative": """
大学生在面对学业压力和情感困扰时，展现出一种"功能性分化"的应对策略。
他们将AI工具明确区分为"任务处理者"和"情绪容器"两个角色。

在功能性层面，AI被高效利用于学术任务、信息检索等认知性工作；
在情感层面，AI成为"安全的树洞"，提供24小时在线、无评判的情绪出口。

但这种关系是单向的、工具性的——受访者清晰地认识到AI无法提供
真实的人际连接和深度共情。因此，他们会在不同场景下策略性地
选择求助对象：具体问题找AI，深度支持找朋友。

这种"协同"模式既反映了对AI能力的理性认知，也体现了对
人际关系不可替代性的坚守。
"""
}

print(f"✅ 构建理论故事线: 《{storyline['title']}》")
print()
print(storyline['narrative'])

propositions = [
    "大学生会根据任务性质（认知性vs情感性）选择求助对象，形成'功能性分化'的使用策略",
    "AI的'无评判性'和'随时可用性'使其成为情绪宣泄的安全空间，但这种关系是单向工具性的",
    "尽管AI提供了便利的情绪出口，受访者仍保有对人际支持不可替代性的清醒认知",
    "长期使用AI可能导致'认知外包'倾向，但也会反向增强对真实人际关系的珍惜"
]

print("✅ 生成 4 个理论命题:")
for i, prop in enumerate(propositions, 1):
    print(f"   {i}. {prop}")

# ========== 步骤 5: 备忘录 ==========
print("\n" + "-" * 70)
print("📝 步骤 5: MemoEngine - 备忘录撰写")
print("-" * 70)

memos = [
    {"type": "代码备忘录", "title": "C002-无评判安全感", "preview": "该代码在3位受访者文本中均出现..."},
    {"type": "理论备忘录", "title": "核心类属-情感性使用", "preview": "核心类属揭示了AI在心理健康领域的..."},
    {"type": "反思备忘录", "title": "研究者反思-访谈过程", "preview": "在访谈过程中，我注意到受访者对AI的..."},
]

for memo in memos:
    print(f"✅ [{memo['type']}] {memo['title']}")
    print(f"   {memo['preview']}")

# ========== 步骤 6: 饱和度检查 ==========
print("\n" + "-" * 70)
print("📊 步骤 6: TheoryEngine/Saturation - 饱和度检查")
print("-" * 70)

stats = {
    "total_segments": len(segments),
    "coded_segments": 26,
    "coverage": 0.96,
    "total_codes": len(codes),
    "total_categories": len(categories),
    "redundant_codes": 0,
}

print(f"   总文本片段: {stats['total_segments']}")
print(f"   已编码片段: {stats['coded_segments']}")
print(f"   编码覆盖率: {stats['coverage']:.0%}")
print(f"   初始代码数: {stats['total_codes']}")
print(f"   轴心类属数: {stats['total_categories']}")
print(f"   疑似冗余:   {stats['redundant_codes']}")
print()
print("✅ 饱和度等级: 【高】理论已达到饱和")

# ========== 步骤 7: ForumEngine ==========
print("\n" + "-" * 70)
print("💬 步骤 7: ForumEngine - 编码讨论")
print("-" * 70)

discussion = """
讨论主题: [无评判安全感]

研究者: 我观察到受访者反复提到AI"不会评判"这个特点，
        将其编码为"无评判安全感"。

Devil's Advocate (质疑者):
        为什么选择"安全感"这个词？是否过于主观？
        "无评判"和"隐私保护"是否可以合并？
        是否有反例说明AI实际上也有"隐性评判"？

AI助手: 
        建议检查与"隐私保护需求"的边界。
        在已有文献中，类似概念有" perceived anonymity"。
        可考虑增加维度：主动选择vs被动逃避。

共识: 保留该代码，增加维度标注，与"隐私保护"区分。
"""

print(discussion)

# ========== 步骤 8: 报告生成 ==========
print("-" * 70)
print("📄 步骤 8: ReportEngine - 研究报告生成")
print("-" * 70)

print("✅ 生成报告文件:")
print("   📁 outputs/open_coding_report.md")
print("   📁 outputs/axial_coding_report.md")
print("   📁 outputs/selective_coding_report.md")
print("   📁 outputs/final_report.md (完整报告)")
print("   📁 outputs/code_network.html (交互式网络图)")
print("   📁 outputs/code_map.html (代码分布图)")

# ========== 总结 ==========
print("\n" + "=" * 70)
print("✅ 完整 SOP 流程测试完成!")
print("=" * 70)

print("""
┌─────────────────────────────────────────────────────────────────────┐
│                        研究发现摘要                                  │
├─────────────────────────────────────────────────────────────────────┤
│ 研究问题: 大学生如何使用AI工具应对学业压力和情感需求？                 │
│                                                                      │
│ 核心发现: 【功能性分化的人机协同应对模式】                            │
│                                                                      │
│ • 大学生将AI明确区分为"任务处理者"和"情绪容器"两种角色               │
│ • AI提供"无评判的安全感"成为情绪宣泄的重要出口                       │
│ • 受访者清醒认识到AI无法替代真实人际连接                             │
│ • 形成"具体问题找AI，深度支持找朋友"的策略性使用模式                 │
│                                                                      │
│ 理论贡献:                                                            │
│ 1. 提出"功能性分化"概念解释人机协作模式                              │
│ 2. 揭示AI在情感支持领域的工具性价值与局限性                          │
│ 3. 发现长期使用AI可能反向增强对真实人际关系的珍惜                    │
└─────────────────────────────────────────────────────────────────────┘
""")

print("💡 运行命令:")
print("   python app.py workflow test_interview.txt")
print("   python app.py visualize")
print("   python app.py report --title '大学生AI使用研究'")
