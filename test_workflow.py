"""
CoderResearch 完整工作流测试
模拟运行编码流程以验证系统架构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ImportEngine.agent import ImportEngine
from CodeEngine.open_coding.agent import OpenCodingAgent
from CodeEngine.axial_coding.agent import AxialCodingAgent
from CodeEngine.selective_coding.agent import SelectiveCodingAgent
from CodeEngine.ir.code_ir import CodeUnit, CodeSource
from MemoEngine.agent import MemoEngine, MemoType
from ForumEngine.agent import ForumEngine

print("=" * 60)
print("🧪 CoderResearch 完整 SOP 测试")
print("=" * 60)

# ========== 步骤 1: 导入数据 ==========
print("\n📥 步骤 1: 导入数据")
print("-" * 40)

import_engine = ImportEngine()
segments = import_engine.import_file("test_interview.txt", segment_type="paragraph")

print(f"✓ 成功导入 {len(segments)} 个文本片段")
print(f"  - 来源: test_interview.txt")
print(f"  - 分段方式: 段落")

# 显示前3个片段
for i, seg in enumerate(segments[:3], 1):
    preview = seg.content[:80] + "..." if len(seg.content) > 80 else seg.content
    print(f"  [{i}] {preview}")

# ========== 步骤 2: 开放编码 ==========
print("\n🔍 步骤 2: 开放编码 (Open Coding)")
print("-" * 40)

open_agent = OpenCodingAgent()
open_agent.config.allow_ai_suggestion = True

# 模拟编码（实际应调用 LLM）
all_codes = []
for seg in segments[:10]:  # 测试前10个片段
    # 简化：创建模拟代码
    if "AI" in seg.content or "人工智能" in seg.content:
        code = CodeUnit(
            id=f"code_{len(all_codes):03d}",
            text_segment=seg,
            code_label="AI工具使用",
            code_definition="受访者描述使用AI工具的经历和方式",
            created_by=CodeSource.HUMAN,
            confidence=0.9
        )
        all_codes.append(code)
    elif "情感" in seg.content or "焦虑" in seg.content or "压力" in seg.content:
        code = CodeUnit(
            id=f"code_{len(all_codes):03d}",
            text_segment=seg,
            code_label="情绪体验",
            code_definition="受访者表达的负面情绪和压力感受",
            created_by=CodeSource.HUMAN,
            confidence=0.85
        )
        all_codes.append(code)
    elif "朋友" in seg.content or "人际" in seg.content or "社交" in seg.content:
        code = CodeUnit(
            id=f"code_{len(all_codes):03d}",
            text_segment=seg,
            code_label="人际支持",
            code_definition="关于朋友、人际关系的描述",
            created_by=CodeSource.HUMAN,
            confidence=0.88
        )
        all_codes.append(code)
    elif "安全" in seg.content or "树洞" in seg.content or "出口" in seg.content:
        code = CodeUnit(
            id=f"code_{len(all_codes):03d}",
            text_segment=seg,
            code_label="AI作为安全空间",
            code_definition="受访者将AI视为无评判的倾诉对象",
            created_by=CodeSource.HUMAN,
            confidence=0.92
        )
        all_codes.append(code)

print(f"✓ 生成 {len(all_codes)} 个初始代码")
for code in all_codes[:5]:
    print(f"  - [{code.code_label}] {code.code_definition[:40]}...")

# ========== 步骤 3: 轴心编码 ==========
print("\n🔄 步骤 3: 轴心编码 (Axial Coding)")
print("-" * 40)

axial_agent = AxialCodingAgent()

# 模拟归类
categories_data = [
    {
        "name": "功能性使用",
        "definition": "将AI视为工具性资源，用于任务完成",
        "codes": ["AI工具使用"],
        "properties": ["效率导向", "问题解决"],
        "dimensions": {"使用频率": "高频", "依赖程度": "高"}
    },
    {
        "name": "情感性使用", 
        "definition": "将AI用于情绪调节和情感支持",
        "codes": ["AI作为安全空间", "情绪体验"],
        "properties": ["情感宣泄", "安全感", "隐私保护"],
        "dimensions": {"情感深度": "浅层", "关系性质": "单向"}
    },
    {
        "name": "人机边界管理",
        "definition": "对AI和人际关系的功能区分与界限设定",
        "codes": ["人际支持"],
        "properties": ["功能分化", "选择性使用"],
        "dimensions": {"边界清晰度": "明确", "替代程度": "有限"}
    }
]

from CodeEngine.ir.code_ir import Category

categories = []
for cat_data in categories_data:
    cat = Category(
        id=f"cat_{len(categories):03d}",
        name=cat_data["name"],
        definition=cat_data["definition"],
        properties=cat_data["properties"],
        dimensions=cat_data["dimensions"]
    )
    categories.append(cat)

print(f"✓ 形成 {len(categories)} 个类属")
for cat in categories:
    print(f"  - [{cat.name}] {cat.definition}")
    print(f"    属性: {', '.join(cat.properties)}")

# ========== 步骤 4: 选择性编码 ==========
print("\n🎯 步骤 4: 选择性编码 (Selective Coding)")
print("-" * 40)

selective_agent = SelectiveCodingAgent()

# 识别核心类属
core_category = categories[1]  # "情感性使用"

print(f"✓ 核心类属: [{core_category.name}]")
print(f"  定义: {core_category.definition}")

# 构建故事线
storyline_title = "功能性分化的人机协同应对模式"
storyline_narrative = """
大学生在面对学业压力和情感困扰时，展现出一种"功能性分化"的应对策略：
他们将AI工具明确区分为"任务处理者"和"情绪容器"两个角色。
在功能性层面，AI被高效利用于学术任务、信息检索等认知性工作；
在情感层面，AI成为"安全的树洞"，提供24小时在线、无评判的情绪出口。
但这种关系是单向的、工具性的——受访者清晰地认识到AI无法提供
真实的人际连接和深度共情。因此，他们会在不同场景下策略性地
选择求助对象：具体问��找AI，深度支持找朋友。
这种"协同"模式既反映了对AI能力的理性认知，也体现了对
人际关系不可替代性的坚守。
"""

print(f"\n✓ 理论故事线: {storyline_title}")
print(f"  {storyline_narrative[:150]}...")

# 理论命题
propositions = [
    "大学生会根据任务性质（认知性vs情感性）选择求助对象，形成'功能性分化'的使用策略",
    "AI的'无评判性'和'随时可用性'使其成为情绪宣泄的安全空间，但这种关系是单向工具性的",
    "尽管AI提供了便利的情绪出口，受访者仍保有对人际支持不可替代性的清醒认知",
    "长期使用AI可能导致'认知外包'倾向，但也会反向增强对真实人际关系的珍惜"
]

print(f"\n✓ 生成 {len(propositions)} 个理论命题")
for i, prop in enumerate(propositions, 1):
    print(f"  {i}. {prop[:60]}...")

# ========== 步骤 5: 备忘录撰写 ==========
print("\n📝 步骤 5: 备忘录撰写")
print("-" * 40)

memo_engine = MemoEngine()

# 代码备忘录
for code in all_codes[:2]:
    memo = memo_engine.create_reflective_memo(
        stage=f"code_{code.code_label}",
        reflections=f"代码 '{code.code_label}' 在多个受访者文本中反复出现，"
                   f"表明这是大学生AI使用体验中的一个重要维度。"
    )
    print(f"✓ 创建备忘录: {memo.title}")

# 理论备忘录
theoretical_memo = memo_engine.create_reflective_memo(
    stage="core_theory",
    reflections="核心类属'情感性使用'揭示了AI在心理健康领域的潜在应用价值，"
               "但也暴露出人机关系的局限性。"
)
print(f"✓ 创建理论备忘录: {theoretical_memo.title}")

# ========== 步骤 6: 饱和度检查 ==========
print("\n📊 步骤 6: 饱和度检查")
print("-" * 40)

coverage = len(all_codes) / len(segments) if segments else 0
redundant = 0  # 简化计算

print(f"  - 编码覆盖率: {coverage:.1%}")
print(f"  - 初始代码数: {len(all_codes)}")
print(f"  - 类属数量: {len(categories)}")
print(f"  - 疑似冗余代码: {redundant}")
print(f"  - 饱和度等级: {'高' if coverage > 0.7 else '中' if coverage > 0.4 else '低'}")

# ========== 步骤 7: 协作讨论 ==========
print("\n💬 步骤 7: 编码讨论 (ForumEngine)")
print("-" * 40)

forum = ForumEngine()

# 模拟讨论
test_code = all_codes[0] if all_codes else None
if test_code:
    print(f"讨论主题: [{test_code.code_label}]")
    print(f"  研究者: 我对这段文本编码为 '{test_code.code_label}'")
    print(f"  Devil's Advocate: 为什么选择这个代码？还有其他可能的理解吗？")
    print(f"  AI助手: 建议检查与'AI工具依赖'的边界区分")

# ========== 总结 ==========
print("\n" + "=" * 60)
print("✅ 完整 SOP 测试完成!")
print("=" * 60)

print(f"""
📋 测试摘要:
  • 导入文本片段: {len(segments)} 个
  • 生成初始代码: {len(all_codes)} 个
  • 形成类属: {len(categories)} 个
  • 核心类属: {core_category.name if categories else 'N/A'}
  • 理论命题: {len(propositions)} 个
  • 备忘录: {len(memo_engine.memos)} 个

🎯 理论贡献:
  核心发现: {storyline_title}
  
📁 输出文件位置:
  - 原始数据: test_interview.txt
  - 代码数据库: coderresearch.db
  - 可视化图表: outputs/code_network.html
  - 研究报告: outputs/final_report.md
""")

print("\n💡 提示: 运行 'python app.py workflow test_interview.txt' 进行实际编码")
