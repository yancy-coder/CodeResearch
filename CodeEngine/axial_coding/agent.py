"""
轴心编码（Axial Coding）模块
扎根理论第二阶段：归类、找关系、构建维度
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import uuid

from CodeEngine.ir.code_ir import CodeUnit, Category, Relationship
from utils.llm_client import llm_client


@dataclass
class AxialCodingConfig:
    """轴心编码配置"""
    min_codes_per_category: int = 2
    max_categories: int = 15
    auto_categorize: bool = True


class AxialCodingAgent:
    """轴心编码 Agent"""
    
    def __init__(self, config: Optional[AxialCodingConfig] = None):
        self.config = config or AxialCodingConfig()
    
    def categorize_codes(self, codes: List[CodeUnit]) -> List[Category]:
        """将代码归类到类属"""
        
        # 准备提示词
        codes_text = "\n".join([
            f"- {c.code_label}: {c.code_definition}" 
            for c in codes
        ])
        
        prompt = f"""你是一位质性研究专家，正在进行扎根理论的轴心编码（Axial Coding）。

请将以下开放编码归类为有意义的类属（Category）：

【代码列表】
{codes_text}

要求：
1. 每个类属包含 2-8 个相关代码
2. 为每个类属提供清晰名称和定义
3. 识别类属间的可能关系

返回 JSON 格式：
{{
    "categories": [
        {{
            "name": "类属名称",
            "definition": "类属定义（50字以内）",
            "code_labels": ["代码1", "代码2"],
            "properties": ["属性1", "属性2"],
            "dimensions": {{"维度名": "高低/强弱等"}}
        }}
    ],
    "relationships": [
        {{
            "source": "类属A",
            "target": "类属B", 
            "type": "因果/条件/过程/属性",
            "description": "关系描述"
        }}
    ]
}}
"""
        
        result = llm_client.generate_json(prompt)
        
        categories = []
        if "categories" in result:
            for cat_data in result["categories"]:
                category = Category(
                    id=str(uuid.uuid4())[:8],
                    name=cat_data["name"],
                    definition=cat_data["definition"],
                    codes=[c.id for c in codes if c.code_label in cat_data.get("code_labels", [])],
                    properties=cat_data.get("properties", []),
                    dimensions=cat_data.get("dimensions", {})
                )
                categories.append(category)
        
        return categories
    
    def analyze_paradigm(self, category: Category, codes: List[CodeUnit]) -> Dict:
        """分析典范模型（因果条件-现象-脉络-中介条件-行动策略-结果）"""
        
        codes_text = "\n".join([
            f"- {c.code_label}: {c.code_definition}"
            for c in codes if c.id in category.codes
        ])
        
        prompt = f"""分析以下类属的典范模型（Paradigm Model）：

类属：{category.name}
定义：{category.definition}
包含代码：
{codes_text}

请识别：
1. 因果条件（Causal Conditions）
2. 现象（Phenomenon）
3. 脉络（Context）
4. 中介条件（Intervening Conditions）
5. 行动/互动策略（Action/Interaction Strategies）
6. 结果（Consequences）

返回 JSON：
{{
    "causal_conditions": ["条件1", "条件2"],
    "phenomenon": "核心现象描述",
    "context": "脉络描述",
    "intervening_conditions": ["中介1", "中介2"],
    "strategies": ["策略1", "策略2"],
    "consequences": ["结果1", "结果2"]
}}
"""
        
        return llm_client.generate_json(prompt)
    
    def find_relationships(self, categories: List[Category]) -> List[Relationship]:
        """找出类属间关系"""
        
        categories_text = "\n".join([
            f"- {c.name}: {c.definition}"
            for c in categories
        ])
        
        prompt = f"""分析以下类属间的关系：

{categories_text}

识别关系类型：因果（causes）、条件（conditions）、过程（processes）、
属性（attributes）、策略（strategies）、结果（consequences）

返回 JSON：
{{
    "relationships": [
        {{
            "source": "类属A名称",
            "target": "类属B名称",
            "type": "因果/条件/过程/属性/策略/结果",
            "description": "具体关系描述"
        }}
    ]
}}
"""
        
        result = llm_client.generate_json(prompt)
        relationships = []
        
        if "relationships" in result:
            for rel_data in result["relationships"]:
                rel = Relationship(
                    id=str(uuid.uuid4())[:8],
                    source_id=rel_data["source"],
                    target_id=rel_data["target"],
                    relation_type=rel_data["type"],
                    description=rel_data.get("description", "")
                )
                relationships.append(rel)
        
        return relationships
    
    def build_coding_matrix(self, codes: List[CodeUnit], categories: List[Category]) -> Dict:
        """构建编码矩阵（类属 × 维度）"""
        matrix = {}
        
        for category in categories:
            matrix[category.name] = {
                "definition": category.definition,
                "codes": [],
                "properties": category.properties,
                "dimensions": category.dimensions
            }
            
            for code in codes:
                if code.id in category.codes:
                    matrix[category.name]["codes"].append({
                        "label": code.code_label,
                        "definition": code.code_definition
                    })
        
        return matrix
