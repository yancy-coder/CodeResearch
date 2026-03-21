"""
选择性编码（Selective Coding）模块
扎根理论第三阶段：识别核心类属，构建理论框架
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import uuid

from CodeEngine.ir.code_ir import Category
from utils.llm_client import llm_client


@dataclass
class SelectiveCodingConfig:
    """选择性编码配置"""
    min_saturation: float = 0.8  # 理论饱和度阈值


class StoryLine:
    """故事线"""
    def __init__(self, title: str, narrative: str, key_categories: List[str]):
        self.title = title
        self.narrative = narrative
        self.key_categories = key_categories


class SelectiveCodingAgent:
    """选择性编码 Agent"""
    
    def __init__(self, config: Optional[SelectiveCodingConfig] = None):
        self.config = config or SelectiveCodingConfig()
    
    def identify_core_category(self, categories: List[Category]) -> Optional[Category]:
        """识别核心类属"""
        
        categories_text = "\n".join([
            f"- {c.name}: {c.definition} (包含{len(c.codes)}个代码)"
            for c in categories
        ])
        
        prompt = f"""你正在进行扎根理论的选择性编码（Selective Coding）。

请从以下类属中识别核心类属（Core Category）：

{categories_text}

核心类属的标准：
1. 具有高度抽象性和解释力
2. 能与其他类属建立广泛联系
3. 贯穿整个研究过程
4. 能解释大部分数据变异

返回 JSON：
{{
    "core_category": "核心类属名称",
    "reasoning": "选择理由（100字以内）",
    "saturation_level": 0.85
}}
"""
        
        result = llm_client.generate_json(prompt)
        
        if "core_category" in result:
            core_name = result["core_category"]
            for cat in categories:
                if cat.name == core_name:
                    return cat
        
        # 默认返回第一个
        return categories[0] if categories else None
    
    def build_storyline(self, core_category: Category, categories: List[Category]) -> StoryLine:
        """构建故事线"""
        
        related_categories = [c for c in categories if c.id != core_category.id]
        
        categories_text = "\n".join([
            f"- {c.name}: {c.definition}"
            for c in related_categories
        ])
        
        prompt = f"""围绕核心类属 "{core_category.name}" 构建理论故事线。

核心类属定义：{core_category.definition}

相关类属：
{categories_text}

请构建一个连贯的叙事，解释：
1. 核心现象是什么
2. 产生的条件和脉络
3. 采取的策略和行动
4. 产生的结果

返回 JSON：
{{
    "title": "故事线标题",
    "narrative": "完整叙事（300-500字）",
    "key_categories": ["类属1", "类属2", "类属3"]
}}
"""
        
        result = llm_client.generate_json(prompt)
        
        return StoryLine(
            title=result.get("title", "理论故事线"),
            narrative=result.get("narrative", ""),
            key_categories=result.get("key_categories", [])
        )
    
    def check_saturation(self, codes: List, categories: List[Category]) -> Dict:
        """检查理论饱和度"""
        
        prompt = f"""评估当前编码的理论饱和度（Theoretical Saturation）：

统计信息：
- 开放编码数量：{len(codes)}
- 轴心类属数量：{len(categories)}

饱和度评估维度：
1. 新数据是否产生新代码？
2. 类属间关系是否已充分建立？
3. 核心类属是否能解释所有数据？
4. 是否存在明显的理论空白？

返回 JSON：
{{
    "saturation_score": 0.85,
    "is_saturated": true,
    "gaps": ["可能缺失的维度1", "可能缺失的维度2"],
    "recommendations": ["建议1", "建议2"]
}}
"""
        
        return llm_client.generate_json(prompt)
    
    def generate_theoretical_propositions(self, storyline: StoryLine, categories: List[Category]) -> List[str]:
        """生成理论命题"""
        
        categories_text = "\n".join([
            f"- {c.name}: {c.definition}"
            for c in categories
        ])
        
        prompt = f"""基于以下故事线和类属，生成理论命题（Theoretical Propositions）：

故事线：{storyline.title}
{storyline.narrative}

类属：
{categories_text}

要求：
1. 命题应具有抽象性和概括性
2. 明确变量间的关系（因果、条件、过程等）
3. 能指导未来研究或实践

返回 JSON：
{{
    "propositions": [
        "当...时，...会导致...",
        "...是...的核心条件",
        "...通过...机制影响..."
    ]
}}
"""
        
        result = llm_client.generate_json(prompt)
        return result.get("propositions", [])
